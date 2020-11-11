from django.db import models


class DocumentManager(models.Manager):

    def __init__(self, document_status=None, *args, **kwargs):

        super(DocumentManager, self).__init__(*args, **kwargs)
        self.document_status = document_status

    def get_queryset(self):
        base_queryset = super(DocumentManager, self).get_queryset()
        return base_queryset.filter(status=self.document_status)

class TaskManager(models.Manager):

    def __init__(self, document_status=None, *args, **kwargs):

        super(DocumentManager, self).__init__(*args, **kwargs)
        self.document_status = document_status

    def get_queryset(self):
        base_queryset = super(DocumentManager, self).get_queryset()
        return base_queryset.filter(status=self.document_status)