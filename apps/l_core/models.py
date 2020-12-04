# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import AbstractUser, Permission, Group
from django.contrib.gis.db import models
from django.core.validators import FileExtensionValidator
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from apps.atu.models import ATURegion, ATUDistrict
from .abstract_base import AbstractBase
from .exceptions import AuthorNotSet, AuthorOrganizationNotSet
from .mixins import RelatedObjects, CheckProtected


class GroupOrganization(AbstractBase):
    name = models.CharField(max_length=200, blank=True, null=True, verbose_name=u'Назва')

    class Meta:
        verbose_name = u'Група компаній (організацій)'

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return '{0}'.format(self.name)


class AbstractCoreOrganization(AbstractBase):
    BANK = (('K', 'Комерційний'), ('Б', 'Бюджет'))

    name = models.TextField(blank=True, null=True, db_index=True, verbose_name="Назва організації")
    full_name = models.TextField(blank=True, null=True, verbose_name="Повна назва організації")
    address = models.CharField(max_length=200, blank=True, null=True, verbose_name="Адреса")
    edrpou = models.CharField(max_length=50, blank=True, null=True, unique=True, db_index=True, verbose_name="ЄДРПОУ")
    mfo = models.CharField(max_length=50, blank=True, null=True, verbose_name="МФО")
    phone = models.CharField(max_length=200, blank=True, null=True, verbose_name="Телефон")
    fax = models.CharField(max_length=200, blank=True, null=True, verbose_name="Факс")
    email = models.EmailField(max_length=200, blank=True, null=True, verbose_name="EMAIL")
    site = models.URLField(max_length=200, blank=True, null=True, verbose_name="Сайт")
    status = models.CharField(max_length=50, blank=True, null=True, verbose_name="Статус", db_index=True)
    register_date = models.DateField(blank=True, null=True, verbose_name="Дата державної реєстрації")
    work_reason = models.TextField(null=True, verbose_name="Працює на підставі")
    sert_name = models.CharField(max_length=200, blank=True, null=True,
                                 verbose_name="Серія та номер державної реєстрації")
    settlement_account = models.CharField(max_length=30, blank=True, null=True, verbose_name="Розрахунковий рахунок")
    bank = models.CharField(choices=BANK, verbose_name="Тип банку", null=True, max_length=1)
    bank_name = models.CharField(max_length=200, verbose_name="Назва банку", null=True)
    ipn = models.CharField(max_length=200, blank=True, null=True, verbose_name="ІПН")
    taxation_method = models.CharField(max_length=200, blank=True, null=True, verbose_name="Спосіб оподаткування")
    certificate_number = models.CharField(max_length=200, blank=True, null=True, verbose_name="Номер свідотства ПДВ")
    main_unit = models.CharField(max_length=200, blank=True, null=True, verbose_name="Уповноважена особа")
    main_unit_state = models.CharField(max_length=200, blank=True, null=True, verbose_name="Посада уповноваженої особи")
    main_activity_text = models.CharField(max_length=200, null=True, blank=True,
                                          verbose_name=u'Основна діяльність (text)')
    region = models.ForeignKey(ATURegion, null=True, blank=True, verbose_name=u'Область', on_delete=models.PROTECT)
    district = models.ForeignKey(ATUDistrict, null=True, blank=True, verbose_name=u'Район', on_delete=models.PROTECT)
    group_organization = models.ForeignKey(GroupOrganization, null=True,
                                           on_delete=models.PROTECT, verbose_name=u'Група компаній')
    central_office = models.PointField(null=True, verbose_name=u'Центральний офіс', blank=True)
    statute_copy = models.FileField(null=True, verbose_name="Статутні документи",
                                    validators=[
                                        FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'jpg'])])
    note = models.TextField(blank=True, null=True, verbose_name="Примітка")

    class Meta:
        abstract = True


class CoreOrganization(AbstractCoreOrganization):
    author = models.ForeignKey('l_core.CoreUser', related_name='%(class)s_author', null=True, editable=False,
                               on_delete=models.PROTECT)
    editor = models.ForeignKey('l_core.CoreUser', related_name='%(class)s_editor', null=True, editable=False,
                               on_delete=models.PROTECT)
    organization = models.ForeignKey('self', null=True, on_delete=models.PROTECT)
    system_id = models.CharField(max_length=256, null=True)
    system_password = models.CharField(max_length=256, null=True)

    class Meta:
        verbose_name = u'Організації'

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return '{0} {1}'.format(self.name or self.full_name, self.edrpou or '')

    def save(self, *args, **kwargs):
        self.validate_organization()
        self.set_organization()
        self.check_org()
        super(CoreOrganization, self).save(*args, **kwargs)

    def set_organization(self):
        if hasattr(self, 'organization'):
            if not self.organization and self.author:
                self.organization = self.author.organization

    def validate_organization(self):
        if hasattr(self, 'organization'):
            if self.organization:
                return
            if not self.author.organization:
                raise AuthorOrganizationNotSet(self.author.organization)

    def check_org(self):
        if not self.organization:
            raise Exception('field "organization" not allowed null value')



class Department(AbstractBase):
    organization = models.ForeignKey(CoreOrganization, on_delete=models.PROTECT, null=True)
    name = models.CharField(max_length=200, blank=True, null=True, verbose_name=u'Назва')

    class Meta:
        verbose_name = u'Департамент оргацінзації'

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return '{0}'.format(self.name)


class CoreUser(RelatedObjects, CheckProtected, AbstractUser):
    organization = models.ForeignKey(CoreOrganization, null=True, on_delete=models.PROTECT)
    department = models.ForeignKey(Department, null=True, on_delete=models.PROTECT)
    first_name = models.CharField(_('first name'), max_length=30, blank=False)
    last_name = models.CharField(_('last name'), max_length=150, blank=False)
    email = models.EmailField(_('email address'), blank=False)
    ipn = models.CharField(max_length=10, null=True)

    class Meta:
        verbose_name = u'Користувач'
        verbose_name_plural = u'Користувачі'

    def __str__(self):
        return f' {self.last_name} {self.first_name}'


class SystemFieldsMixin(models.Model):
    date_add = models.DateTimeField(auto_now_add=True, null=True, editable=False, verbose_name="**Дата створення",
                                    db_index=True)
    date_edit = models.DateTimeField(auto_now=True, null=True, editable=False, verbose_name="**Дата останньої зміни",
                                     db_index=True)

    class Meta:
        abstract = True


class PersonIdentityMixin(models.Model):
    author = models.ForeignKey(CoreUser, related_name='%(class)s_author', null=True, editable=False,
                               on_delete=models.PROTECT, verbose_name="**Автор")
    editor = models.ForeignKey(CoreUser, related_name='%(class)s_editor', null=True, editable=False,
                               on_delete=models.PROTECT, verbose_name="**Останій редактор")

    class Meta:
        abstract = True


class OrganizationIdentityMixin(models.Model):
    organization = models.ForeignKey(CoreOrganization, null=True, on_delete=models.PROTECT,
                                     verbose_name="**Організація",
                                     help_text="До якої організації відноситься інформація")

    class Meta:
        abstract = True


class ComplexBaseMixin(SystemFieldsMixin, PersonIdentityMixin, OrganizationIdentityMixin):
    class Meta:
        abstract = True


class CoreBase(AbstractBase, SystemFieldsMixin, PersonIdentityMixin, OrganizationIdentityMixin):
    pass

    def save(self, *args, **kwargs):
        ##TODO Довелось закоментувати, бо при інтеграції з СЕВОВВ недостатньо даних для вказування повноцінного автора-(користувача)
        ##self.validate_author()
        self.validate_organization()
        self.set_organization()
        self.check_org()
        super(CoreBase, self).save(*args, **kwargs)

    def set_organization(self):
        if hasattr(self, 'organization'):
            if not self.organization and self.author:
                self.organization = self.author.organization

    def validate_author(self):
        if hasattr(self, 'organization'):
            if not self.author:
                raise AuthorNotSet(self.author)

    def validate_organization(self):
        if hasattr(self, 'organization'):
            if self.organization:
                return
            ##Якщо організація в документі вказана-далі не перевіряємо, можуть бути конфлікти при інтеграції з СЕВОВВ
            if not self.author.organization:
                raise AuthorOrganizationNotSet(self.author.organization)

    def check_org(self):
        if not self.organization:
            raise Exception('field "organization" not allowed null value')

    class Meta:
        default_permissions = ('add', 'change', 'delete', 'view', 'view_self', 'delete_self', 'change_self')
        abstract = True







class Counter(models.Model):
    max_value = models.IntegerField(default=0)
    model = models.CharField(max_length=100)

    @classmethod
    def next_id(cls, model):
        cls.dispatch(model)
        with transaction.atomic():
            counter_obj = cls.objects.select_for_update().filter(model=model).first()
            next_id = counter_obj.max_value + 1
            counter_obj.max_value = next_id
            counter_obj.save()
            return next_id

    @classmethod
    def dispatch(cls, model):
        with transaction.atomic():
            if cls.objects.select_for_update().filter(model=model).count() == 0:
                cls.objects.create(model=model)