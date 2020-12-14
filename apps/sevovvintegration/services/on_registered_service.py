import base64
import os

import declxml as xml
from django.conf import settings

from apps.document.models.document_model import BaseDocument, SEV, ON_REGISTRATION
from apps.document.models.sign_model import Sign
from apps.l_core.ua_sign import verify_external
from apps.sevovvintegration.serializers.document_1207_serializer import DocumentXML1207Serializer
from .sender_service import SendAct2SEVOVVProcess
from ..constants import AcknowledgementAckType, ErrorCodes
from ..models import SEVIncoming
from ...document.models.document_constants import INCOMING

MEDIA_ROOT = settings.MEDIA_ROOT
import logging

logger = logging.getLogger(__name__)


class ProcessRegisteredDocument():
    def __init__(self, incoming_message: SEVIncoming):
        self.incoming_message = incoming_message

    def run(self):
        ## спочатку повідомляємо що документ завантажено
        self.send_receipt_registered()


    def send_receipt_registered(self):
        """ Відправляє повідомлення про успішне завантаження документа з шини обміну"""
        send_ack_process = SendAct2SEVOVVProcess(self.incoming_message, AcknowledgementAckType.DELIVERED,
                                                 ErrorCodes.SUCCESS)
        send_ack_process.run()

