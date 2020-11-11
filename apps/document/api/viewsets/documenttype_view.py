from __future__ import unicode_literals

from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.document.api.srializers.documenttype_serializer import IncomingDocumentTypeSerializer, \
    OutgoingDocumentTypeSerializer
from apps.document.models.documenttype_model import IncomingDocumentType, OutgoingDocumentType
from apps.l_core.api.base.serializers import BaseViewSetMixing


class IncomingDocumentTypeSerializerViewSet(BaseViewSetMixing):
    queryset = IncomingDocumentType.objects.all()
    serializer_class = IncomingDocumentTypeSerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter, OrderingFilter)

    def get_queryset(self):
        return self.queryset


class OutgoingDocumentTypeSerializerViewSet(BaseViewSetMixing):
    queryset = OutgoingDocumentType.objects.all()
    serializer_class = OutgoingDocumentTypeSerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter, OrderingFilter)

    def get_queryset(self):
        return self.queryset
