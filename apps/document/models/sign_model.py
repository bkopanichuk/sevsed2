from django.contrib.postgres.fields import JSONField
from django.db import models

from apps.document.models.document_model import BaseDocument
from apps.l_core.models import CoreUser


class Sign(models.Model):
    document = models.ForeignKey(BaseDocument, related_name='document_sign', verbose_name="До документа",
                                 on_delete=models.CASCADE, null=True, blank=True)
    signer = models.ForeignKey(CoreUser, verbose_name="Підписант", on_delete=models.PROTECT, null=True,
                               blank=True)
    sign = models.TextField(max_length=100, null=True, blank=True, verbose_name="Підпис")
    sign_info = JSONField(null=True, verbose_name='Детальна інформація про накладений цифровий підпис')

    class Meta:
        verbose_name = 'Підпис'
        verbose_name_plural = 'Підписи'
