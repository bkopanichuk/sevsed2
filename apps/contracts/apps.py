from django.apps import AppConfig


class ContractsConfig(AppConfig):
    name = 'contracts'

    def ready(self):
        from apps.contracts import connectors
        pass