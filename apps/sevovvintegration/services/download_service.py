import base64
import os

import declxml as xml
from apps.sevovvintegration import tasks

from django.conf import settings
from django.utils.timezone import now

from apps.document.models.document_model import BaseDocument, SEV, ON_REGISTRATION
from apps.document.models.sign_model import Sign
from apps.l_core.models import CoreOrganization
from apps.l_core.ua_sign import verify_external
from .client import SEVDownloadClient, CompanyInfo
from ..models import SEVIncoming
from ..serializers import DocumentXML1207Serializer
from ...document.models.document_constants import INCOMING


MEDIA_ROOT = settings.MEDIA_ROOT
import logging

logger = logging.getLogger(__name__)

def get_incoming_path(document, message_id):
    _now = now()
    return os.path.join(
        f'sevovv_integration/organization_{document.organization.id}/incoming/{_now.year}/{_now.month}/{_now.day}/{message_id}')


class DownloadMessages():
    def run(self):
        res = self.load_messages()
        return res

    def get_consumers(self):
        ## TODO Замінити на явний фільтр
        return CoreOrganization.objects.exclude(system_password='')

    tasks

    # def process_xml(self, path):
    #     try:
    #         data = xml.parse_from_file(DocumentXML1207Serializer, path)
    #         from_sys_id = data.get('from_sys_id')
    #         from_org = CoreOrganization.objects.get(system_id=from_sys_id)
    #         to_sys_id = data.get('to_sys_id')
    #         to_org = CoreOrganization.objects.get(system_id=to_sys_id)
    #         xml_relative_path = path.replace(MEDIA_ROOT + '/', '')
    #         incoming = SEVIncoming(from_org=from_org, to_org=to_org)
    #         incoming.xml_file.name = xml_relative_path
    #         incoming.save()
    #         service = ProcessIncoming(incoming_message=incoming)
    #         service.run()
    #     except Exception as e:
    #         logger.error(e)

    def process_xml_list(self, path_list):
        for path in path_list:
            tasks.process_xml(path)

    def load_messages(self):
        res = []
        download_client = SEVDownloadClient()
        for _consumer in self.get_consumers():
            consumer = CompanyInfo(_consumer.id, _consumer.edrpou, _consumer.system_id, _consumer.system_password)
            xml_path_list = download_client.download_messages(consumer)
            res.append([str(_consumer), xml_path_list])
            self.process_xml_list(xml_path_list)
        return res


class ProcessIncoming():
    def __init__(self, incoming_message: SEVIncoming):
        self.incoming_message = incoming_message

    def run(self):
        document, data = self.create_incoming_message()
        self.save_sign(document, data)

    def create_incoming_message(self):
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
        return relative_path
