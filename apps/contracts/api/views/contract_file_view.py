from __future__ import unicode_literals
from django_filters import rest_framework as filters
from collections import OrderedDict
from rest_framework.request import Request
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.contracts.models.contract_additional_file_model import ContractFile
from apps.contracts.api.serializers.contract_file_serializer import ContractFileSerializer
from apps.l_core.api.base.serializers import BaseOrganizationViewSetMixing


class ContractFileViewSet(BaseOrganizationViewSetMixing):
    queryset = ContractFile.objects.all()
    serializer_class = ContractFileSerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter, OrderingFilter)

    def get_queryset(self):
        q = super(ContractFileViewSet, self).get_queryset()
        return q.filter(contract__id=self.contract_id)

    def list(self, request, contract_id, *args, **kwargs):
        self.contract_id = int(contract_id)
        return super(ContractFileViewSet, self).list(request, *args, **kwargs)

    def create(self, request: Request, contract_id, *args, **kwargs):
        if isinstance(request.data, OrderedDict):
            setattr(request.data, '_mutable', True)
        self.contract_id = int(contract_id)
        request.data['contract'] = self.contract_id
        return super(ContractFileViewSet, self).create(request, *args, **kwargs)

    def destroy(self, request, contract_id, *args, pk=None, **kwargs):
        if isinstance(request.data, OrderedDict):
            setattr(request.data, '_mutable', True)
        self.contract_id = int(contract_id)
        request.data['contract'] = self.contract_id
        return super(ContractFileViewSet, self).destroy(request, *args, pk=None, **kwargs)

    def retrieve(self, request, contract_id, *args, **kwargs):
        if isinstance(request.data, OrderedDict):
            setattr(request.data, '_mutable', True)
        self.contract_id = int(contract_id)
        request.data['contract'] = self.contract_id
        return super(ContractFileViewSet, self).retrieve(request, *args, **kwargs)

##-------------------------------------------------------------
