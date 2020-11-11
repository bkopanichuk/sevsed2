# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework import serializers, viewsets

from atu.models import *


__all__=['ATURegionViewSet','ATUDistrictViewSet']


##ATURegion------------------------------------------------------
class ATURegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ATURegion
        fields = ('id','name','__str__')

# ViewSets define the view behavior.
class ATURegionViewSet(viewsets.ModelViewSet):
    queryset = ATURegion.objects.all()
    serializer_class = ATURegionSerializer
##-------------------------------------------------------------


##ATUDistrict------------------------------------------------------
class ATUDistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = ATUDistrict
        fields = ('id','name','__str__')

# ViewSets define the view behavior.
class ATUDistrictViewSet(viewsets.ModelViewSet):
    queryset = ATUDistrict.objects.all()
    serializer_class = ATUDistrictSerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_fields = ('region__id',)
##-------------------------------------------------------------
