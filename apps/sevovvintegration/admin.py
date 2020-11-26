from django.contrib import admin
from .models import SEVIncoming,SEVOutgoing

@admin.register(SEVIncoming)
class SEVIncomingAdmin(admin.ModelAdmin):
    list_display = ['from_org','to_org','date_add']

@admin.register(SEVOutgoing)
class SEVOutgoingAdmin(admin.ModelAdmin):
     list_display = ['message_id','from_org','to_org','date_add']
