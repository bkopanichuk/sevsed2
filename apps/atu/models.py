

from django.contrib.gis.db import models




__all__ = ['ATURegion','ATUDistrict']



class ATURegion(models.Model):
    name = models.CharField(max_length=50, verbose_name=u'Область')
    class Meta:
        verbose_name_plural = u'Області'
        verbose_name = u'Область'

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return '{} область'.format(self.name)


class ATUDistrict(models.Model):
    name = models.CharField(max_length=50, verbose_name=u'Район')
    region = models.ForeignKey(ATURegion,  on_delete=models.PROTECT, verbose_name=u'Область',  related_name='atu_region_%(class)s')
    class Meta:
        verbose_name_plural = u'Райони'
        verbose_name = u'Район'

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return '{} район, {}'.format(self.name, str(self.region))