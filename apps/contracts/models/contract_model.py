import calendar
import os
from datetime import date
from datetime import datetime
from typing import List

import docxtpl
from babel.dates import format_datetime
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db import transaction
from django.db.models import Q
from django.db.models import Sum
from django.utils.crypto import get_random_string
from django.utils.timezone import now
from num2words import num2words
from rest_framework.serializers import ValidationError
from simple_history.models import HistoricalRecords

from apps.contracts.exceptions import StartDateOrEndDateIsNone
from apps.contracts.managers import ContractSubscriptionManager
from apps.contracts.tasks import async_create_accrual_doc, async_create_act_doc
from apps.l_core.models import CoreBase
from apps.l_core.models import Counter
from apps.l_core.utilits.converter import LibreOfficeConverter
from apps.l_core.utilits.finance import get_pdv
from apps.l_core.utilits.month import LOCAL_MONTH
from .dict_model import Subscription
from .dict_model import TemplateDocument

MEDIA_ROOT = settings.MEDIA_ROOT

import logging

logger = logging.getLogger(__name__)

CHARGING_DATE = 20
############################################################
CONTRACT_STATUS_FUTURE = 'future'  ##'Укладається'
CONTRACT_STATUS_ACTUAL = 'actual'  ##'Дійсний'
CONTRACT_STATUS_ARCHIVE = 'archive'  ##'Архівний'
CONTRACT_STATUS_REJECTED = 'rejected'  ##'Не заключений', контраген відмовився підписувати договір

CONTRACT_STATUS = [
    [CONTRACT_STATUS_FUTURE, 'Укладається'],
    [CONTRACT_STATUS_ACTUAL, 'Дійсний'],
    [CONTRACT_STATUS_ARCHIVE, 'Архівний'],
    [CONTRACT_STATUS_REJECTED, 'Не заключений']
]

class Contract(CoreBase):
    parent_element = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
                                       verbose_name="Батьківський елемент")
    number_contract = models.TextField(max_length=50, verbose_name="№ Договору", null=True)

    subject_contract = models.TextField(max_length=500, null=True, verbose_name="Предмет договору")
    contractor = models.ForeignKey('l_core.CoreOrganization', related_name='%(class)s_contractor', null=True,
                                   blank=True,
                                   on_delete=models.PROTECT, verbose_name="Контрагент")
    price_contract = models.FloatField(default=0, verbose_name="Ціна договору")
    price_contract_by_month = models.FloatField(default=0, verbose_name="Ціна договору за місяць")
    price_additional_services = models.FloatField(default=0,
                                                  verbose_name="Вартість додаткових послуг(підключення і тд)")
    contract_time = models.IntegerField(verbose_name="Строк дії договору", null=True, blank=True)
    one_time_service = models.BooleanField(verbose_name="Одноразова послуга/купівля", default=False)
    start_date = models.DateField(verbose_name="Дата заключення договору")
    start_of_contract = models.DateField(verbose_name="Дата початку дії договору")
    start_accrual = models.DateField(null=True, verbose_name="Дата початку нарахувань")
    expiration_date = models.DateField(verbose_name="Дата закінчення")
    copy_contract = models.FileField(upload_to='uploads/copy_contract/%Y/%m/%d/', null=True,
                                     verbose_name="Копія договору")
    contract_docx = models.FileField(upload_to='uploads/contract_docx/%Y/%m/%d/', null=True,
                                     verbose_name="Проект договору")
    status = models.CharField(max_length=20, choices=CONTRACT_STATUS, default='future', verbose_name="Статус")
    change_status_reason = models.CharField(max_length=200, verbose_name="Причина зміни статусу", null=True)
    automatic_number_gen = models.BooleanField(default=False, verbose_name="Сформувати номер автоматично?")
    history = HistoricalRecords()

    class Meta:
        verbose_name_plural = u'Договори'
        verbose_name = u'Договір'

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return '{0}'.format(self.number_contract or '-')

    def save(self, *args, **kwargs):
        if not self.id:
            self.contract_time = self.get_contract_time()
            self.set_number_contract()
            ## Відключаємо автоматичне визначення дати початку договору, поки незрозуміло як реально здійснюються нарахування
            ##self.set_start_accrual_date()
        super(Contract, self).save(*args, **kwargs)

        ##self.set_details_from_statement()
        ##self.set_price_from_details()

    def set_number_contract(self):
        """Автоматично встановлює номер нового договору якщо встановлено відповідну відмітку"""
        if not self.id and self.automatic_number_gen:
            n = Counter.next_id('contracts_contract')
            ## 2/2019/K
            number_contract = f"{n}/{self.start_date.year}/{self.contractor.bank}"
            self.number_contract = number_contract

    def set_price_from_details(self):
        """Отримати деталі вартість послуг на поточну дату та записати """
        self.price_contract_by_month, self.price_contract = self.get_price_from_details()
        self.save()

    def get_price_from_details(self, actual_date=None):

        total_price_subscription_pdv = self.get_contract_subscription_price(actual_date=actual_date)
        total_price_products_pdv = ContractProducts.objects.filter(contract=self).aggregate(Sum('total_price_pdv'))[
                                       'total_price_pdv__sum'] or 0
        ## Кількість місяців в періоді платежів
        month_count = len(self.get_pay_periods())
        price_contract = (month_count * total_price_subscription_pdv) + total_price_products_pdv
        price_contract_by_month = total_price_subscription_pdv
        return (price_contract_by_month, price_contract)

    def get_subscription(self, subscription_pk):
        return Subscription.objects.get(pk=subscription_pk)

    def get_contract_subscription_price(self, actual_date=None):
        """ Отримати вартість тарифного плану на поточну дату """
        if not actual_date:
            actual_date = now().date()

        total_price_pdv = 0
        ## Отримуємо дійсний тарифний план
        q = ContractSubscription.objects.actual_on_date(actual_date=actual_date).filter(contract=self).values(
            'total_price_pdv')
        # raise Exception(q.query)
        if q.exists():
            total_price_pdv = q.aggregate(Sum('total_price_pdv'))['total_price_pdv__sum'] or 0
        print(actual_date, total_price_pdv)
        print((q.query))
        return total_price_pdv

    def get_contract_product_price(self):
        total_price_pdv = \
            ContractProducts.objects.filter(contract=self).values('total_price_pdv').aggregate(Sum('total_price_pdv'))[
                'total_price_pdv__sum'] or 0
        if not total_price_pdv:
            return self.price_additional_services
        return total_price_pdv

    def set_contract_product_price(self):
        self.price_additional_services = self.get_contract_product_price()
        self.save()

    def set_start_accrual_date(self):
        """Якщо початок договору пізніше 10-го числа поточного місяця,
        то початок нарахувань з 1-го числа настпного місяця, якшо менше то з 1-го поточного"""

        if self.start_date.day > 10:
            next_month = datetime(self.start_date.year, self.start_date.month, 1) + relativedelta(months=+1)
            self.start_accrual = next_month
        else:
            self.start_accrual = datetime(self.start_date.year, self.start_date.month, 1)

    def get_contract_time(self):
        """ Отримати загальний термін дії договору в днях """
        if self.expiration_date and self.start_accrual:
            return (self.expiration_date - self.start_accrual).days
        else:
            return 0

    @classmethod
    def refresh_total_balance(cls):
        """ Оновлює баданс по всих договорах"""
        contracts = Contract.objects.all()
        ##contracts = Contract.objects.values('country__name').annotate(Sum('population'))
        for contract in contracts:
            contract.save()
        return contracts.count()

    @classmethod
    def calculate_accruals(cls, start_date=None, end_date=None, create_pdf=None, is_comercial=None, is_budget=None):
        """ Розраховує нарахування для всіх договорів"""
        logging.debug('calculate_accruals')
        contracts = cls.objects.filter(expiration_date__gte=(end_date or date.today()))
        result = []
        for contract in contracts:
            res = RegisterAccrual.calculate_accruals(contract=contract, start_date=start_date, end_date=end_date)
            result.append(res)
        return result

    def calculate_accrual(self):
        res = RegisterAccrual.calculate_accruals(contract=self)
        return res

    def get_pay_periods(self, end_date=None):
        if hasattr(self, '__pay_periods'):
            return self.__pay_periods

        period_list = []
        start_date = self.start_accrual

        if type(start_date) == datetime:
            first_date = start_date.date()
        else:
            first_date = start_date

        end_date = end_date or self.expiration_date
        ##raise Exception(start_date)
        month_range = ((end_date.year - start_date.year) * 12 - start_date.month) + end_date.month
        ##raise Exception(month_range)
        ##print('month_range -> ', str(month_range))
        for month_index in range(month_range + 1):
            year = first_date.year
            ##print('first_date -> ', str(first_date))
            ##print('month_index -> ',month_index)
            month = (start_date + relativedelta(months=+month_index)).month
            ##print('month -> ',month)
            last_day_of_month = calendar.monthrange(year, month)[1]

            last_date = date(year, month, last_day_of_month)
            ##print('last_date:',type(last_date),'first_date:',type(first_date))
            interval = (last_date - first_date).days
            period_list.append({"start_date": first_date, "end_date": last_date, "interval": interval})
            ##print('last_date -> ', str(last_date))
            first_date = last_date + relativedelta(days=+1)
        ##print('pay_periods -> ', str(period_list))
        self.__pay_periods = period_list
        return period_list

    def refresh_balance(self):
        self.save()


class ProductMixin(object):
    def calculate_price_if_not_set(self):
        if not self.price:
            self.price = self.product.price
            self.total_price = self.count * self.price
            self.pdv = get_pdv(self.total_price)
            self.total_price_pdv = self.total_price + self.pdv


class XXXProducts(ProductMixin, CoreBase):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
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


def default_end_period():
    return date.today() + relativedelta(years=1)


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


class StageProperty(CoreBase):
    """"""
    contract = models.OneToOneField('Contract',
                                    on_delete=models.CASCADE, verbose_name="Договір")
    name = models.TextField(default='', verbose_name="Назва організації", null=True, blank=True)
    address = models.TextField(default='', null=True, blank=True)
    settlement_account = models.CharField(max_length=30, verbose_name="Розрахунковий рахунок", null=True, blank=True)
    bank_name = models.CharField(max_length=200, null=True, verbose_name="Назва банку")
    main_unit = models.CharField(max_length=200, blank=True, null=True, verbose_name="Уповноважена особа")
    main_unit_state = models.CharField(max_length=200, blank=True, null=True, verbose_name="Посада уповноваженої особи")
    mfo = models.CharField(max_length=50, null=True, blank=True, verbose_name='МФО')
    ipn = models.CharField(max_length=200, blank=True, null=True, verbose_name="ІПН")
    certificate_number = models.CharField(max_length=200, blank=True, null=True, verbose_name="Номер свідотства ПДВ")
    edrpou = models.CharField(max_length=10, verbose_name="ЄДРПОУ", null=True, blank=True)
    phone = models.CharField(max_length=150, verbose_name="Телефон", null=True, blank=True)
    email = models.CharField(max_length=150, verbose_name="email", null=True, blank=True)
    work_reason = models.TextField(null=True, verbose_name="Працює на підставі")
    statute_copy = models.FileField(null=True, verbose_name="Статутні документи")
    history = HistoricalRecords()

    class Meta:
        verbose_name_plural = u'Реквізити договорів'
        verbose_name = u'Реквізити договору'

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return 'Реквізити {0}'.format(str(self.contract) or '-')

    def load_from_contract(self):
        contractor = self.contract.contractor
        if not contractor:
            return
        self.name = contractor.full_name
        self.main_unit_state = contractor.main_unit_state
        self.main_unit = contractor.main_unit
        self.edrpou = contractor.edrpou
        self.bank_name = contractor.bank_name
        self.mfo = contractor.mfo
        self.ipn = contractor.ipn
        self.certificate_number = contractor.certificate_number
        self.address = contractor.address
        self.settlement_account = contractor.settlement_account
        self.phone = contractor.phone
        self.email = contractor.email
        self.work_reason = contractor.work_reason
        self.statute_copy = contractor.statute_copy


class Coordination(CoreBase):
    subject = models.TextField(verbose_name='Особа')
    status = models.BooleanField(default=False, verbose_name="Статус погодження (Так/Ні)")
    start = models.DateField(verbose_name="Початок погодження")
    end = models.DateField(verbose_name="Кінець погодження")
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name_plural = u'Погодження договорів'
        verbose_name = u'Погодження договору'

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return '{0} {1}'.format(str(self.subject), str(self.status))


class ContractFinance(CoreBase):
    """Містить загальну інформацію про фінансову частину договорів"""
    contract = models.OneToOneField('Contract', editable=False,
                                    on_delete=models.CASCADE, verbose_name="Договір")
    last_date_accrual = models.DateField(null=True, verbose_name="Дата останніх нарахувань")
    total_size_accrual = models.FloatField(default=0, verbose_name="Розмір нарахувань (Загальний)")
    last_date_pay = models.DateField(null=True, verbose_name="Дата останніх нарахувань")
    total_size_pay = models.FloatField(default=0, verbose_name="Розмір нарахувань (Загальний)")
    total_balance = models.FloatField(default=0, verbose_name="Баланс")

    class Meta:
        verbose_name_plural = u'Баланс по договорах'
        verbose_name = u'Баланс по договору'

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return 'Баланс по договору {0}'.format(self.contract or '-')

    def get_total_size_accrual(self):
        if self.contract:
            return self.contract.registeraccrual_set.all().aggregate(Sum('size_accrual'))['size_accrual__sum'] or 0

    def get_total_size_pay(self):
        if self.contract:
            return self.contract.registerpayment_set.all().aggregate(Sum('sum_payment'))['sum_payment__sum'] or 0

    def get_last_accrual_date(self):
        if self.contract:
            accruals = RegisterAccrual.objects.filter(contract=self.contract).order_by('-date_accrual')
            if accruals.count() > 0:
                return accruals[0].date_accrual

    def get_total_balance(self):
        if self.contract:
            return ((self.total_size_pay or 0.00) - (self.total_size_accrual or 0.00))

    def set_finance_values(self):

        self.total_size_accrual = self.get_total_size_accrual()
        self.total_size_pay = self.get_total_size_pay()
        self.total_balance = self.get_total_balance()
        self.last_date_accrual = self.get_last_accrual_date()


class RegisterAccrual(CoreBase):
    """ Реєстр нарахувань (Рахунків) """
    SUBSCRIPTION = 'subscription'
    SERVICE = 'service'
    ACCRUAL_TYPES = [[SUBSCRIPTION, 'Абонплата'], [SERVICE, 'Послуги']]
    title = models.CharField(verbose_name='Заголовок рахунку', max_length=150, null=True)
    accrual_type = models.CharField(verbose_name='Тип рахунку', choices=ACCRUAL_TYPES, max_length=150, null=True)
    contract = models.ForeignKey('Contract', on_delete=models.CASCADE, verbose_name="Договір")
    date_start_period = models.DateField(null=True, verbose_name="Початок періоду")
    date_end_period = models.DateField(null=True, verbose_name="Кінець періоду")
    date_accrual = models.DateField(null=True, verbose_name="Дата нарахувань")
    mb_size = models.FloatField(null=True, verbose_name="Кількість мегабайт (фактично)")
    mb_size_tariff = models.FloatField(null=True, verbose_name="Кількість мегабайт в тарифі")
    mb_size_over_tariff = models.FloatField(null=True, verbose_name="Кількість мегабайт понад тариф")
    size_accrual = models.FloatField(null=True, verbose_name="Розмір нарахувань")
    pay_size = models.FloatField(null=True, verbose_name="Сума до сплати")
    balance = models.FloatField(null=True, verbose_name="Баланс на поточний період")
    penalty = models.FloatField(null=True, verbose_name="Пеня за попередній період")
    accrual_docx = models.FileField(upload_to='uploads/accrual_docx/%Y/%m/%d/', null=True,
                                    verbose_name="Проект Рахунку")
    date_sending_doc = models.DateField(verbose_name="Дата відправлення акту", null=True)
    is_doc_send_successful = models.BooleanField(verbose_name="Акт успішно відправлено?", null=True)

    class Meta:
        verbose_name_plural = u'Нарахування'
        verbose_name = u'Нарахування'

    @classmethod
    def calculate_penalty(cls, balance, delay):
        if balance > 0:
            return 0

        if delay < 1:
            return 0

        balance = balance * -1
        p1 = balance * 0.03
        p2 = (balance * 0.001) * delay
        p3 = balance * 0.07 if delay > 30 else 0
        return p1 + p2 + p3

    @classmethod
    def calculate_accruals(cls, contract: Contract = None, start_date=None, end_date=None, create_pdf=None) -> List:
        if contract.status != CONTRACT_STATUS_ACTUAL:
            raise ValidationError({'non_field_errors': 'Нарахування можливо здійснити лише по "Укладеному" договору'})

        cls.calculate_non_regular_accrual(contract)
        ## Перевіряємо чи це є договір на одноразову послугу, якщо так не здійснюємо нарахування абонплати
        if contract.one_time_service:
            return []

        res = cls.calculate_regular_accruals(contract=contract, start_date=start_date, end_date=end_date,
                                             create_pdf=create_pdf)
        return res

    @classmethod
    def calculate_non_regular_accrual(cls, contract):
        """ Розраховує нарахування для одноразових послуг (підключення, встановлення кріптоавтографа і тд)"""
        logger.debug('RUN: calculate_non_regular_accrual')
        ##pay_periods = contract.get_pay_periods()
        ##period = pay_periods[0]
        ##start_date = period.get('start_date')
        start_date = contract.start_date

        total_price_pdv = contract.get_contract_product_price()
        if total_price_pdv > 0:
            if cls.objects.filter(contract=contract).count() > 0:
                return {'message': 'accrual alredy exist'}
            accrual = cls(contract=contract,
                          title='Послуги',
                          accrual_type=RegisterAccrual.SERVICE,
                          date_start_period=start_date,
                          date_end_period=start_date,
                          size_accrual=total_price_pdv,
                          date_accrual=start_date,
                          balance=-total_price_pdv,
                          pay_size=total_price_pdv,
                          penalty=0.00)
            accrual.save()
            ## Одноразові послуги чи товари
            contract_products = ContractProducts.objects.filter(contract=contract)
            for contract_product in contract_products:
                accrual_product = AccrualProducts(accrual=accrual, product=contract_product.product,
                                                  count=contract_product.count, price=contract_product.price,
                                                  total_price=contract_product.total_price, pdv=contract_product.pdv,
                                                  total_price_pdv=contract_product.total_price_pdv)
                accrual_product.save()
                logger.info(accrual_product)
            ## Одноразові послуги чи товари
            accrual.set_docx(save=True)
            ##accrual.save()
            ## Створення АКТУ ВИКОНАНИХ ПОСЛУГ
            number_act = u"Акт №{}-{} до договору № {}".format(accrual.date_accrual.strftime("%m"), accrual.pk,
                                                               accrual.contract.number_contract)
            act = RegisterAct(number_act=number_act, accrual=accrual, contract=accrual.contract,
                              date_formation_act=accrual.date_accrual)
            act.save()
            act.generate_act_docs()
            ## Створення АКТУ ВИКОНАНИХ ПОСЛУГ

    @classmethod
    def calculate_end_date(cls):
        now = datetime.today()
        month = now.month
        year = now.year
        last_day_of_month = calendar.monthrange(year, month)[1]
        _end_date = date(year, month, last_day_of_month)
        return _end_date

    @classmethod
    def calculate_regular_accruals(cls, contract: Contract = None, start_date=None, end_date=None, create_pdf=None):
        logging.debug(f'START REGULAR ACCRUAL')
        res = []

        end_date = end_date or cls.calculate_end_date()

        pay_periods = contract.get_pay_periods(end_date=end_date)

        logger.debug(f'Pay_periods: {pay_periods}')
        n = 0
        for period in pay_periods:
            charging_date = date(period.get('start_date').year, period.get('start_date').month, CHARGING_DATE)
            ## Перевіряємо чи не здійснювались нарахування на період
            q = cls.objects.filter(date_start_period=period.get('start_date'), date_end_period=period.get('end_date'),
                                   contract=contract).values('id')
            # Якщо нарахування здійснювались пропускаємо на цій ітерації
            if q.exists():
                continue

            ## ... Отримуємо платежі за попередній період з нарахуваннями
            last_period_q = cls.objects.filter(date_start_period__lte=period.get('start_date'),
                                               contract=contract).order_by('-date_start_period').values('size_accrual',
                                                                                                        'date_start_period',
                                                                                                        'balance')
            if last_period_q.exists():
                ## Якщо нарахування за перод уже здіснювались - отримуємо станнє нарахування
                last_period_latest_accrual = last_period_q.first()
                logger.debug(f' Last period date: {last_period_latest_accrual.get("date_start_period")}')
                logger.debug(f' Last period balanse: {last_period_latest_accrual.get("balance")}')
                balance_by_last_period = last_period_latest_accrual.get("balance")
                ## Отримаємо баланс по договору за останнє нарахування
            else:
                balance_by_last_period = (last_period_q.aggregate(Sum('size_accrual'))[
                                              'size_accrual__sum'] or 0) * -1 or 0
                ## Отримаємо баланс за весь період

            payments = RegisterPayment.objects.filter(contract=contract, payment_date__lte=period.get('end_date'),
                                                      payment_date__gte=period.get('start_date')).aggregate(
                Sum('sum_payment'))['sum_payment__sum'] or 0
            ## Порівнюємо платежі за попередній період з нарахуваннями ...
            price_by_month, price_contract = contract.get_price_from_details(charging_date)
            balance = balance_by_last_period + payments - price_by_month
            logger.debug(f'Balance: {balance}')
            logger.debug(f'Iteration: {n}')

            pay_size = balance * -1 if balance < 0 else 0
            logger.debug(f'Pay size: {pay_size}')
            ###

            accrual = cls(contract=contract,
                          title='Абонплата',
                          accrual_type=RegisterAccrual.SUBSCRIPTION,
                          date_start_period=period.get('start_date'),
                          date_end_period=period.get('end_date'),
                          size_accrual=price_by_month,
                          date_accrual=charging_date,
                          balance=balance,
                          pay_size=pay_size,
                          penalty=0)
            accrual.save()

            actual_contract_subscriptions = ContractSubscription.objects.actual_on_date(charging_date).filter(
                contract=contract)
            for contract_subscription in actual_contract_subscriptions:
                AccrualSubscription.objects.create(accrual=accrual,
                                                   charging_day=contract_subscription.charging_day,
                                                   start_period=period.get('start_date'),
                                                   end_period=period.get('end_date'),
                                                   product=contract_subscription.product,
                                                   count=contract_subscription.count,
                                                   price=contract_subscription.price,
                                                   total_price=contract_subscription.total_price,
                                                   pdv=contract_subscription.pdv,
                                                   total_price_pdv=contract_subscription.total_price_pdv)

            ##
            async_create_accrual_doc.delay(accrual.id)
            ## Створення АКТУ ВИКОНАНИХ ПОСЛУГ

            number_act = u"Акт №{} до договору № {}".format(accrual.date_accrual.strftime("%m"),
                                                            accrual.contract.number_contract)
            act = RegisterAct(number_act=number_act, accrual=accrual, contract=accrual.contract,
                              date_formation_act=accrual.date_accrual)
            act.save()
            async_create_act_doc.delay(act.id)
            ## Створення АКТУ ВИКОНАНИХ ПОСЛУГ
            res.append({'period': period, 'status': 'success', 'size_accrual': price_by_month})
            n += 1
        return res

    def generate_docx_invoice(self, doc=None):
        """ Return *.docx path from MEDIA_ROOT """
        logger.debug(' start function "generate_docx_invoice"')
        if not doc:
            template_obj = TemplateDocument.objects.get(related_model_name='registerinvoice')
            docx_template = template_obj.template_file.path
            doc = docxtpl.DocxTemplate(docx_template)

        upload_to = datetime.today().strftime('uploads/accrual_docx/%Y/%m/%d/')
        base_dir = os.path.join(MEDIA_ROOT, upload_to)
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)
        filename = get_random_string(length=32) + '.docx'
        out_path = os.path.join(base_dir, filename)

        ret = os.path.join(upload_to, filename)

        data = self.get_invoice_data()
        logger.debug(' end function "generate_docx_invoice"')
        doc.render(data)
        doc.save(out_path)
        return ret

    def get_reg_number(self):
        return f'РФ-{self.id}'

    def get_invoice_data(self):
        logger.debug('start function "get_invoice_data"')
        data = {}
        contract = self.contract
        data['number_contract'] = str(contract.number_contract)
        data['reg_number'] = self.get_reg_number()
        local_contract_date = format_datetime(contract.start_date, "«d» MMMM Y", locale='uk_UA')
        data['local_contract_date'] = local_contract_date
        data['subject_contract'] = contract.subject_contract
        data['price_contract_by_month'] = float(self.size_accrual or 0.00)
        price_contract_by_month_locale = num2words(self.size_accrual + 0.00, lang='uk', to='currency',
                                                   currency='UAH')
        data['price_contract_by_month_locale'] = price_contract_by_month_locale
        data['total_price'] = self.size_accrual
        data['pdv'] = get_pdv(self.size_accrual)
        data['total_price_no_pdv'] = round(self.size_accrual - data['pdv'], 2)
        data['debt'] = round(self.balance + self.size_accrual, 2)
        data['price_locale'] = num2words(data['total_price'] + 0.00, lang='uk', to='currency',
                                         currency='UAH')
        data['act_date_locale'] = format_datetime(self.date_accrual, "«d» MMMM Y", locale='uk_UA')
        local_month_name = LOCAL_MONTH[self.date_accrual.month]
        data['spatial_date'] = '{} {}'.format(local_month_name, self.date_accrual.year)
        stage_property_q = StageProperty.objects.filter(contract=contract)
        if stage_property_q.count() > 0:
            stage_property = stage_property_q[0]
            stage_property_data = {'name': stage_property.name,
                                   'address': stage_property.address,
                                   'bank_name': stage_property.bank_name,
                                   'settlement_account': stage_property.settlement_account,
                                   'certificate_number': stage_property.certificate_number,
                                   'mfo': stage_property.mfo,
                                   'edrpou': stage_property.edrpou,
                                   'phone': stage_property.phone
                                   }
        else:
            stage_property_data = None

        data['stage_property_data'] = stage_property_data
        details_1 = AccrualProducts.objects.filter(accrual=self).values('product', 'product__name', 'count', 'price',
                                                                        'pdv', 'total_price', 'total_price_pdv')
        details_2 = AccrualSubscription.objects.filter(accrual=self).values('product', 'product__name', 'count',
                                                                            'price', 'pdv', 'total_price',
                                                                            'total_price_pdv', 'start_period',
                                                                            'end_period')
        data['details'] = list(details_1) + list(details_2)
        logger.debug(' end function "get_invoice_data"')
        return data

    def set_docx(self, save=None):
        self.accrual_docx.name = self.generate_docx_invoice()
        if save:
            self.save()

    def save(self, *args, **kwargs):
        super(RegisterAccrual, self).save()

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return 'Нарахування у розмірі {0} до договору {1}'.format(self.size_accrual or '0', self.contract.__str__())


class RegisterPayment(CoreBase):
    PAYMENT_CHOICES = [['import', 'Клієнт-банк'],
                       ['handly', 'Вручну'], ]
    contract = models.ForeignKey('Contract',
                                 on_delete=models.CASCADE, verbose_name="Договір")
    payment_date = models.DateField(null=True, verbose_name="Дата оплати")
    outer_doc_number = models.CharField(max_length=100, null=True,
                                        verbose_name='Зовнішній номер документа платежу')
    act = models.ForeignKey('RegisterAct', related_name='payments',
                            null=True, blank=True, editable=False,
                            on_delete=models.CASCADE, verbose_name="Акт")
    payment_type = models.CharField(default=PAYMENT_CHOICES[1][0], max_length=100, choices=PAYMENT_CHOICES)
    sum_payment = models.IntegerField(null=True, verbose_name="Число")
    importer = models.ForeignKey('contracts.ImportPayment', on_delete=models.CASCADE, null=True,
                                 verbose_name='Назва завантаження')

    class Meta:
        verbose_name_plural = u'Платежі'
        verbose_name = u'Платіж'

    def __str__(self):
        return self.__unicode__()

    def get_pay_date(self):
        if self.payment_date:
            return self.payment_date.strftime("%m/%d/%Y")
        else:
            return '<не вказано>'

    def __unicode__(self):
        return u'платіж у розмірі {0} від {1} "{2}"'.format(self.sum_payment or '0', self.get_pay_date(),
                                                            self.contract.contractor)


class RegisterAct(CoreBase):
    number_act = models.TextField(verbose_name="Номер акту")
    contract = models.ForeignKey('Contract', on_delete=models.CASCADE, verbose_name="Договір")
    accrual = models.ForeignKey('RegisterAccrual', null=True, blank=True, editable=False,
                                on_delete=models.CASCADE, verbose_name="Нарахування")
    date_formation_act = models.DateField(verbose_name="Дата формування акту")
    date_sending_act = models.DateField(verbose_name="Дата відправлення акту", null=True)
    is_send_successful = models.BooleanField(verbose_name="Акт успішно відправлено?", null=True)
    date_return_act = models.DateField(verbose_name="Дата повернення акту", null=True, )
    copy_act = models.FileField(null=True, upload_to='uploads/docx_act/%Y/%m/%d/', verbose_name="Копія акту(DOCX)")
    copy_act_pdf = models.FileField(null=True, upload_to='uploads/pdf_act/%Y/%m/%d/', verbose_name="Копія акту(PDF)")
    sign_act_from_contractor = models.TextField(null=True, verbose_name="Цифровий підпис контрагента",
                                                help_text="Підписант може накласти цифровий підпис на копію акту в пдф")
    copy_act_from_contractor = models.FileField(null=True, upload_to='uploads/pdf_act_stamp/%Y/%m/%d/',
                                                verbose_name="Копія акту підписана контрагентом",
                                                help_text="Повинна містити скановану копію з штампом організації підписанта")

    class Meta:
        verbose_name_plural = u'Акти'
        verbose_name = u'Акт'

    def save(self, *args, **kwargs):
        super(RegisterAct, self).save(*args, **kwargs)

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return u'{}'.format(self.number_act or '-')

    @classmethod
    def generate_acts(cls, regenerate_all=None):
        template_obj = TemplateDocument.objects.get(related_model_name='registeract')
        docx_template = template_obj.template_file.path
        doc = docxtpl.DocxTemplate(docx_template)
        res = []
        if regenerate_all:
            acts = cls.objects.all()
        else:
            acts = cls.objects.filter(copy_act__exact=None)
        for act in acts:
            act_docx_file = act.generate_docx_act(doc=doc)
            act.copy_act.name = act_docx_file
            act_pdf_file = act.convert_docx_to_pdf()
            act.copy_act_pdf.name = act_pdf_file
            act.save()
            res.append(str(act))

        return res

    def generate_act_docs(self):
        act_docx_file = self.generate_docx_act()
        self.copy_act.name = act_docx_file
        ##act_pdf_file = self.convert_docx_to_pdf()
        ##self.copy_act_pdf.name = act_pdf_file
        self.save()
        return {'copy_act': self.copy_act.name}  # , 'copy_act_pdf': self.copy_act_pdf.name}

    def generate_docx_act(self, doc=None):
        """ Return *.docx path from MEDIA_ROOT """
        logger.debug(' start function "generate_docx_act"')
        if not doc:
            template_obj = TemplateDocument.objects.get(related_model_name='registeract')
            docx_template = template_obj.template_file.path
            doc = docxtpl.DocxTemplate(docx_template)

        upload_to = datetime.today().strftime('uploads/docx_act/%Y/%m/%d/')
        base_dir = os.path.join(MEDIA_ROOT, upload_to)
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)
        filename = get_random_string(length=32) + '.docx'
        out_path = os.path.join(base_dir, filename)

        ret = os.path.join(upload_to, filename)

        data = self.get_act_data()
        logger.debug(' end function "generate_docx_act"')
        doc.render(data)
        doc.save(out_path)
        return ret

    def get_act_data(self):
        logger.debug('start function "get_act_data"')
        data = {}
        contract = self.contract
        data['number_contract'] = str(contract.number_contract)
        local_contract_date = format_datetime(contract.start_date, "«d» MMMM Y", locale='uk_UA')
        data['local_contract_date'] = local_contract_date
        data['subject_contract'] = contract.subject_contract
        data['price_contract_by_month'] = float(self.accrual.size_accrual or 0.00)
        price_contract_by_month_locale = num2words(self.accrual.size_accrual + 0.00, lang='uk', to='currency',
                                                   currency='UAH')
        data['price_contract_by_month_locale'] = price_contract_by_month_locale

        pdv = round(self.accrual.size_accrual / 120 * 20, 2)  ## розмір пдв
        data['pdv'] = pdv
        pdv_locale = num2words(pdv + 0.00, lang='uk', to='currency',
                               currency='UAH')
        data['pdv_locale'] = pdv_locale
        data['price'] = round(self.accrual.size_accrual - pdv, 2)
        data['price_locale'] = num2words(data['price'] + 0.00, lang='uk', to='currency',
                                         currency='UAH')

        data['act_date_locale'] = format_datetime(self.date_formation_act, "«d» MMMM Y", locale='uk_UA')

        local_month_name = LOCAL_MONTH[self.date_formation_act.month]

        data['spatial_date'] = '{} {}'.format(local_month_name, self.date_formation_act.year)

        stage_property_q = StageProperty.objects.filter(contract=contract)
        if stage_property_q.count() > 0:
            stage_property = stage_property_q[0]
            stage_property_data = {'name': stage_property.name,
                                   'address': stage_property.address,
                                   'bank_name': stage_property.bank_name,
                                   'settlement_account': stage_property.settlement_account,
                                   'certificate_number': stage_property.certificate_number,
                                   'mfo': stage_property.mfo,
                                   'edrpou': stage_property.edrpou,
                                   'phone': stage_property.phone
                                   }

        else:
            stage_property_data = None

        data['stage_property_data'] = stage_property_data
        details_1 = AccrualProducts.objects.filter(accrual=self.accrual).values('product', 'product__name', 'count',
                                                                                'price', 'pdv', 'total_price',
                                                                                'total_price_pdv')
        details_2 = AccrualSubscription.objects.filter(accrual=self.accrual).values('product', 'product__name', 'count',
                                                                                    'price', 'pdv', 'total_price',
                                                                                    'total_price_pdv', 'start_period',
                                                                                    'end_period')
        data['details'] = list(details_1) + list(details_2)
        logger.debug(' end function "get_act_data"')
        return data

    def convert_docx_to_pdf(self, save=None):
        """ Return *.pdf path from MEDIA_ROOT """
        upload_to = datetime.today().strftime('uploads/pdf_act/%Y/%m/%d/')
        source = self.copy_act.path
        # print('source:',source)
        out_path = os.path.join(MEDIA_ROOT, upload_to)
        filename = os.path.basename(source).replace('.docx', '.pdf')
        ret = os.path.join(upload_to, filename)
        # print('ret:', ret)
        out_file = os.path.join(out_path, filename)
        # print('out_file:', out_file)
        LibreOfficeConverter.convert_to_pdf(source, out_file)
        if save:
            self.copy_act_pdf.name = ret
            self.save()
        return ret

    def send_act(self):
        ##TODO
        ##1. Отримати пошту контрагента
        ##2. Сформувати акт (generate_act)
        ##3. Перегнати акт з docx в pdf
        ##3. Відправити акт по пошті
        ##4. Якщо відправлено успішно змінюємо статус акту
        pass


class TariffChange(CoreBase):
    start_date = models.DateField(verbose_name='Дата початку дії договору', editable=False)
    tariff_plan = models.ForeignKey('Subscription', on_delete=models.PROTECT,
                                    verbose_name="Тарифний план")
    contract = models.ForeignKey('Contract', on_delete=models.PROTECT,
                                 verbose_name="Договір")

    class Meta:
        verbose_name_plural = u'Зміна тарифного плану'
        verbose_name = u'Зміна тарифного плану'

    def save(self, *args, **kwargs):
        if not self.id:
            self.set_start_date()
        super(TariffChange, self).save()

    def set_start_date(self):
        """ Дата початку дії зміни тарифу визначається з першого числа наступного місяця після подачі заяви """
        next_month = self.date_add + relativedelta(months=+1)
        self.start_date = date(next_month.year, next_month.month, 1)

    def get_count(self):
        contract_subscription = ContractSubscription.objects.get(contract=self.contract, product=self.tariff_plan)
        return contract_subscription.count

    def change_contract_subscription(self):
        count = self.get_count()
        ContractSubscription.objects.create(contract=self,
                                            product=self.tariff_plan,
                                            start_period=self.start_date,
                                            end_period=self.contract.expiration_date,
                                            count=count,
                                            price=self.tariff_plan,
                                            total_price=count * self.tariff_plan.price,
                                            pdv=self.tariff_plan.pdv,
                                            total_price_pdv=count * self.tariff_plan.price_pdv,
                                            charging_day=CHARGING_DATE)
