from __future__ import unicode_literals

import os
import zipfile

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse
from django.utils.crypto import get_random_string
from django_filters import rest_framework as filters
from drf_renderer_xlsx.mixins import XLSXFileMixin
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.contracts.models.payment_model import ImportPayment
from apps.l_core.api.base.serializers import BaseOrganizationViewSetMixing
from ..serializers.contract_serializers import ContractSerializer, RegisterAccrualSerializer, RegisterPaymentSerializer, \
    RegisterActSerializer, StagePropertySerializer, ContractSubscriptionSerializer, ContractProductsSerializer, \
    CoordinationSerializer, RegisterAccrual, RegisterAct, ContractFinance, calculateAccrualSerializer, \
    UploadCilentBanklSerializer, ConvertCilentBanklSerializer
from ...models.contract_model import Contract, RegisterPayment, StageProperty, Coordination, ContractSubscription, \
    ContractProducts

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


class RegisterAccrualViewSet(BaseOrganizationViewSetMixing):
    """Реєстр нарахувань за договорами (рахунки)"""
    permit_list_expands = ['contract']
    queryset = RegisterAccrual.objects.all()
    serializer_class = RegisterAccrualSerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter, OrderingFilter)
    search_fields = ['contract__number_contract']
    filterset_fields = {
        'contract__id': ['exact'],
        'date_accrual': ['exact', 'year__exact', 'month__exact'],
    }
    ordering = ['date_accrual', 'date_sending_doc']


class RegisterPaymentViewSet(BaseOrganizationViewSetMixing):
    """Реєстр платежів. Всі платежі привязані до договорів"""
    permit_list_expands = ['contract_data']
    queryset = RegisterPayment.objects.all()
    serializer_class = RegisterPaymentSerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_fields = ['contract__id']


class RegisterActViewSet(BaseOrganizationViewSetMixing):
    """Реєстр актів виконаних послуг. Формуються на основі нарахувань"""
    permit_list_expands = ['accrual', 'contract']
    queryset = RegisterAct.objects.all()
    serializer_class = RegisterActSerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_fields = {'contract': ['exact'],
                        'is_send_successful': ['exact'], }
    ordering_fields = ['date_formation_act', 'is_send_successful']
    ordering = ['date_formation_act']


class StagePropertyViewSet(BaseOrganizationViewSetMixing):
    """детальна інформація контрагента. Привязаний до договору і не змінюється при змінах Контрахента"""
    queryset = StageProperty.objects.all()
    serializer_class = StagePropertySerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_fields = ['contract__id']


class ContractSubscriptionViewSet(BaseOrganizationViewSetMixing):
    """Реєетр парпметрів абонентської плати за договорами"""
    queryset = ContractSubscription.objects.all()
    serializer_class = ContractSubscriptionSerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_fields = ['contract__id']


class ContractProductsViewSet(BaseOrganizationViewSetMixing):
    """Реєстр наданих послуг за договорами одноразову послуги, або товари"""
    queryset = ContractProducts.objects.all()
    serializer_class = ContractProductsSerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_fields = ['contract__id']


class CoordinationViewSet(BaseOrganizationViewSetMixing):
    queryset = Coordination.objects.all()
    serializer_class = CoordinationSerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_fields = ['object_id']

    def create(self, request, *args, **kwargs):
        model = request.data['model']
        app_label = request.data['app_label']
        model_type = ContentType.objects.get(model=model, app_label=app_label)
        request.data['content_type'] = model_type.id
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save()


@api_view(['GET'])
def refresh_total_balance(request):
    """Оновити баланс за всіма договорами"""
    refresh_count = Contract.refresh_total_balance()
    return JsonResponse({'refresh_count': refresh_count})


@api_view(['GET'])
def generate_acts_view(request):
    """Запустити процес створення актів виконаних послуг"""
    generated_acts = RegisterAct.generate_acts()
    return JsonResponse({'generated_acts': generated_acts})


@api_view(['GET'])
def calculate_accrual(request):
    """Запустити процес створення нахувань"""
    from apps.contracts.tasks import calculate_accruals
    result = calculate_accruals.delay()
    return JsonResponse({'task_id': result.task_id})


@api_view(['GET'])
def clear_accrual_data(request):
    """Очистити всі акти та нарахування"""
    register_act_count = RegisterAct.objects.all().count()
    RegisterAct.objects.all().delete()
    register_accrual_count = RegisterAccrual.objects.all().count()
    RegisterAccrual.objects.all().delete()
    ContractFinance.objects.all().update(last_date_accrual=None,
                                         total_size_accrual=0, last_date_pay=None, total_size_pay=0, total_balance=0)
    return JsonResponse({'register_accrual_count': register_accrual_count, "register_act_count": register_act_count})


@api_view(['POST'])
def calculate_accrual_in_range(request):
    """Запустити процес створення нахувань у вказаному часовому проміжку"""
    serializer = calculateAccrualSerializer(data=request.data)
    if serializer.is_valid():
        data = serializer.validated_data
        res = Contract.calculate_accruals(**data)
        return JsonResponse(res, safe=False)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UploadClientBankViewSet(BaseOrganizationViewSetMixing):
    """Дані проплат за договорами"""
    queryset = ImportPayment.objects.all()
    serializer_class = UploadCilentBanklSerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter, OrderingFilter)


@api_view(['POST'])
def upload_client_bank(request):
    """Завантажити дані проплат за договорами з клієнт-банку"""
    serializer = UploadCilentBanklSerializer(data=request.data)
    if serializer.is_valid():
        res = serializer.save()
        return JsonResponse(res.details, safe=False)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_accrual_zip(request):
    """Завантажити всі акти та нарахування в ZIP"""
    # Create the HttpResponse object with the appropriate PDF headpeers.
    _ids = request.GET.getlist('ids[]')
    ids = [int(item) for item in _ids]
    base_name = get_random_string() + '.zip'
    mk_path = os.path.join(MEDIA_ROOT, 'tmp')
    ####
    if not os.path.exists(mk_path):
        os.makedirs(mk_path)
    ####
    zf_path = os.path.join(MEDIA_ROOT, 'tmp', base_name)
    zf = zipfile.ZipFile(zf_path, "w")
    print(_ids, ids)
    accruals = RegisterAccrual.objects.filter(pk__in=ids).values('accrual_docx')
    for accrual in accruals:
        print('Accrual:', accrual['accrual_docx'])
        zf.write(os.path.join(MEDIA_ROOT, accrual['accrual_docx']), os.path.basename(accrual['accrual_docx']))
    zf.close()
    url = os.path.join(MEDIA_URL, 'tmp', base_name)
    return JsonResponse({'url': url})


class ConvertClientBankView(APIView):
    """Конвертувати дані Клієнт-банку з CSV в XML - який здатен прочитати 1с"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ConvertCilentBanklSerializer(data=request.data)
        if serializer.is_valid():
            url = serializer.convert_data_from_csv()
            return JsonResponse({'url': url})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
