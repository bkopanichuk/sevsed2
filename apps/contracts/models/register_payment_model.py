from django.db import models

from apps.l_core.models import CoreBase
from apps.contracts.models.payment_model import ImportPayment


class RegisterPayment(CoreBase):
    PAYMENT_CHOICES = [['import', 'Клієнт-банк'],
                       ['handly', 'Вручну'], ]
    contract = models.ForeignKey('contracts.Contract',
                                 on_delete=models.CASCADE, verbose_name="Договір")
    payment_date = models.DateField(null=True, verbose_name="Дата оплати")
    outer_doc_number = models.CharField(max_length=100, null=True,
                                        verbose_name='Зовнішній номер документа платежу')
    act = models.ForeignKey('contracts.RegisterAct', related_name='payments',
                            null=True, blank=True, editable=False,
                            on_delete=models.CASCADE, verbose_name="Акт")
    payment_type = models.CharField(default=PAYMENT_CHOICES[1][0], max_length=100, choices=PAYMENT_CHOICES)
    sum_payment = models.IntegerField(null=True, verbose_name="Число")
    importer = models.ForeignKey(ImportPayment, on_delete=models.CASCADE, null=True,
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