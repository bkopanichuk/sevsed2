import uuid
from apps.document.models.document_model import BaseDocument
from apps.document.models.sign_model import Sign
from .client import SEVUploadClient,CompanyInfo
from .document2xml1207converter import Document2Xml1207Converter
from ..models import SEVOutgoing


class CreateSevOutgoing():

    def __init__(self,document:BaseDocument):
        self.document = document

    def run(self):
        self.send_to_all()

    def send_to_all(self):
        sign = self.get_sign(self.document)
        for addressee in self.document.mailing_list.all():
            message_id = uuid.uuid4().__str__().upper()
            SEVOutgoing.objects.create(document = self.document,
                                       from_org = self.document.organization,
                                       message_id = message_id,
                                       to_org = addressee,
                                       sign=sign)

    def get_sign(self,document):
        sign = Sign.objects.filter(document=document,signer = document.main_signer).first()
        return sign







class SendToSEVOVVProcess():
    def __init__(self, outgoing_doc: SEVOutgoing):
        self.outgoing_doc: SEVOutgoing = outgoing_doc
        self.client = SEVUploadClient()

    def run(self):
        self.send_message()

    def format_company(self,org):
        return CompanyInfo(org.id ,org.edrpou, org.system_id, org.system_password)

    def send_message(self):
        conv = Document2Xml1207Converter(self.outgoing_doc.document,
                                         self.outgoing_doc.message_id,
                                         self.outgoing_doc.to_org,
                                         sign=self.outgoing_doc.sign.sign)
        xml_path, outgoing_path = conv.save_xml()
        result = self.client.send_document(xml_path, producer=self.format_company(self.outgoing_doc.from_org),
                                           consumer=self.format_company(self.outgoing_doc.to_org), message_id=self.outgoing_doc.message_id)
        self.outgoing_doc.xml_file.name = outgoing_path
        self.outgoing_doc.sending_result = result
        self.outgoing_doc.save()
