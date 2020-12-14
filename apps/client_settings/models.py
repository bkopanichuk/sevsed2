# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import Permission, Group
from django.contrib.gis.db import models


class ClientFormSettings(models.Model):
    role = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=False)
    active = models.BooleanField(default=False)
    form_name = models.CharField(max_length=250)

    class Meta:
        unique_together = [['role', 'active', 'form_name']]

    def __str__(self):
        return f'{self.role} - {self.form_name}'


class ClientFormElementSettings(models.Model):
    client_form = models.ForeignKey(ClientFormSettings, on_delete=models.CASCADE, related_name='elements')
    name = models.CharField(max_length=100)
    values = models.JSONField(default="['default',]")
    permissions = models.ManyToManyField(Permission, null=True, blank=True)
    visible = models.BooleanField(default=True)
    disabled = models.BooleanField(default=False)

    class Meta:
        unique_together = [['client_form', 'name','visible','disabled','values']]

    def __str__(self):
        return f'{self.client_form}- {self.name}'
