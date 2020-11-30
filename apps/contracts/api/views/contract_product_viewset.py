from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.contracts.api.serializers.contract_product_serializer import ContractProductsSerializer
from apps.contracts.models.contract_product_model import ContractProducts
from apps.l_core.api.base.serializers import BaseOrganizationViewSetMixing


class ContractProductsViewSet(BaseOrganizationViewSetMixing):
    """Реєстр наданих послуг за договорами одноразову послуги, або товари"""
    queryset = ContractProducts.objects.all()
    serializer_class = ContractProductsSerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_fields = ['contract__id']