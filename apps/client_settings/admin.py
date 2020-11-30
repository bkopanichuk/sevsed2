from django.contrib import admin

from simple_history.admin import SimpleHistoryAdmin
from .models import ClientFormSettings,ClientFormElementSettings


class ClientFormElementSettingsInline(admin.TabularInline):
    model = ClientFormElementSettings
    show_change_link = True
    min_num = 0
    max_num = 50
    extra = 0

@admin.register(ClientFormSettings)
class ClientFormSettingsAdmin(SimpleHistoryAdmin):
    list_display = ['role', 'form_name','active']
    inlines = [
        ClientFormElementSettingsInline
    ]
