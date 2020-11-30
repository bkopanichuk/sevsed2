from django.http import JsonResponse
from django_filters import rest_framework as filters
from rest_framework.decorators import api_view
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.contracts.api.serializers.register_act_serializers import RegisterActSerializer
from apps.contracts.models.register_act_model import RegisterAct
from apps.l_core.api.base.serializers import BaseOrganizationViewSetMixing


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


@api_view(['GET'])
def generate_acts_view(request):
    """Запустити процес створення актів виконаних послуг"""
    generated_acts = RegisterAct.generate_acts()
    return JsonResponse({'generated_acts': generated_acts})