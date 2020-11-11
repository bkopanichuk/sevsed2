from django.apps import AppConfig


class SevovvintegrationConfig(AppConfig):
    name = 'apps.sevovvintegration'

    def ready(self):
        from apps.sevovvintegration.signals import processing_outgoing
