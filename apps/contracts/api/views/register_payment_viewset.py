from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.contracts.api.serializers.register_payment_serializers import RegisterPaymentSerializer
from apps.contracts.models.register_payment_model import RegisterPayment
from apps.l_core.api.base.serializers import BaseOrganizationViewSetMixing


class RegisterPaymentViewSet(BaseOrganizationViewSetMixing):
    """Реєстр платежів. Всі платежі привязані до договорів"""
    permit_list_expands = ['contract_data']
    queryset = RegisterPayment.objects.all()
    serializer_class = RegisterPaymentSerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_fields = ['contract__id']