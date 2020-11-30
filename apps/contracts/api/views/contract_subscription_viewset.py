from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.contracts.api.serializers.contract_subscription_serializers import ContractSubscriptionSerializer
from apps.contracts.models.contract_product_model import ContractSubscription
from apps.l_core.api.base.serializers import BaseOrganizationViewSetMixing


class ContractSubscriptionViewSet(BaseOrganizationViewSetMixing):
    """Реєетр парпметрів абонентської плати за договорами"""
    queryset = ContractSubscription.objects.all()
    serializer_class = ContractSubscriptionSerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_fields = ['contract__id']