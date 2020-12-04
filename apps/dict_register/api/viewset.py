from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.dict_register.api.serializer import TemplateDocumentSerializer
from apps.dict_register.models import TemplateDocument
from apps.l_core.api.base.serializers import BaseOrganizationViewSetMixing


class TemplateDocumentViewSet(BaseOrganizationViewSetMixing):
    queryset = TemplateDocument.objects.all()
    serializer_class = TemplateDocumentSerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_fields = {
        'related_model_name': ['exact']}

    def get_queryset(self):
        return super(TemplateDocumentViewSet, self).get_queryset()
