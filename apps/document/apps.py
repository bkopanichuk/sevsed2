from django.apps import AppConfig


class DocumentConfig(AppConfig):
    name = 'apps.document'
    verbose_name = 'Документи'

    def ready(self):
        from apps.document.signals.document_signals import  create_preview
        from apps.document.signals.task_signals import set_parent_task, set_child_status
