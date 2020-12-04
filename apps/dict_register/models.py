from django.db import models
import os

# Create your models here.
from django.utils.crypto import get_random_string

from apps.l_core.models import CoreBase, CoreOrganization


class DictBase(CoreBase):
    organization = models.ForeignKey(CoreOrganization, null=True, on_delete=models.CASCADE,
                                     verbose_name="**Організація",
                                     help_text="До якої організації відноситься інформація")
    parent = models.ForeignKey('self', null=True, on_delete=models.SET_NULL)
    is_group = models.BooleanField(default=False)
    protected = models.BooleanField(default=False, verbose_name='Захищено від видалення')
    code = models.SlugField(verbose_name="Код", default=get_random_string)
    name = models.CharField(max_length=200, blank=True, null=True, verbose_name="Значення")

    class Meta:
        abstract = True

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return '{0} {1}'.format(self.code or '-', self.name or '-')


class MainActivity(DictBase):
    class Meta:
        verbose_name = u'Вид основної діяльності'


class OrganizationType(DictBase):
    class Meta:
        verbose_name = u'Типів органцізації'


class PropertyType(DictBase):
    class Meta:
        verbose_name = u'Тип власності'


def get_upload_template_path(instance, filename):
    return os.path.join(
        f'uploads/document_templates/org_{instance.organization.id}/', filename)


class TemplateDocument(DictBase):
    template_file = models.FileField(upload_to=get_upload_template_path, null=True, max_length=500,
                                     verbose_name="Шаблон документу")
    related_model_name = models.SlugField(unique=True, max_length=100, verbose_name="Сигнатура шаблону")

    class Meta:
        verbose_name = u'Шаблон документу'
        verbose_name_plural = u'Шаблони документів'
        unique_together=['related_model_name','organization']

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return '{0}'.format(self.related_model_name or '-', )
