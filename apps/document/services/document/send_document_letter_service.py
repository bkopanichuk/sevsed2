from apps.document.models.document_model import LETTER,TRANSFERRED,REGISTERED_LETTER,HAND_OUT
from apps.l_core.exceptions import ServiceException


class SendDocumentLetter:
    """ Відправити документ звичайним листом (поштою)"""
    VALID_SEND_METHODS = [REGISTERED_LETTER,LETTER,HAND_OUT]
    def __init__(self, doc, data):
        self.document = doc
        self.mailing_method = data.get('mailing_method')

    def run(self):
        self.validate_send_method()
        self.validate_mailing_list()
        self.change_document_status()
        return self.document

    def validate_send_method(self):
        if self.mailing_method not in self.VALID_SEND_METHODS:
            raise ServiceException(
                f'Метод відправки "{self.mailing_method}" -  не дозволений для даного способу відправки.')


    def validate_mailing_list(self):
        addressees = self.document.mailing_list.all()
        if not addressees.exists():
            raise ServiceException(f'Ви не можете відправити документ без вказаних адресатів. Спочатку вкажіть адресатів.')



    def change_document_status(self):
        self.document.mailing_method=self.mailing_method
        self.document.status = TRANSFERRED
        self.document.save()

