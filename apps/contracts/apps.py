from django.apps import AppConfig


class ContractsConfig(AppConfig):
    name = 'contracts'
    verbose_name = 'Договори'

    def ready(self):
        from apps.contracts import connectors
        pass