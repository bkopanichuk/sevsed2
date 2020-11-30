from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.contracts.api.serializers.stage_propperty_serializers import StagePropertySerializer
from apps.contracts.models.stage_propperty_model import StageProperty
from apps.l_core.api.base.serializers import BaseOrganizationViewSetMixing


class StagePropertyViewSet(BaseOrganizationViewSetMixing):
    """детальна інформація контрагента. Привязаний до договору і не змінюється при змінах Контрахента"""
    queryset = StageProperty.objects.all()
    serializer_class = StagePropertySerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_fields = ['contract__id']