from __future__ import unicode_literals
from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.document.api.srializers.sign_serializer import SignSerializer
from apps.document.models.sign_model import Sign


class SignSerializerViewSet(viewsets.ModelViewSet):
    queryset = Sign.objects
    serializer_class = SignSerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter, OrderingFilter)