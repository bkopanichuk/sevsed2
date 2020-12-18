from django import forms
from django.contrib import admin
from django_json_widget.widgets import JSONEditorWidget
from .admin_actions import copy_settings

from .models import ClientFormSettings, ClientFormElementSettings


class YourForm(forms.ModelForm):
    class Meta:
        model = ClientFormElementSettings
        fields = ['client_form', 'name', 'values', 'visible', 'enabled','title']
        widgets = {
            'values': JSONEditorWidget
        }
        ##filter_horizontal = ('permissions',)


@admin.register(ClientFormElementSettings)
class ClientFormElementSettingsAdmin(admin.ModelAdmin):
    form = YourForm
    # formfield_overrides = {
    #     fields.JSONField: {'widget': JSONEditorWidget},
    # }
    ##filter_horizontal = ('permissions',)


class ClientFormElementSettingsInline(admin.TabularInline):
    model = ClientFormElementSettings
    fields = ['title','client_form', 'name', 'values', 'visible', 'enabled']
    ##filter_horizontal = ('permissions',)
    show_change_link = True
    min_num = 0
    max_num = 50
    extra = 0


@admin.register(ClientFormSettings)
class ClientFormSettingsAdmin(admin.ModelAdmin):
    list_display = ['role', 'form_name', 'active']
    actions = [copy_settings, ]

    inlines = [
        ClientFormElementSettingsInline
    ]
