from django.db import models
from simple_history.models import HistoricalRecords

from apps.l_core.models import AbstractCoreOrganization, ComplexBaseMixin


class StageProperty(AbstractCoreOrganization, ComplexBaseMixin):
    """"""
    contract = models.OneToOneField('Contract',
                                    on_delete=models.CASCADE, verbose_name="Договір")
    edrpou = models.CharField(max_length=50, blank=True, null=True,  verbose_name="ЄДРПОУ")
    history = HistoricalRecords()

    class Meta:
        unique_together = [['contract', 'edrpou']]
        verbose_name_plural = u'Реквізити договорів'
        verbose_name = u'Реквізити договору'

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return 'Реквізити {0}'.format(str(self.contract) or '-')