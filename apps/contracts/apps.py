from django.apps import AppConfig

class ContractsConfig(AppConfig):
    name = 'apps.contracts'
    verbose_name = 'Договори'

    def ready(self):
        from apps.contracts.signals.contract_signals import init_signals
        #init_signals()
