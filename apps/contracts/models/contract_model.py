import calendar
from datetime import date
from datetime import datetime

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Sum
from django.utils.timezone import now
from simple_history.models import HistoricalRecords

from apps.contracts.models.contract_constants import CONTRACT_STATUS
from apps.contracts.models.contract_product_model import ContractProducts, ContractSubscription
from apps.l_core.models import CoreBase
from apps.l_core.models import Counter
from .dict_model import Subscription

MEDIA_ROOT = settings.MEDIA_ROOT

import logging

logger = logging.getLogger(__name__)

############################################################
def copy_contract_directory_path(instance, filename):
    return 'uploads/org_{0}/contract/{1}/copy_contract/{2}'.format(instance.contract.organization.id,
                                                                    instance.contract.unique_uuid, filename)

def contract_docx_directory_path(instance, filename):
    return 'uploads/org_{0}/contract/{1}/contract_docx/{2}'.format(instance.contract.organization.id,
                                                                    instance.contract.unique_uuid, filename)

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
    copy_contract = models.FileField(upload_to=copy_contract_directory_path, null=True,
                                     verbose_name="Копія договору")
    contract_docx = models.FileField(upload_to=contract_docx_directory_path, null=True,
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



    def calculate_accrual(self):
        from apps.contracts.models.register_accrual_model import RegisterAccrual
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


