import logging

from django.conf import settings
from django.utils.timezone import localdate

from apps.document.models.document_constants import OUTGOING, INCOMING, INNER
from apps.document.models.document_model import BaseDocument, ON_REGISTRATION, AUTOMATIC_REG, REGISTERED, SEV
from apps.document.models.sign_model import Sign
from apps.document.services import CreateFlow
from apps.l_core.exceptions import ServiceException
from apps.sevovvintegration.services.on_registered_service import ProcessRegisteredDocument
from ..add_qrcode_and_sing_info import AddQRCode2PDF

logger = logging.getLogger(__name__)
SITE_URL = settings.SITE_URL


class RegisterDocument:
    """Зареєструвати документ """

    def __init__(self, doc):
        self.document: BaseDocument = doc

    def run(self):
        self.set_reg_number()
        self.validate_document_reg_number()
        self.validate_document_status()
        self.validate_main_file()
        self.register_document()
        self.create_flow()
        self.send_registered_status()
        return self.document

    def create_flow(self):
        """Автоматично створити потік виконання завдань, якщо реєструється вхідний документ
        :return:
        """
        if self.document.document_cast == INCOMING:
            service = CreateFlow(doc=self.document)
            service.run()

    def send_registered_status(self):
        """Відправити в шину обміну інформацю про успішну реєстрацію документа. Застосовується, тільки у випадку надходження документа з шини обміну."""
        if self.document.source == SEV:
            process_registered = ProcessRegisteredDocument(self.document)
            process_registered.run()

    def validate_document_status(self):
        if self.document.status != ON_REGISTRATION:
            raise ServiceException(f'Заборонена повторна реєстрація документа.')

    def set_reg_number(self):
        """Автоматично присвоїти реєстраційний номер, якщо обрано автоматичну реєстрацію документа,
        а також вказано журнал реєстрації
        :return:
        """
        if self.document.registration_type == AUTOMATIC_REG and self.document.registration:
            registration_journal = self.document.registration
            reg_number = registration_journal.get_next_register_number(self.document)
            self.document.reg_number = reg_number

    def validate_document_reg_number(self):
        if not self.document.reg_number:
            raise ServiceException(f'Заборонена реєстрація документа без номера.')

    def validate_main_file(self):
        if not self.document.main_file:
            raise ServiceException(f'Заборонена реєстрація  документа без завантаженого документа.')

    def register_document(self):
        if self.document.document_cast == OUTGOING:
            self.register_outgoing_document()
        elif self.document.document_cast == INCOMING:
            self.register_incoming_document()
        elif self.document.document_cast == INNER:
            self.register_inner_document()
        else:
            raise ServiceException('document_cast is not set')
        self.set_qrcode()

    def get_signers4qrcode(self):
        reg_date = f'Номер: {self.document.reg_number}\nЗареєстрований: {self.document.reg_date}\n'
        res = reg_date + "ЕЦП:\n"
        sign_objects = Sign.objects.filter(document=self.document)
        for sign in sign_objects:
            f_string = sign.get_signer_info_text()
            res += f_string
        return res

    def get_detail_url4qrcode(self):
        data = f'{SITE_URL}/api/document_details/{self.document.unique_uuid}/'
        return data

    def get_main_signer_data(self):
        sign_objects = Sign.objects.filter(document=self.document)
        logger.error(sign_objects)
        data = []
        for sign in sign_objects:
            data.append(sign.get_signer_info())
        return data

    def set_qrcode(self):
        data = self.get_signers4qrcode()
        signers_data = self.get_main_signer_data()
        logger.error(signers_data)
        qr_service = AddQRCode2PDF(self.document.preview_pdf.path, data, signers_data=signers_data)
        qr_service.run()

    def register_incoming_document(self):
        self.document.status = REGISTERED
        self.document.reg_date = localdate()
        self.document.save(update_fields=['status', 'reg_date', 'reg_number'])

    def register_outgoing_document(self):
        self.document.status = REGISTERED
        self.document.reg_date = localdate()
        self.document.save(update_fields=['status', 'reg_date', 'reg_number'])

    def register_inner_document(self):
        self.document.status = REGISTERED
        self.document.reg_date = localdate()
        self.document.save(update_fields=['status', 'reg_date', 'reg_number'])
