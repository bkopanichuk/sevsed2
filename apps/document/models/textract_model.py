from django.db import models

from apps.document.models.document_model import BaseDocument


class DocumentGeneratedText(models.Model):
    document = models.ForeignKey(BaseDocument, on_delete=models.CASCADE)
    text = models.TextField(verbose_name="Зміст", null=True, blank=True)

    class Meta:
        verbose_name = 'Зміст'
        verbose_name_plural = 'Зміст'
