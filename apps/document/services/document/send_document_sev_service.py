""" викор истовується для відправки вокументів  документ через СЕВ ОВВ
"""
from apps.document.models.document_model import TRANSFERRED,SEV
from apps.l_core.exceptions import ServiceException
from apps.sevovvintegration.services.sender_service import CreateSevOutgoing




class SendDocumentLetter:
    """ Відправити документ через СЕВ ОВВ"""
    VALID_SEND_METHODS = [SEV]
    def __init__(self, doc, data):
        self.document = doc
        self.mailing_method = data.get('mailing_method')

    def run(self):
        self.validate_sender()
        self.validate_send_method()
        self.validate_mailing_list()
        self.sand_document()
        self.change_document_status()
        return self.document

    def validate_sender(self):
        if not self.document.organization.system_id:
            raise ServiceException(
                f'Організація-відправник не має ідентифікатора для відкравки через СЕВОВВ')


    def validate_send_method(self):
        if self.mailing_method not in self.VALID_SEND_METHODS:
            raise ServiceException(
                f'Метод відправки "{self.mailing_method}" -  не дозволений для даного способу відправки.')


    def validate_mailing_list(self):
        addressees = self.document.mailing_list.all()
        if not addressees.exists():
            raise ServiceException(f'Ви не можете відправити документ без вказаних адресатів. Спочатку вкажіть адресатів.')

    def sand_document(self):
        sev_outgoing = CreateSevOutgoing(document=self.document)
        sev_outgoing.run()

    def change_document_status(self):
        self.document.mailing_method=self.mailing_method
        self.document.status = TRANSFERRED
        self.document.save()

