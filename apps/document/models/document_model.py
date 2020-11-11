import os
import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from simple_history.models import HistoricalRecords

from apps.document.models import register_model
from apps.document.models.coverletter_model import CoverLetter
from apps.document.models.document_constants import DOCUMENT_CAST
from apps.document.models.document_constants import CustomDocumentPermissions
from apps.document.models.documenttype_model import IncomingDocumentType, OutgoingDocumentType
from apps.l_core.models import CoreBase, CoreOrganization, Department, CoreUser

#################################################DOCUMENT_STATUS_CHOICES################################################
ON_REGISTRATION = 'ON_REGISTRATION'
REGISTERED = 'REGISTERED'
ON_RESOLUTION = 'ON_RESOLUTION'
ON_EXECUTION = 'ON_EXECUTION'
COMPLETED = 'COMPLETED'
ON_CONTROL = 'ON_CONTROL'
PASSED_CONTROL = 'PASSED_CONTROL'
ARCHIVED = 'ARCHIVED'

# Outcoming document
ON_AGREEMENT = 'ON_AGREEMENT'
PROJECT = 'PROJECT'
REJECT = 'REJECT'
CONCERTED = 'CONCERTED'
ON_SIGNING = 'ON_SIGNING'
SIGNED = 'SIGNED'
TRANSFERRED = 'TRANSFERRED'

##################################################INCOMING_DOCUMENT_STATUS_CHOICES######################################
INCOMING_DOCUMENT_STATUS_CHOICES = (
    (ON_REGISTRATION, 'На реєстрації'),
    (REGISTERED, 'Зареєстрованний'),
    (ON_RESOLUTION, 'На резолюції'),
    (ON_EXECUTION, 'На виконанні'),
    (COMPLETED, 'Виконаний'),
    (ON_CONTROL, 'На контролі'),
    (PASSED_CONTROL, 'Знятий з контролю'),
    (ARCHIVED, 'В архіві'),
)
#################################################################################S######################################
##################################################OUTGOING_DOCUMENT_STATUS_CHOICES######################################
OUTGOING_DOCUMENT_STATUS_CHOICES = (
    (PROJECT, 'Проект'),
    (ON_AGREEMENT, 'На узгодженні'),
    (REJECT, 'Повернуто на доопрацювання'),  ##Якщо відмова
    (CONCERTED, 'Узгоджений'),
    (ON_REGISTRATION, 'На реєстрації'),
    (REGISTERED, 'Зареєстрованний'),
    (TRANSFERRED, 'Відправлено'),
    (ARCHIVED, 'В архіві'),
)
########################################################################################################################
####################################INNER_DOCUMENT_STATUS_CHOICES#######################################################
INNER_DOCUMENT_STATUS_CHOICES = (
    (PROJECT, 'Проект'),
    (ON_REGISTRATION, 'На реєстрації'),
    (REGISTERED, 'Зареєстрованний'),
    (ON_AGREEMENT, 'На узгодженні'),
    (REJECT, 'Повернуто на доопрацювання'),  ##Якщо відмова
    (CONCERTED, 'Узгоджений'),
    (ON_RESOLUTION, 'На резолюції'),
    (ON_EXECUTION, 'На виконанні'),
    (COMPLETED, 'Виконаний'),
    (ON_CONTROL, 'На контролі'),
    (PASSED_CONTROL, 'Знятий з контролю'),
    (ARCHIVED, 'В архіві'),

)
########################################################################################################################
MANUAL_REG = 'MANUAL_REG'
AUTOMATIC_REG = 'AUTOMATIC_REG'
REGISTRATION_TYPES = [(MANUAL_REG, "Ручна"), (AUTOMATIC_REG, "Автоматична")]

########################################################################################################################
###############################################APPROVE_TYPE#############################################################
WITH_APPROVE = 'WITH_APPROVE'
WITHOUT_APPROVE = 'WITHOUT_APPROVE'
APPROVE_TYPE = [(WITH_APPROVE, "З узгодженням"), (WITHOUT_APPROVE, "Простий (без узгодження)")]
########################################################################################################################
###################MAILING_METHODS######################################################################################
EMAIL = 'EMAIL'
SEV = 'SEV'
LETTER = 'LETTER'
MAILING_METHODS = ((EMAIL, 'Електронна пошта'), (SEV, 'СЕВОВВ'), (LETTER, 'Лист'))


########################################################################################################################
def get_upload_document_path(instance, filename):
    return os.path.join(
        f'uploads/document/org_{instance.organization.id}/{instance.unique_uuid}/files', filename)


def get_upload_path(instance, filename):
    return os.path.join(
        f'uploads/document/org_{instance.organization.id}_{instance.unique_uuid}/')


def def_reg_number(*args):
    return f'{uuid.uuid1()}'


def get_preview_directory(instance, filename):
    return os.path.join(
        f'uploads/document/org_{instance.organization.id}/{instance.unique_uuid}/preview/')


class IncomingDocument(models.Model):
    # Incoming details
    outgoing_number = models.CharField(verbose_name="*Вихідний номер", max_length=100, null=True, blank=True)
    outgoing_date = models.DateField(verbose_name="*Вихідна дата", null=True, blank=True)
    correspondent = models.ForeignKey(CoreOrganization, related_name='incoming_documents', verbose_name="Кореспондент",
                                      on_delete=models.PROTECT, null=True, blank=True)
    signer = models.CharField(verbose_name="*Підписант", max_length=100, null=True, blank=True)
    sign = models.TextField(verbose_name="*Підпис", max_length=100, null=True, blank=True)
    cover_letter = models.ForeignKey(CoverLetter, verbose_name="*Супровідний лист", on_delete=models.PROTECT, null=True,
                                     blank=True)
    incoming_type = models.ForeignKey(IncomingDocumentType, verbose_name="Тип документа", on_delete=models.PROTECT,
                                      null=True)
    execute_task_on_create = models.ForeignKey('TaskExecutor', verbose_name="Закрити задачу при стовренні документа",
                                               on_delete=models.PROTECT, null=True)
    reply_date = models.DateField(verbose_name="Кінцева дата  для надання відповіді", null=True, blank=True)
    source = models.CharField(choices=MAILING_METHODS, default=LETTER, verbose_name="Джерело надходження",
                              max_length=10)

    class Meta:
        abstract = True


class OutgoingDocument(models.Model):
    blank_number = models.CharField(verbose_name="&Номер бланку", max_length=100, null=True, blank=True)
    outgoing_type = models.ForeignKey(OutgoingDocumentType, verbose_name="Тип вихідного документа",
                                      on_delete=models.PROTECT, null=True)
    approve_type = models.CharField(verbose_name="Чи потрібне узгодження", default=WITH_APPROVE, choices=APPROVE_TYPE,
                                    max_length=20)
    mailing_list = models.ManyToManyField(CoreOrganization, related_name='outgoing_documents', verbose_name='Адресати')
    main_signer = models.ForeignKey(CoreUser, related_name='outgoing_document_signer', verbose_name='Підписант',
                                    on_delete=models.PROTECT,null=True)
    mailing_method = models.CharField(choices=MAILING_METHODS, default=LETTER, verbose_name="Спосіб відпралення",
                                      max_length=10)

    class Meta:
        abstract = True


class innerDocument(models.Model):
    class Meta:
        abstract = True


class BaseDocument(IncomingDocument, OutgoingDocument, innerDocument, CoreBase):
    # General
    title = models.CharField(verbose_name="Назва", max_length=100, default='-')
    main_file = models.FileField(verbose_name="Головинй файл", upload_to=get_upload_document_path, null=True)

    document_cast = models.CharField(verbose_name="Вид документа", choices=DOCUMENT_CAST,
                                     max_length=100)
    reg_number = models.CharField(verbose_name="Реєстраціний номер", max_length=100, null=True)
    reg_date = models.DateField(verbose_name="Дата реєстрації", null=True, editable=False)

    comment = models.TextField(verbose_name="Короткий зміст", max_length=500, null=True, blank=True)
    document_linked_to = models.ManyToManyField('self', related_name='document_linked_to_document',
                                                verbose_name="До документа", blank=True)
    department = models.ForeignKey(Department, verbose_name="Департамент", on_delete=models.SET_NULL, null=True,
                                   blank=True)
    approvers_list = models.ManyToManyField(get_user_model(), verbose_name="На розгляд",
                                            help_text="Список користувачів які мають розглянути документ", blank=True)
    registration_type = models.CharField(verbose_name="&Тип реєстрації", choices=REGISTRATION_TYPES, default=MANUAL_REG,
                                         max_length=50)
    registration = models.ForeignKey(register_model.RegistrationJournal,
                                     verbose_name="Журнал реєстрації",
                                     on_delete=models.PROTECT, null=True, blank=True)
    case_index = models.CharField( verbose_name="Індекс  та  заголовок справи",
                                     max_length=100, null=True)

    case_number = models.CharField( verbose_name="Номер тому справи",
                                     max_length=100, null=True)

    preview = models.FileField(upload_to=get_preview_directory, null=True, editable=False, max_length=500)
    preview_pdf = models.FileField(upload_to=get_preview_directory, null=True, editable=False, max_length=500)
    status = models.CharField(verbose_name="Статус", max_length=100, default=PROJECT)
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Документ'
        verbose_name_plural = 'Документы'
        permissions = [
            (CustomDocumentPermissions.REGISTER_DOCUMENT, "Може реєструвати документ"),
            (CustomDocumentPermissions.CREATE_RESOLUTION, "Може створювати резолюцію"),
            (CustomDocumentPermissions.EXECUTE_RESOLUTION, "Може запускати резолюцію на виконання"),
            (CustomDocumentPermissions.SEND_TO_ARCHIVE, "Може відправляти документ в архів"),
        ]

    def __str__(self):
        return f'{self.get_document_cast_display()} документ "{self.reg_number}"'

    def save(self, *args, **kwargs):
        super(BaseDocument, self).save(*args, **kwargs)


class MainFileVersion(models.Model):
    document = models.ForeignKey(BaseDocument, on_delete=models.CASCADE)
    add_date = models.DateTimeField(auto_now_add=True, null=True)
    main_file = models.FileField(verbose_name="Головинй файл", upload_to=get_upload_document_path, null=True)

    class Meta:
        verbose_name = 'Документ'
        verbose_name_plural = 'Документы'
