from __future__ import unicode_literals
from django_filters import rest_framework as filters
from collections import OrderedDict
from rest_framework.request import Request
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.document.models.document_additional_file_model import DocumentFile
from apps.document.api.srializers.document_file_serializer import DocumentFileSerializer
from apps.l_core.api.base.serializers import BaseOrganizationViewSetMixing


class DocumentFileViewSet(BaseOrganizationViewSetMixing):
    queryset = DocumentFile.objects.all()
    serializer_class = DocumentFileSerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter, OrderingFilter)

    def get_queryset(self):
        q = super(DocumentFileViewSet, self).get_queryset()
        return q.filter(document__id=self.document_id)

    def list(self, request, document_id, *args, **kwargs):
        self.document_id = int(document_id)
        return super(DocumentFileViewSet, self).list(request, *args, **kwargs)

    def create(self, request: Request, document_id, *args, **kwargs):
        if isinstance(request.data, OrderedDict):
            setattr(request.data, '_mutable', True)
        self.document_id = int(document_id)
        request.data['document'] = self.document_id
        return super(DocumentFileViewSet, self).create(request, *args, **kwargs)

    def destroy(self, request, document_id, *args, pk=None, **kwargs):
        if isinstance(request.data, OrderedDict):
            setattr(request.data, '_mutable', True)
        self.document_id = int(document_id)
        request.data['document'] = self.document_id
        return super(DocumentFileViewSet, self).destroy(request, *args, pk=None, **kwargs)

    def retrieve(self, request, document_id, *args, **kwargs):
        if isinstance(request.data, OrderedDict):
            setattr(request.data, '_mutable', True)
        self.document_id = int(document_id)
        request.data['document'] = self.document_id
        return super(DocumentFileViewSet, self).retrieve(request, *args, **kwargs)

##-------------------------------------------------------------
