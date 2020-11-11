from rest_framework.exceptions import PermissionDenied

from apps.document.models.document_constants import CustomDocumentPermissions
from apps.document.models.document_model import BaseDocument, ARCHIVED


class SendToArchive:
    def __init__(self, document, data, user):
        self.document: BaseDocument = document
        self.data = data
        self.user = user

    def run(self):
        self.check_user_permissions()
        self.send_to_archive()

    def check_user_permissions(self):
        if not self.user.has_perm(CustomDocumentPermissions.SEND_TO_ARCHIVE):
            raise PermissionDenied('Поточний користувач не має дозвому переміщати документи до архіву.')

    def send_to_archive(self):
        self.document.case_index = self.data.get('case_index')
        self.document.case_number = self.data.get('case_number')
        self.document.status = ARCHIVED
        self.document.save()