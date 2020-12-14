from django.conf import settings

from apps.document.models.document_model import BaseDocument
from .sender_service import SendAct2SEVOVVProcess
from ..constants import AcknowledgementAckType, ErrorCodes
from ..models import SEVIncoming



MEDIA_ROOT = settings.MEDIA_ROOT
import logging

logger = logging.getLogger(__name__)


class ProcessRegisteredDocument():
    def __init__(self, document:BaseDocument):
        self.document = document
        self.incoming_message = SEVIncoming.objects.get(document=document)

    def run(self):
        self.send_receipt_registered()


    def send_receipt_registered(self):
        """ Відправляє повідомлення на шину обміну, про успішну реєстрацію документа."""
        send_ack_process = SendAct2SEVOVVProcess(self.incoming_message, AcknowledgementAckType.REGISTERED,
                                                 ErrorCodes.SUCCESS)
        send_ack_process.run()

