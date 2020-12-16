from django.apps import AppConfig


class DocumentConfig(AppConfig):
    name = 'apps.document'
    verbose_name = 'Документи'

    def ready(self):
        from apps.document.signals.document_signals import init_document_signals
        from apps.document.signals.task_signals import init_task_signals
        init_document_signals()
        init_task_signals()
