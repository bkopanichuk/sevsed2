from django.db import models

class ContractSubscriptionManager(models.Manager):

    def actual_on_date(self,  actual_date):
        return self.filter( start_period__lte=actual_date,
                           end_period__gte=actual_date,)



class ContractArchiveManager(models.Manager):
    pass
