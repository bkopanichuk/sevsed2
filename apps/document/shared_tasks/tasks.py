from __future__ import absolute_import, unicode_literals
import glob
import logging
import os

from preview_generator.manager import PreviewManager
from preview_generator.preview.generic_preview import UnavailablePreviewType
from celery import shared_task

from apps.document.models.document_model import get_upload_document_path, get_preview_directory, BaseDocument, \
    MainFileVersion
from apps.document.models.textract_model import DocumentGeneratedText
from config.settings import MEDIA_ROOT
import textract as tx

logger = logging.getLogger("debug")
UPDATED_FIELDS = ['preview_pdf', 'preview']


@shared_task
def generate_text(doc_id):
    doc = BaseDocument.objects.get(unique_uuid=doc_id)
    upload_document_path = get_upload_document_path(doc, os.path.basename(doc.main_file.name))
    full_path = os.path.join(MEDIA_ROOT, upload_document_path)
    text = tx.process(full_path, language='ukr')
    DocumentGeneratedText.objects.create(document=doc, text=text.decode())



@shared_task
def create_preview(doc_id):
    document = BaseDocument.objects.get(unique_uuid=doc_id)
    upload_document_path = get_upload_document_path(document,
                                                    os.path.basename(document.main_file.name))
    upload_cache_path = get_preview_directory(document, os.path.basename(document.main_file.name))
    full_path = os.path.join(MEDIA_ROOT, upload_document_path)
    full_cache_path = os.path.join(MEDIA_ROOT, upload_cache_path)
    cache_path = os.path.dirname(full_cache_path)

    manager = PreviewManager(cache_path, create_folder=True)
    try:
        path_to_preview_image = manager.get_jpeg_preview(full_path, width=1920, height=1080)
    except UnavailablePreviewType:
        logger.warning("UnavailablePreviewType: Preview was not created")
    else:
        preview_dir_path = os.path.dirname(path_to_preview_image)
        preview_base_name = os.path.basename(path_to_preview_image)
        document.preview.name = os.path.join(upload_cache_path, os.path.basename(path_to_preview_image))

        if document.main_file.name.endswith('.pdf'):
            document.preview_pdf.name = upload_document_path
            return

        os.chdir(preview_dir_path)
        for file in glob.glob(preview_base_name.replace('-1920x1080.jpeg', '') + "*.pdf"):
            document.preview_pdf.name = os.path.join(upload_cache_path, os.path.basename(file))
            return
