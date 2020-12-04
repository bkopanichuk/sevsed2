# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.gis.db import models
from django.utils.timezone import now

from apps.dict_register.models import DictBase
from apps.l_core.models import CoreBase


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
    service_type = models.ForeignKey(ServiceType, on_delete=models.PROTECT, null=True)

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
