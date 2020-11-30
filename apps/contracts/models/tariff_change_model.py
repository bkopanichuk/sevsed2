from datetime import date

from dateutil.relativedelta import relativedelta
from django.db import models

from apps.contracts.models import ContractSubscription
from apps.contracts.models.contract_constants import CHARGING_DATE
from apps.l_core.models import CoreBase


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