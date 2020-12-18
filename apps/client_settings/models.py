# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import Permission, Group
from django.contrib.gis.db import models


class ClientFormSettings(models.Model):
    role = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=False, verbose_name='Група доступу')
    active = models.BooleanField(default=False, verbose_name='Ознака використання компоненту')
    form_name = models.CharField(max_length=250, verbose_name='Код компоненту елементу')
    title = models.CharField(max_length=250, verbose_name='Назва компоненту елементу', null=True)

    class Meta:
        verbose_name = "Компонент"
        unique_together = [['role', 'active', 'form_name']]
        ordering = ['role', 'form_name']

    def __str__(self):
        return f'{self.role} - {self.form_name}'


class ClientFormElementSettings(models.Model):
    client_form = models.ForeignKey(ClientFormSettings, on_delete=models.CASCADE, related_name='elements')
    name = models.CharField(max_length=100, verbose_name='Ідентифікатор програмного елементу')
    title = models.CharField(max_length=250, verbose_name='Назва програмного елементу', null=True)
    values = models.JSONField(default=["PROJECT", ], verbose_name='Значення', null=True, blank=True)
    permissions = models.ManyToManyField(Permission, null=True, blank=True)
    visible = models.BooleanField(default=True, verbose_name='Видимість компонента')
    enabled = models.BooleanField(default=True, verbose_name='Доступність для вводу')

    class Meta:
        verbose_name = "Видимість та доступність елементів компонента"
        unique_together = [['client_form', 'name', 'visible', 'enabled', 'values']]

    def __str__(self):
        return f'{self.client_form}- {self.name}'
