from __future__ import unicode_literals

from django.conf import settings
from django.http import JsonResponse
from django_filters import rest_framework as filters
from drf_renderer_xlsx.mixins import XLSXFileMixin
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.decorators import api_view
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.l_core.api.base.serializers import BaseOrganizationViewSetMixing
from apps.contracts.api.serializers.contract_serializers import ContractSerializer
from apps.contracts.models.contract_model import Contract
from apps.contracts.models.contract_constants import CONTRACT_STATUS_FUTURE, CONTRACT_STATUS_ACTUAL, \
    CONTRACT_STATUS_ARCHIVE

MEDIA_ROOT = settings.MEDIA_ROOT
MEDIA_URL = settings.MEDIA_URL


class ContractSerializerViewSet(XLSXFileMixin, BaseOrganizationViewSetMixing):
    """Договори"""
    permit_list_expands = ['contractor_data']
    queryset = Contract.objects
    serializer_class = ContractSerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_fields = {
        'contractfinance__total_size_pay': ['exact', 'gte', 'lte'],
        'contractfinance__total_balance': ['exact', 'gte', 'lte'],
        'number_contract': ['exact', 'icontains'],
        'contractor': ['exact'],
        'status': ['exact'],
        'expiration_date': ['exact'],
        'start_date': ['exact']
    }
    search_fields = ('number_contract', 'contractor__full_name')
    ordering_fields = ('contractfinance__total_size_accrual',
                       'contractfinance__total_size_pay',
                       'contractfinance__total_balance',
                       'contractor__name',
                       'number_contract', 'parent_element', 'start_date', 'start_of_contract',
                       'subject_contract', 'copy_contract', 'contractor', 'contractor_name', 'price_contract',
                       'contract_time', 'expiration_date')

    @swagger_auto_schema(method='get', responses={200: ContractSerializer(many=True)})
    @action(detail=False, methods=['get'])
    def future(self, request, ):
        """Договори що в процесі підписання"""
        self.queryset = self.queryset.filter( status=CONTRACT_STATUS_FUTURE)
        return self.list(request)

    @swagger_auto_schema(method='get', responses={200: ContractSerializer(many=True)})
    @action(detail=False, methods=['get'])
    def actual(self, request, ):
        """Актуальні договори"""
        self.queryset = self.queryset.filter( status=CONTRACT_STATUS_ACTUAL)
        return self.list(request)

    @swagger_auto_schema(method='get', responses={200: ContractSerializer(many=True)})
    @action(detail=False, methods=['get'])
    def archive(self, request, ):
        """Договори перенесені в архів"""
        self.queryset = self.queryset.filter( status=CONTRACT_STATUS_ARCHIVE)
        return self.list(request)


@api_view(['GET'])
def refresh_total_balance(request):
    """Оновити баланс за всіма договорами"""
    refresh_count = Contract.refresh_total_balance()
    return JsonResponse({'refresh_count': refresh_count})


