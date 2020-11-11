import logging

from ..models.document_model import MainFileVersion
from ..shared_tasks.tasks import generate_text, create_preview

logger = logging.getLogger("debug")

UPDATED_FIELDS = ['preview_pdf', 'preview']



class GenerateText:
    def __init__(self, doc):
        self.document = doc

    def run(self):
        generate_text.delay(self.document.unique_uuid)


class CreatePreview:
    """Створити файл для попередного перегляду"""

    def __init__(self, doc, update_fields):
        self.document = doc
        self.update_fields = update_fields

    def run(self):
        if self.update_fields:
            if list(self.update_fields)[0] in UPDATED_FIELDS:
                return
                ##raise Exception(self.update_fields)
        create_preview.delay(self.document.unique_uuid)
        self.document.save(update_fields=UPDATED_FIELDS)


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
