import uuid

from apps.document.models.document_model import BaseDocument
from apps.document.models.sign_model import Sign
from .client import SEVUploadClient, CompanyInfo
from .document2xml1207converter import Document2Xml1207Converter
from .ackonowlage_document_factory import Acknowlage2Xml1207Factory
from ..models import SEVOutgoing, SEVIncoming
import logging

logger = logging.getLogger(__name__)


def get_sign(document):
    sign = Sign.objects.filter(document=document, signer=document.main_signer).first()
    return sign


class CreateSevOutgoing():

    def __init__(self, document: BaseDocument):
        self.document = document

    def run(self):
        self.send_to_all()

    def send_to_all(self):
        sign = get_sign(self.document)
        for addressee in self.document.mailing_list.all():
            message_id = uuid.uuid4().__str__().upper()
            SEVOutgoing.objects.create(document=self.document,
                                       from_org=self.document.organization,
                                       message_id=message_id,
                                       to_org=addressee,
                                       sign=sign)


class SendToSEVOVVProcess():
    def __init__(self, outgoing_doc: SEVOutgoing):
        self.outgoing_doc: SEVOutgoing = outgoing_doc
        self.client = SEVUploadClient()

    def run(self):
        self.send_message()

    def format_company(self, org):
        return CompanyInfo(org.id, org.edrpou, org.system_id, org.system_password)

    def send_message(self):
        conv = Document2Xml1207Converter(self.outgoing_doc.document,
                                         self.outgoing_doc.message_id,
                                         self.outgoing_doc.to_org,
                                         sign=self.outgoing_doc.sign.sign)
        xml_path, outgoing_path = conv.save_xml()
        logger.info(f'xml_path:{xml_path}')
        logger.info(f'outgoing_path:{outgoing_path}')
        self.outgoing_doc.xml_file.name = outgoing_path
        self.outgoing_doc.save()
        result = self.client.send_document(xml_path, producer=self.format_company(self.outgoing_doc.from_org),
                                           consumer=self.format_company(self.outgoing_doc.to_org),
                                           message_id=self.outgoing_doc.message_id)
        self.outgoing_doc.sending_result = result
        self.outgoing_doc.save()


class SendAct2SEVOVVProcess():
    def __init__(self, incoming_message, act_type, error_code):
        logger.info(f'PARAMS: incoming_message:{incoming_message}, act_type:{act_type},error_code:{error_code}')
        self.incoming_message: SEVIncoming = incoming_message
        self.act_type = act_type
        self.error_code = error_code
        self.client = SEVUploadClient()

    def run(self):
        self.send_message()

    def format_company(self, org):
        return CompanyInfo(org.id, org.edrpou, org.system_id, org.system_password)

    def send_message(self):
        message_id = uuid.uuid4().__str__().upper()
        document_message_id = self.incoming_message.message_id
        producer = self.incoming_message.to_org
        consumer = self.incoming_message.from_org
        ak_f = Acknowlage2Xml1207Factory(document_message_id, message_id, consumer, producer, self.act_type,
                                         self.error_code)
        xml_path, outgoing_path = ak_f.create_xml_and_get_path()
        result = self.client.send_document(xml_path, producer=self.format_company(producer),
                                           consumer=self.format_company(consumer),
                                           message_id=message_id)
        self.save_sevovv_message(message_id, producer, consumer, outgoing_path)

        return result

    def save_sevovv_message(self, message_id, producer, consumer, outgoing_path):
        SEVOutgoing.objects.create(from_org=consumer, to_org=producer, xml_file=outgoing_path, message_id=message_id)
