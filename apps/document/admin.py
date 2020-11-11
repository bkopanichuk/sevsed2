from django.contrib import admin

from simple_history.admin import SimpleHistoryAdmin

from apps.document.models.coverletter_model import CoverLetter
from apps.document.models.document_model import BaseDocument
from apps.document.models.documenttype_model import IncomingDocumentType,OutgoingDocumentType
from apps.document.models.sign_model import Sign
from apps.document.models.task_model import Task
#
#
# class DocumentResolutionInline(admin.TabularInline):
#     model = Task
#     show_change_link = True
#     min_num = 0
#     max_num = 50
#     extra = 0
#
#
# class SignInline(admin.TabularInline):
#     model = Sign
#     show_change_link = True
#     min_num = 0
#     max_num = 50
#     extra = 0
#
#
# @admin.register(BaseDocument)
# class DocumentAdmin(SimpleHistoryAdmin):
#     list_display = ['reg_number', 'incoming_type']
#     search_fields = ['reg_number', ]
#     list_filter = ['incoming_type', ]
#     readonly_fields = ['status', 'reg_number']
#     inlines = [
#         DocumentResolutionInline,
#         SignInline
#     ]

    # def get_queryset(self, request):
    #     #     org = request.user.organization
    #     #     q = super(DocumentAdmin, self).get_queryset(request)
    #     #     return q.filter(organization= org)

#
# @admin.register(IncomingDocumentType)
# class DocumentTypeAdmin(admin.ModelAdmin):
#     pass
#
#
# @admin.register(OutgoingDocumentType)
# class OutgoingDocumentTypeAdmin(admin.ModelAdmin):
#     pass
#
#
# @admin.register(CoverLetter)
# class CoverLetterAdmin(admin.ModelAdmin):
#     pass
#
#
# @admin.register(Task)
# class TaskAdmin(admin.ModelAdmin):
#     pass
#
#
# @admin.register(Sign)
# class SignAdmin(admin.ModelAdmin):
#     pass
