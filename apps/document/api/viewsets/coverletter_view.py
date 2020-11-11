from __future__ import unicode_literals
from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.document.api.srializers import DocumentSerializer
from apps.document.models.coverletter_model import CoverLetter


class CoverLetterSerializerViewSet(viewsets.ModelViewSet):
    queryset = CoverLetter.objects
    serializer_class = DocumentSerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter, OrderingFilter)