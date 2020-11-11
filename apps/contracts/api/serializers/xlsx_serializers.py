from __future__ import unicode_literals
from rest_framework import serializers
from django_filters import rest_framework as filters

from rest_framework.filters import SearchFilter, OrderingFilter

from drf_renderer_xlsx.mixins import XLSXFileMixin
from ...models.contract_model import Contract
from apps.contracts.api.views.contract_views import ContractSerializerViewSet
from rest_framework.viewsets import ReadOnlyModelViewSet
from apps.l_core.api.base.serializers import BaseViewSetMixing
from collections import OrderedDict


CONTRACT_FIELD_TITLES =OrderedDict([('number_contract',"Номер договору"),
                                   ('contractor_name',"Контрагент"),
                                   ('start_date',"Початок договору"),
                                   ( 'expiration_date',"Закінчення договору"),
                                   ('price_contract_by_month',"Абонплата"),
                                   ('price_additional_services',"Плата за підключення"),
                                   ('price_contract',"Загальна вартість за період дії договору")])

class XLSXContractSerializer(serializers.ModelSerializer):
    contractor_name = serializers.SerializerMethodField()

    class Meta:
        model = Contract
        fields = [ key for key,value in  CONTRACT_FIELD_TITLES.items()]

    def get_contractor_name(self, obj):
        if obj.contractor:
            return obj.contractor.__str__()


# ViewSets define the view behavior.
class XLSXContractSerializerViewSet(XLSXFileMixin,BaseViewSetMixing,ReadOnlyModelViewSet):
    queryset = Contract.objects.all()
    serializer_class = XLSXContractSerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_fields = ContractSerializerViewSet.filterset_fields
    search_fields = ContractSerializerViewSet.search_fields
    ordering_fields = ContractSerializerViewSet.ordering_fields
    column_header = {
        'titles': [ value for key,value in  CONTRACT_FIELD_TITLES.items()],
        'style': {
            'border_side': {
                'border_style': 'thin',
                'color': 'FF000000',
            },
            'fill': {
                'fill_type': 'solid',
                'start_color': 'FFCCFFCC',
            },}

    }
    body = {
        'style': {
            'border_side': {
                'border_style': 'thin',
                'color': 'FF000000',
            }
        }
    }


##-------------------------------------------------------------