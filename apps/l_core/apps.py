import smtplib

from django.apps import AppConfig
from django.conf import settings

from apps.l_core.utilits.project_hash import CheckProjectHash
from config.email_settings import EMAIL_HOST, DEFAULT_FROM_EMAIL, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD


class CoreConfig(AppConfig):
    name = 'apps.l_core'
    verbose_name = 'Адміністрування'

    def ready(self):
        if not CheckProjectHash():
            mail_client = smtplib.SMTP(EMAIL_HOST)
            mail_client.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
            admins = settings.ADMINS
            for admin in admins:
                mail_client.sendmail(DEFAULT_FROM_EMAIL, admin[1], "Hash of the app has been changed, please update the app ")