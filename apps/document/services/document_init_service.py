import logging
import os

from django.utils.timezone import now

from apps.document.models.document_model import BaseDocument, get_preview_directory, get_upload_document_path
from apps.document.models.task_model import RUNNING, REVIEW, RESULT, MAIN, Task
from config.settings import MEDIA_ROOT
from preview_generator.manager import PreviewManager

logger = logging.getLogger("debug")

class CreatePreview:
    def __init__(self, doc):
        self.document = doc

    def run(self):
        old_path = self.document.main_file.name
        if not self.document.preview or old_path != self.document.main_file.name:
            self.create_preview()
            self.document.save()

    def create_preview(self):
        upload_path = get_upload_document_path(self.document, os.path.basename(self.document.main_file.name))
        upload_cache_path = get_preview_directory(self.document, os.path.basename(self.document.main_file.name))
        full_path = os.path.join(MEDIA_ROOT, upload_path)
        full_cache_path = os.path.join(MEDIA_ROOT, upload_cache_path)
        cache_path = os.path.dirname(full_cache_path)

        manager = PreviewManager(cache_path, create_folder=True)
        path_to_preview_image = manager.get_jpeg_preview(full_path, width=1920, height=1080)
        self.document.preview.name = os.path.join(upload_cache_path, os.path.basename(path_to_preview_image))


class CreateBaseTask:
    def __init__(self, doc):
        self.document = doc
        self.task = Task
        self.approvers = self.document.approvers_list.all()

    def run(self):
        self.create_resolution_task()

    def create_resolution_task(self):
        logger.error(self.document.main_file.name)
        for executor in self.document.approvers_list.all():
            logger.error('entered cycle')

            self.task.objects.create(task_status=RUNNING, task_goal=REVIEW, document=self.document,
                                     parent_task=None, parent_node=None, is_completed=False,
                                     title="На узгодження", controller=None, is_controlled=False,
                                     content="Документ на узгождення", task_type=RESULT,
                                     start_date=now(), end_date=None, executor=executor,
                                     executor_role=MAIN)


class InitFields:
    def __init__(self, doc):
        self.document = doc

    def run(self):
        self.pre_save()

    def pre_save(self, *args, **kwargs):
        if self.document.document_cast == "INCOMING":
            self.document.blank_number = None
            self.document.registration_type = None
        else:
            self.document.outgoing_number = None
            self.document.outgoing_date = None
            self.document.correspondent = None
            self.document.signer = None
