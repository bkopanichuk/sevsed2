from django.db import models
from django.db import transaction
from django.db.models import F
from django.utils.timezone import localdate
from multiselectfield import MultiSelectField

from apps.l_core.models import CoreBase
from ..models.document_constants import DOCUMENT_CAST
from ..models.validators import mask_validator


class RegistrationMask(CoreBase):
    name = models.CharField(verbose_name="Назва", max_length=100)
    description = models.TextField(verbose_name="Опис", max_length=400, null=True, blank=True)
    mask = models.CharField(verbose_name="Маска", max_length=150, validators=[mask_validator])

    class Meta:
        verbose_name = 'Маска реєстраціного номеру'
        verbose_name_plural = 'Маски реєстраціних номерів'

    def __str__(self):
        return f'{self.name}  ---  "{self.mask}"'


MASK_HELP_TEXT = """
{seq_number} - номер документа в межах реєстраційного ключа \n
{yyyy} - поточний рік (4 символи) \n
{yy} - поточний рік (2 символи) \n
{idx_journal} - код журналу \n
{doc_cast} - код виду документа \n
"""


class RegistrationJournal(CoreBase):
    #code = models.SlugField(verbose_name="Код", unique=True)
    mask = models.ForeignKey(RegistrationMask, on_delete=models.PROTECT, related_name='registration_journals',
                             verbose_name="Маска реєстрації", help_text=MASK_HELP_TEXT)
    max_count_to_new_volume = models.PositiveIntegerField(verbose_name="Кількість документів в томі", default=250)
    current_max_number = models.PositiveIntegerField(verbose_name="Поточний максимальний номер", default=1,editable=False)
    name = models.CharField(verbose_name="Назва", max_length=100)
    document_cast = models.CharField(verbose_name="Вид документа", choices=DOCUMENT_CAST,
                                     max_length=50)

    class Meta:
        verbose_name = 'Журнал реєстрації'
        verbose_name_plural = 'Журнали реєстрації'

    def __str__(self):
        return f'{self.name}'

    def get_document_variables(self, document):
        if not document:
            return {}
        else:
            data = dict(
                doc_cast=document.document_cast,

            )
            return data

    def get_variables(self, document=None):
        today = localdate()
        kwargs = dict(
            seq_number=self.get_next_number(),
            today=today,
            yyyy=today.year,
            yy=str(today.year)[2:],
            idx_journal=self.document_cast,
        )
        doc_info = self.get_document_variables(document)
        kwargs.update(doc_info)
        return kwargs

    def get_next_number(self):
        with transaction.atomic():
            self.current_max_number = F('current_max_number') + 1
            self.save()
            self.refresh_from_db()
        return self.current_max_number



    def get_next_register_number(self, document=None):
        kwargs = self.get_variables(document)
        reg_number_mask = self.mask.mask
        reg_number= reg_number_mask.format(**kwargs)
        return reg_number




class RegistrationJournalVolumeManager(models.Manager):
    def latest_volume(self, registration_journal_id):
        return super(RegistrationJournalVolumeManager, self).get_query_set().select_for_update().filter(
            registration_journal_id=registration_journal_id).latest('date_add')


class RegistrationJournalVolume(CoreBase):
    registration_journal = models.ForeignKey(RegistrationJournal, on_delete=models.PROTECT,
                                             related_name='registration_journal_volumes',
                                             verbose_name="Журнал")
    name = models.CharField(verbose_name="Назва(номер)", max_length=100)

    current_max_number = models.PositiveIntegerField()
    objects = RegistrationJournalVolumeManager()

    class Meta:
        verbose_name = 'Том журналу реєстрації'
        verbose_name_plural = 'Томи журналів реєстрації'

    def __str__(self):
        return f'{self.name}'

    @classmethod
    def get_next_number(cls, registration_journal_id):
        journal = RegistrationJournalVolume.objects.latest_volume(
            registration_journal_id=registration_journal_id)
        with transaction.atomic():
            journal.current_max_number = F('current_max_number') + 1
            journal.save()
            current_max_number = journal.refresh_from_db().current_max_number
            return current_max_number
