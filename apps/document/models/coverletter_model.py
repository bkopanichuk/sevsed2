import os

from apps.l_core.models import CoreBase, CoreOrganization
from django.db import models

NONE = "NONE"
SPECIAL = "SPECIAL"

CONTROL_LEVEL = [(NONE, "Без контролю"), (SPECIAL, "Особливий")]


def get_upload_document_path(instance, filename):
    return os.path.join(
        f'uploads/document/organization_{instance.organization.id}', filename)


class CoverLetter(CoreBase):
    # General
    outgoing_number = models.CharField(verbose_name="Вхідний номер", max_length=100)
    outgoing_date = models.DateField(verbose_name="Вихідна дата")
    file = models.FileField(verbose_name="Супровідний файл", upload_to=get_upload_document_path, null=True)
    recipient = models.ForeignKey(CoreOrganization, related_name='cover_letters', verbose_name="Отримувач",
                                  on_delete=models.PROTECT)
    signer = models.CharField(verbose_name="Підписант", max_length=100)
    control_level = models.CharField(verbose_name="Рівень контролю", choices=CONTROL_LEVEL, blank=False, max_length=100)
    is_urgent = models.BooleanField(verbose_name="Терміново", default=False)

    class Meta:
        verbose_name = 'Супровідний лист'
        verbose_name_plural = 'Супровідні листи'
