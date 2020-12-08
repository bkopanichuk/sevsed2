from __future__ import absolute_import, unicode_literals

import logging
import os

from celery import shared_task

from apps.document.models.document_model import get_upload_document_path, BaseDocument
from apps.document.models.textract_model import DocumentGeneratedText
from config.settings import MEDIA_ROOT
import textract as tx
#import apps.document.services.document_service  as document_service
logger = logging.getLogger("debug")
UPDATED_FIELDS = ['preview_pdf', 'preview']


@shared_task
def generate_text(doc_id) -> None:
    """Запускає завдання для створення індексу повнотекстового пошуку

    :param doc_id: Первинний ключ документа
    :return: None
    """
    doc = BaseDocument.objects.get(unique_uuid=doc_id)
    upload_document_path = get_upload_document_path(doc, os.path.basename(doc.main_file.name))
    full_path = os.path.join(MEDIA_ROOT, upload_document_path)
    text = tx.process(full_path, language='ukr')
    DocumentGeneratedText.objects.create(document=doc, text=text.decode())

# @shared_task
# def create_preview(doc_id,update_fields):
#     doc = BaseDocument.objects.get(pk=doc_id)
#     service = document_service.CreatePreview(doc=doc,update_fields=update_fields)
#     service.run()


