from __future__ import unicode_literals

from rest_framework import serializers
from apps.contracts.models.contract_additional_file_model import ContractFile


class ContractFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContractFile
        fields = ('contract', 'upload', 'preview', 'id','file_name','file_size','date_add','__str__')
        read_only_fields = ['preview', 'id']
