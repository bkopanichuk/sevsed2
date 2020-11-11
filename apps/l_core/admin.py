from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CoreUser,CoreOrganization,GroupOrganization


admin.site.register(CoreUser, UserAdmin)


@admin.register(CoreOrganization)
class CoreOrganizationAdmin(admin.ModelAdmin):
    pass





@admin.register(GroupOrganization)
class GroupOrganizationAdmin(admin.ModelAdmin):
    pass
