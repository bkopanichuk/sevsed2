from django.db import models
from apps.l_core.models import CoreBase


class IncomingDocumentType(CoreBase):
    name = models.CharField(max_length=200, verbose_name='Тип вхідного документа')
    execute_interval = models.PositiveSmallIntegerField(default=5, verbose_name='Час на обробку документа (робочих днів)')
    execute_interval_reason = models.TextField(null=True, max_length=1000,
                                               verbose_name='Обгарунтування встановленого часу на обробку',
                                               help_text="Необхідно вказати станню закону, постанову КМУ, або інший нормативний документ")

    class Meta:
        verbose_name = 'Тип вхідного документу'
        verbose_name_plural = 'Типи вхідних документів'

    def __str__(self):
        return self.name


class OutgoingDocumentType(CoreBase):
    name = models.CharField(max_length=200, verbose_name='Тип вхідного документа')

    class Meta:
        verbose_name = 'Тип вихідного документу'
        verbose_name_plural = 'Типи вихідних документів'

    def __str__(self):
        return self.name



class InnerDocumentType(CoreBase):
    name = models.CharField(max_length=200, verbose_name='Тип внутрішнього документа')

    class Meta:
        verbose_name = 'Тип внутрішнього документу'
        verbose_name_plural = 'Типи внутрішніх документів'

    def __str__(self):
        return self.name
