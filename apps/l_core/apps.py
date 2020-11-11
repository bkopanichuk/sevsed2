from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = 'apps.l_core'
    verbose_name = 'Адміністрування'

    def ready(self):
        pass