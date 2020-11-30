import os
import zipfile

from django.http import JsonResponse
from django.utils.crypto import get_random_string
from django_filters import rest_framework as filters
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response

from apps.contracts.api.serializers.register_accrual_serializers import RegisterAccrualSerializer, \
    calculateAccrualSerializer
from apps.contracts.api.views.contract_views import MEDIA_ROOT, MEDIA_URL
from apps.contracts.models.register_accrual_model import RegisterAccrual
from apps.l_core.api.base.serializers import BaseOrganizationViewSetMixing


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


@api_view(['GET'])
def clear_accrual_data(request):
    """Очистити всі акти та нарахування"""
    from apps.contracts.models.register_act_model import RegisterAct
    from apps.contracts.models.contract_finance_model import ContractFinance
    register_act_count = RegisterAct.objects.all().count()
    RegisterAct.objects.all().delete()
    register_accrual_count = RegisterAccrual.objects.all().count()
    RegisterAccrual.objects.all().delete()
    ContractFinance.objects.all().update(last_date_accrual=None,
                                         total_size_accrual=0, last_date_pay=None, total_size_pay=0, total_balance=0)
    return JsonResponse({'register_accrual_count': register_accrual_count, "register_act_count": register_act_count})


@api_view(['GET'])
def calculate_accrual(request):
    """Запустити процес створення нахувань"""
    from apps.contracts.tasks import calculate_accruals
    result = calculate_accruals.delay()
    return JsonResponse({'task_id': result.task_id})


@api_view(['POST'])
def calculate_accrual_in_range(request):
    """Запустити процес створення нахувань у вказаному часовому проміжку"""
    from apps.contracts.models.contract_model import Contract
    serializer = calculateAccrualSerializer(data=request.data)
    if serializer.is_valid():
        data = serializer.validated_data
        res = Contract.calculate_accruals(**data)
        return JsonResponse(res, safe=False)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
