# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.gis.db import models
from django.utils.crypto import get_random_string
from django.utils.timezone import now

from apps.l_core.models import CoreBase


class DictBase(CoreBase):
    parent = models.ForeignKey('self', null=True, on_delete=models.SET_NULL)
    is_group = models.BooleanField(default=False)
    code = models.SlugField(verbose_name="Код", default=get_random_string)
    name = models.CharField(max_length=200, blank=True, null=True, verbose_name="Значення")

    class Meta:
        abstract = True
        unique_together = ['code']

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


class ProductPropertyMixin():

    def get_actual_data(self, calc_date=None):
        if not calc_date:
            calc_date = now().date()
        return self.productpricedetails_set.filter(start_period__lte=calc_date).order_by('-start_period').first()

    @property
    def start_period(self):
        return self.get_actual_data().start_period

    @property
    def price(self):
        return self.get_actual_data().price

    @property
    def pdv(self):
        return self.get_actual_data().pdv

    @property
    def price_pdv(self):
        return self.get_actual_data().price_pdv


class Product(DictBase, ProductPropertyMixin):
    UNIT_CHOICES = [
        ['service', 'Послуга'],
        ['product', 'ТОвар'],
    ]
    unit = models.CharField(verbose_name="Одиничі виміру", choices=UNIT_CHOICES, max_length=100)

    class Meta:
        verbose_name = u'Послуги,Товари'

    def __str__(self):
        return self.name


class ProductPriceDetails(DictBase):
    start_period = models.DateField(verbose_name='Початок дії ціни', )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.FloatField(verbose_name="Ціна")
    pdv = models.FloatField(verbose_name="ПДВ")
    price_pdv = models.FloatField(verbose_name="Ціна з ПДВ")

    def __str__(self):
        return f'{self.product} -  від {self.start_period}'


class ServiceType(CoreBase):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        verbose_name = u'Типи послуг'


class Subscription(DictBase, ProductPropertyMixin):
    service_type = models.ForeignKey(ServiceType, on_delete=models.PROTECT)

    class Meta:
        verbose_name = u'Обслуговування, абонплата'

    def __str__(self):
        return self.name

    def get_actual_data(self, calc_date=None):
        if not calc_date:
            calc_date = now().date()
        return self.subscriptionpricedetails_set.filter(start_period__lte=calc_date).order_by('-start_period').first()

    @property
    def s_count(self):
        return self.get_actual_data().s_count

    @property
    def unit(self):
        return self.get_actual_data().unit


class SubscriptionPriceDetails(DictBase):
    UNIT_CHOICES = [
        ['mb', 'Мегабайти'],
    ]
    start_period = models.DateField(verbose_name='Початок дії ціни', )
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE)
    price = models.FloatField(verbose_name="Ціна")
    pdv = models.FloatField(verbose_name="ПДВ")
    price_pdv = models.FloatField(verbose_name="Ціна з ПДВ")

    unit = models.CharField(verbose_name="Одиничі виміру", choices=UNIT_CHOICES, max_length=100,
                            default=UNIT_CHOICES[0][0])
    s_count = models.FloatField(null=True, verbose_name="Кількість ")

    def __str__(self):
        return f'{self.subscription} -  від {self.start_period}'


class TemplateDocument(DictBase):
    template_file = models.FileField(upload_to='uploads/doc_templates/%Y/%m/%d/', null=True,
                                     verbose_name="Шаблон документу (договору)")
    related_model_name = models.SlugField(unique=True, max_length=100, verbose_name="Шаблон документу")

    class Meta:
        verbose_name = u'Шаблон документу'

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return '{0}'.format(self.related_model_name or '-', )
