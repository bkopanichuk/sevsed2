from django.db import models
from simple_history.models import HistoricalRecords

from apps.l_core.models import AbstractCoreOrganization, ComplexBaseMixin


class StageProperty(AbstractCoreOrganization, ComplexBaseMixin):
    """"""
    contract = models.OneToOneField('Contract',
                                    on_delete=models.CASCADE, verbose_name="Договір")
    history = HistoricalRecords()

    class Meta:
        verbose_name_plural = u'Реквізити договорів'
        verbose_name = u'Реквізити договору'

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return 'Реквізити {0}'.format(str(self.contract) or '-')