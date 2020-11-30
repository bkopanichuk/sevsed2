from django.db import models, transaction
from django.db.models import Q
from rest_framework.exceptions import ValidationError

from apps.contracts.exceptions import StartDateOrEndDateIsNone
from apps.contracts.managers import ContractSubscriptionManager
from apps.contracts.utils import default_end_period
from apps.contracts.models.contract_constants import CHARGING_DATE
from apps.l_core.models import CoreBase
from apps.l_core.utilits.finance import get_pdv


class ProductMixin(object):
    def calculate_price_if_not_set(self):
        if not self.price:
            self.price = self.product.price
            self.total_price = self.count * self.price
            self.pdv = get_pdv(self.total_price)
            self.total_price_pdv = self.total_price + self.pdv


class XXXProducts(ProductMixin, CoreBase):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    product_name = models.CharField(max_length=250,null=True, verbose_name="Назва товару чи послуги")
    count = models.IntegerField(default=1)
    price = models.FloatField(default=0)
    total_price = models.FloatField(default=0)
    pdv = models.FloatField(default=0)
    total_price_pdv = models.FloatField(default=0)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.calculate_price_if_not_set()
        super(XXXProducts, self).save(*args, **kwargs)


class XXXSubscription(ProductMixin, CoreBase):
    product = models.ForeignKey('Subscription', on_delete=models.CASCADE)
    charging_day = models.IntegerField(verbose_name="Дата місяця на яку необхідно здійснювати нарахування оплати")
    start_period = models.DateField(verbose_name='Початок дії тарифного плану', )
    end_period = models.DateField(default=default_end_period, verbose_name='Кінець дії тарифного плану')
    is_legal = models.BooleanField(verbose_name='Вказує чи тарифний план наразі дійсний', default=True, editable=False)
    count = models.IntegerField(default=1)
    price = models.FloatField(default=0)
    total_price = models.FloatField(default=0)
    pdv = models.FloatField(default=0)
    total_price_pdv = models.FloatField(default=0)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.charging_day = CHARGING_DATE
        self.calculate_price_if_not_set()

        super(XXXSubscription, self).save(*args, **kwargs)


class ContractProducts(XXXProducts):
    contract = models.ForeignKey('Contract', on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = u'Послуги(товари) по договору'
        verbose_name = u'Послуги(товари) по договору'

    def __str__(self):
        return str(self.product)


class ContractSubscription(XXXSubscription):
    contract = models.ForeignKey('Contract', on_delete=models.CASCADE)
    objects = ContractSubscriptionManager()

    class Meta:
        verbose_name_plural = u'Послуги(товари) по договору'
        verbose_name = u'Послуги(товари) по договору'

    def __str__(self):
        return str(self.product)

    def calculate_date_if_not_set(self):
        if not self.start_period:
            self.start_period = self.contract.start_accrual

        if not self.end_period:
            self.end_period = self.contract.expiration_date

    def validate_new_subscription(self):
        if not self.start_period or not self.end_period:
            raise StartDateOrEndDateIsNone(self.start_period, self.end_period)
        q = ContractSubscription.objects.filter(contract=self.contract, product=self.product).filter(
            Q(start_period__range=(self.start_period, self.end_period)) | Q(
                end_period__range=(self.start_period, self.end_period)) | Q(
                start_period__lt=self.start_period, end_period__gt=self.end_period))
        if q.exists() and q.exclude(id=self.id).exists():
            raise ValidationError(
                {'start_period': 'Дата  дії тарифу не може перекриватись з іншими тарифами того ж тарифного плану'})

    def before_set_new_subscription(self):
        self.validate_new_subscription()
        q = ContractSubscription.objects.select_for_update().filter(contract=self.contract,
                                                                    product=self.product,
                                                                    end_period__isnull=True).exclude(id=self.id)
        if q.exists:
            with transaction.atomic():
                q.update(end_period=self.start_period)

    def save(self, *args, **kwargs):
        self.calculate_date_if_not_set()
        self.before_set_new_subscription()
        super(ContractSubscription, self).save(*args, **kwargs)


class AccrualProducts(XXXProducts):
    accrual = models.ForeignKey('RegisterAccrual', on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = u'Послуги(товари) по договору'
        verbose_name = u'Послуги(товари) по договору'


class AccrualSubscription(XXXSubscription):
    accrual = models.ForeignKey('RegisterAccrual', on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = u'Послуги(товари) по договору'
        verbose_name = u'Послуги(товари) по договору'