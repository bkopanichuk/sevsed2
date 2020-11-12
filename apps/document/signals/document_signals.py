from django.db.models import signals
from apps.document.models.document_model import BaseDocument
from apps.document.services import CreateFlow
from apps.document.services.document_service import UpdateMainFileVersion, \
  CreatePreview, GenerateText
from apps.document.services.document.check_controllers_service import CheckControllers
from apps.document.services.document.close_task_executor_on_create_doc_service import CloseTaskExecutorOnCreateDoc
from apps.document.services.document.set_reply_date_service import SetReplyDate



def generate_text(instance, **kwargs):
    if instance.document.main_file:
        service = GenerateText(doc=instance.document)
        service.run()


def create_preview(instance, created, update_fields, **kwargs):
    if instance.main_file:
        service = CreatePreview(doc=instance, update_fields=update_fields)
        service.run()


def close_task_if_exist(instance, created, update_fields, **kwargs):
    if created and instance.execute_task_on_create:
        service = CloseTaskExecutorOnCreateDoc(task_executor=instance.execute_task_on_create, document=instance)
        service.run()


def update_main_file_version(instance, created, **kwargs):
    service = UpdateMainFileVersion(doc=instance)
    service.run()


def create_base_task(instance, action, **kwargs):
    print('action', action)
    if action == 'post_add':
        service = CreateFlow(doc=instance)
        service.run()


def check_controlers(instance, **kwargs):
    service = CheckControllers(doc=instance)
    service.run()

def set_reply_date(instance,**kwargs):
    service = SetReplyDate(doc=instance)
    service.run()




signals.pre_save.connect(receiver=set_reply_date, sender=BaseDocument)
signals.pre_save.connect(receiver=check_controlers, sender=BaseDocument)
signals.post_save.connect(receiver=create_preview, sender=BaseDocument)
signals.post_save.connect(receiver=close_task_if_exist, sender=BaseDocument)
signals.post_save.connect(receiver=update_main_file_version, sender=BaseDocument)
signals.m2m_changed.connect(receiver=create_base_task, sender=BaseDocument.approvers_list.through)
