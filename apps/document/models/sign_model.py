from django.contrib.postgres.fields import JSONField
from django.db import models

from apps.document.models.document_model import BaseDocument
from apps.l_core.models import CoreUser


class Sign(models.Model):
    document = models.ForeignKey(BaseDocument, related_name='document_sign', verbose_name="До документа",
                                 on_delete=models.CASCADE, null=True, blank=True)
    signer = models.ForeignKey(CoreUser, verbose_name="Підписант", on_delete=models.PROTECT, null=True,
                               blank=True)
    sign = models.TextField(max_length=500, null=True, blank=True, verbose_name="Підпис")
    sign_info = JSONField(null=True, verbose_name='Детальна інформація про накладений цифровий підпис')

    class Meta:
        verbose_name = 'Підпис'
        verbose_name_plural = 'Підписи'

    def get_formated_sign_time(self,t):
        return f'{t.get("wYear")}-{t.get("wMonth")}-{t.get("wDay")}:{t.get("wHour")}:{t.get("wMinute")}:{t.get("wSecond")}'

    def get_signer_info_text(self):
        template_sign = """\n
        -------------------------------
        Підписант:	{pszSubjFullName}\n
        Серійний номер: {pszSerial}\n
        Місце знаходження:	{pszSubjLocality}\n
        Мітка часу:  {bTimeStamp}\n
        Дата підписання:{Time} \n
        -------------------------------\n """
        info = self.sign_info.get('cert')
        info['Time'] = self.get_formated_sign_time(info['Time'])
        f_string = template_sign.format(**info)
        return f_string
