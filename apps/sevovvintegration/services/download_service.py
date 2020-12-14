import base64
import os

import declxml as xml
from django.conf import settings
from django.utils.timezone import now

from apps.document.models.document_model import BaseDocument, SEV, ON_REGISTRATION
from apps.document.models.sign_model import Sign
from apps.l_core.models import CoreOrganization
from apps.l_core.ua_sign import verify_external
from apps.sevovvintegration import tasks
from apps.sevovvintegration.constants import HeaderMsgType
from apps.sevovvintegration.serializers.base_header import HeaderXML1207Serializer
from apps.sevovvintegration.serializers.document_1207_serializer import DocumentXML1207Serializer
from apps.sevovvintegration.serializers.acknowledgement_1207_serialiser import AcknowledgementXML1207Serializer
from .client import SEVDownloadClient, CompanyInfo
from .sender_service import SendAct2SEVOVVProcess
from ..constants import AcknowledgementAckType, ErrorCodes
from ..models import SEVIncoming,SEVOutgoing
from ...document.models.document_constants import INCOMING
from ...document.models.document_model import DELIVERED,get_upload_document_path
from shutil import copyfile,copy2


MEDIA_ROOT = settings.MEDIA_ROOT
import logging

logger = logging.getLogger(__name__)


def get_incoming_path(document, message_id):
    _now = now()
    return os.path.join(
        f'sevovv_integration/org_{document.organization.id}/incoming/{_now.year}/{_now.month}/{_now.day}/{message_id}')


class DownloadMessages():
    def run(self):
        res = self.load_messages()
        return res

    def get_consumers(self):
        return CoreOrganization.objects.filter(sev_connected=True)

    def process_xml_list(self, path_list):
        for path in path_list:
            tasks.process_xml(path)

    def load_messages(self):
        logger.info('load_messages')
        res = []
        download_client = SEVDownloadClient()
        for _consumer in self.get_consumers():
            consumer = CompanyInfo(_consumer.id, _consumer.edrpou, _consumer.system_id, _consumer.system_password)
            xml_path_list = download_client.download_messages(consumer)
            res.append([str(_consumer), xml_path_list])
            self.process_xml_list(xml_path_list)
        return res


class ProcessXml():
    def __init__(self,path):
        self.path=path

    def get_incoming_message_type(self):
        data = xml.parse_from_file(HeaderXML1207Serializer, self.path)
        message_type = data.get('msg_type')
        return int(message_type)


    def run(self):
        message_type = self.get_incoming_message_type()
        if message_type in [HeaderMsgType.DOCUMENT, HeaderMsgType.DOCUMENT_REPLAY]:
            self.serialiser = DocumentXML1207Serializer
        if message_type == HeaderMsgType.MESSAGE:
            self.serialiser = AcknowledgementXML1207Serializer
        self.create_incoming_document()

    def create_incoming_document(self):
        data = xml.parse_from_file(self.serialiser, self.path)
        from_sys_id = data.get('from_sys_id')
        from_org = CoreOrganization.objects.get(system_id=from_sys_id)
        to_sys_id = data.get('to_sys_id')
        msg_id = data.get('msg_id')
        to_org = CoreOrganization.objects.get(system_id=to_sys_id)
        xml_relative_path = self.path.replace(MEDIA_ROOT + '/', '')
        incoming = SEVIncoming(from_org=from_org, to_org=to_org, message_id=msg_id)
        incoming.xml_file.name = xml_relative_path
        incoming.save()
        service = ProcessIncoming(incoming_message=incoming)
        service.run()

class ProcessIncoming():
    def __init__(self, incoming_message: SEVIncoming):
        self.incoming_message = incoming_message

    def run(self):
        message_type = self.get_incoming_message_type()
        if message_type in [HeaderMsgType.DOCUMENT, HeaderMsgType.DOCUMENT_REPLAY]:
            self.process_incoming_document()
        if message_type == HeaderMsgType.MESSAGE:
            self.process_incoming_message()

    def process_incoming_document(self):
        ## спочатку повідомляємо що документ завантажено
        self.send_receipt_delivered()
        document, data = self.create_incoming_document()
        self.save_sign(document, data)
        ## повідомляємо що документ опрацьовані і відправлено на реєстрацію
        self.send_receipt_accepted(document)
        self.incoming_message.document = document
        self.incoming_message.save()

    def get_incoming_message_type(self):
        data = xml.parse_from_file(HeaderXML1207Serializer, self.incoming_message.xml_file.path)
        message_type = data.get('msg_type')
        return int(message_type)

    def process_incoming_message(self):
        data = xml.parse_from_file(AcknowledgementXML1207Serializer, self.incoming_message.xml_file.path)
        message_data = data.get('Acknowledgement')
        logger.warning(message_data)
        ##
        message_id = message_data.get('msg_id')
        sev_outgoing_doc = SEVOutgoing.objects.get(message_id = message_id)
        sev_outgoing_doc.document.status =DELIVERED
        sev_outgoing_doc.document.save()

    def create_incoming_document(self):
        data = xml.parse_from_file(DocumentXML1207Serializer, self.incoming_message.xml_file.path)
        document_data = data.get('Document')
        document = BaseDocument(document_cast=INCOMING)
        print('DOCUMENT: ', document)
        document.comment = document_data.get('annotation')
        print(document.comment)
        document.outgoing_number = document_data.get('RegNumber').get('.')
        print(document.outgoing_number)
        document.outgoing_date = document_data.get('RegNumber').get('regdate')
        print(document.outgoing_date)
        document.correspondent = self.incoming_message.from_org
        document.organization = self.incoming_message.to_org  ## Власник листа, організація на яку прийшло повідомлення
        document.main_file.name = self.save_incoming_document_file(data, document)
        document.status = ON_REGISTRATION
        document.source = SEV
        document.save()
        return document, data

    def save_sign(self, document, data):
        sign_data = data.get('Expansion').get('StaticExpansion').get('SignInfo').get('SignData').get('.')
        sign = Sign(document=document)
        sign.sign = sign_data
        sign.sign_info = verify_external(data_path=document.main_file.path, sign_data=sign_data)

    def save_incoming_document_file(self, data, document):
        row_data = data.get('Document').get('DocTransfer')
        message_id = data.get('msg_id')
        b_64_data = row_data.get('.')
        b_data = base64.b64decode(b_64_data)
        file_name = row_data.get('description')
        relative_path_dir = get_incoming_path(document, message_id)
        absolute_path_dir = os.path.join(MEDIA_ROOT, relative_path_dir)
        absolute_path_file = os.path.join(absolute_path_dir, file_name)
        relative_path = os.path.join(relative_path_dir, file_name)
        if not os.path.exists(absolute_path_dir):
            os.makedirs(absolute_path_dir)
        with open(absolute_path_file, 'wb') as file:
            file.write(b_data)
        ##Переміщаємо документ в стандартну директорію для документів
        _document_relative_path = get_upload_document_path(document,file_name)
        _document_absolute_path = os.path.join(MEDIA_ROOT,_document_relative_path)
        _document_absolute_dir = os.path.dirname(_document_absolute_path)
        if not os.path.exists(_document_absolute_dir):
            os.makedirs(_document_absolute_dir)

        try:
            copy2(absolute_path_file, _document_absolute_path)
        except:
            pass
        ##os.rename(absolute_path_file, _document_absolute_path)
        return _document_relative_path

    def send_receipt_delivered(self):
        """ Відправляє повідомлення про успішне завантаження документа з шини обміну"""
        send_ack_process = SendAct2SEVOVVProcess(self.incoming_message, AcknowledgementAckType.DELIVERED,
                                                 ErrorCodes.SUCCESS)
        send_ack_process.run()

    def send_receipt_accepted(self, document):
        """ Відправляє повідомлення про успішне створення  документа на основі завантаженого з шини обміну"""
        send_ack_process = SendAct2SEVOVVProcess(self.incoming_message, AcknowledgementAckType.ACCEPTED,
                                                 ErrorCodes.SUCCESS)
        send_ack_process.run()
