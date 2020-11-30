# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import Permission
from django.contrib.gis.db import models


class ClientFormSettings(models.Model):
    ROLE_CHOICES = (
        ('REGISTRATOR', 'Реєстратор'),
        ('EXECUTOR', 'Виконавець')
    )
    role = models.CharField(choices=ROLE_CHOICES, max_length=100)
    active = models.BooleanField(default=False)
    form_name = models.CharField(max_length=250)

    class Meta:
        unique_together = [['role', 'active', 'form_name']]


class ClientFormElementSettings(models.Model):
    client_form = models.ForeignKey(ClientFormSettings, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=100)
    permissions = models.ManyToManyField(Permission, null=True,blank=True)

    class Meta:
        unique_together = [['client_form', 'name']]
