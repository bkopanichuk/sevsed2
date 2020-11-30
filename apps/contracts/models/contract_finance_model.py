from django.db import models
from django.db.models import Sum


from apps.l_core.models import CoreBase


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
        from apps.contracts.models import RegisterAccrual
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