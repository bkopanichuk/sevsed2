import logging
import os
import glob
from ..models.document_model import MainFileVersion
from apps.document.tasks import generate_text
from preview_generator.manager import PreviewManager

from apps.document.models.document_model import get_upload_document_path, get_preview_directory
from config.settings import MEDIA_ROOT

logger = logging.getLogger("debug")

UPDATED_FIELDS = ['preview_pdf', 'preview']



class GenerateText:
    def __init__(self, doc):
        self.document = doc

    def run(self):
        generate_text.delay(self.document.unique_uuid)


class CreatePreview:
    def __init__(self, doc, update_fields):
        self.document = doc
        self.update_fields = update_fields

    def run(self):
        if self.update_fields:
            if list(self.update_fields)[0] in UPDATED_FIELDS:
                return
                ##raise Exception(self.update_fields)
        self.create_preview()
        self.document.save(update_fields=UPDATED_FIELDS)

    def create_preview(self):
        upload_document_path = get_upload_document_path(self.document, os.path.basename(self.document.main_file.name))
        upload_cache_path = get_preview_directory(self.document, os.path.basename(self.document.main_file.name))
        if self.document.main_file.name.endswith('.pdf'):
            self.document.preview_pdf.name = upload_document_path
            return
        full_path = os.path.join(MEDIA_ROOT, upload_document_path)
        full_cache_path = os.path.join(MEDIA_ROOT, upload_cache_path)
        cache_path = os.path.dirname(full_cache_path)

        manager = PreviewManager(cache_path, create_folder=True)
        path_to_preview_image = manager.get_jpeg_preview(full_path, width=600, height=800)
        preview_dir_path = os.path.dirname(path_to_preview_image)
        preview_base_name = os.path.basename(path_to_preview_image)
        self.document.preview.name = os.path.join(upload_cache_path, os.path.basename(path_to_preview_image))

        if self.document.main_file.name.endswith('.pdf'):
            self.document.preview_pdf.name = upload_document_path
            return

        os.chdir(preview_dir_path)
        for file in glob.glob(preview_base_name.replace('-600x800.jpeg', '') + "*.pdf"):
            self.document.preview_pdf.name = os.path.join(upload_cache_path, os.path.basename(file))
            return


class UpdateMainFileVersion:
    def __init__(self, doc):
        self.document = doc

    def run(self):
        if not self.check_if_file_exists():
            return
        if self.check_duplicates():
            return
        self.update_main_file_version()

    def check_if_file_exists(self):
        return self.document.main_file.name

    def check_duplicates(self):
        q = MainFileVersion.objects.filter(document=self.document)
        if not q.exists():
            return False
        if q.latest('add_date').main_file.name == self.document.main_file.name:
            return True
        return False

    def update_main_file_version(self):
        if self.document.main_file:
            new_version = MainFileVersion()
            new_version.document = self.document
            new_version.main_file.name = self.document.main_file.name
            new_version.save()
