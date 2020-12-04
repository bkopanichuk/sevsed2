import calendar
import logging
import os
from datetime import datetime, date
from typing import List

import docxtpl
from babel.dates import format_datetime
from django.db import models
from django.db.models import Sum
from django.utils.crypto import get_random_string
from num2words import num2words
from rest_framework.exceptions import ValidationError
from django.conf import settings
from apps.contracts.models.contract_constants import CHARGING_DATE, CONTRACT_STATUS_ACTUAL
from apps.dict_register.models import TemplateDocument
from apps.contracts.models.contract_product_model import AccrualProducts, AccrualSubscription
from apps.contracts.tasks import async_create_accrual_doc, async_create_act_doc
from apps.l_core.models import CoreBase
from apps.l_core.utilits.finance import get_pdv
from apps.l_core.utilits.month import LOCAL_MONTH

MEDIA_ROOT = settings.MEDIA_ROOT

logger = logging.getLogger(__name__)


## TODO Перенести нарпхування в окремий сервіс

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
    def calculate_accruals(cls, contract, start_date=None, end_date=None, create_pdf=None) -> List:
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
        from apps.contracts.models.contract_product_model import ContractProducts
        from apps.contracts.models.register_act_model import RegisterAct
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
                          organization=contract.organization,
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
                                                  organization=accrual.organization,
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
            act = RegisterAct(number_act=number_act, organization=accrual.organization, accrual=accrual,
                              contract=accrual.contract,
                              date_formation_act=accrual.date_accrual)
            act.save()
            act.generate_act_docs()
            async_create_accrual_doc.delay(accrual.id)
            async_create_act_doc.delay(act.id)


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
    def calculate_regular_accruals(cls, contract, start_date=None, end_date=None, create_pdf=None):
        from apps.contracts.models.register_payment_model import RegisterPayment
        from apps.contracts.models.contract_product_model import ContractSubscription
        from apps.contracts.models.register_act_model import RegisterAct
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
                          organization=contract.organization,
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
                                                   organization = accrual.organization,
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
            act = RegisterAct(number_act=number_act, accrual=accrual, organization=accrual.organization, contract=accrual.contract,
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
            template_obj = TemplateDocument.objects.get(related_model_name='registerinvoice',
                                                        organization_id=self.organization.id)
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
        from apps.contracts.models.stage_propperty_model import StageProperty
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
