from __future__ import unicode_literals

from django.conf import settings
from rest_framework import serializers

from apps.contracts.api.serializers.contract_finance_serializers import ContractFinanceSerializer
from apps.l_core.api.base.serializers import CoreOrganizationSerializer
from apps.l_core.api.base.serializers import DynamicFieldsModelSerializer
from apps.l_core.models import CoreOrganization
from apps.contracts.models.contract_model import Contract

MEDIA_ROOT = settings.MEDIA_ROOT
MEDIA_URL = settings.MEDIA_URL

import logging

logger = logging.getLogger(__name__)



class ContractSerializer(DynamicFieldsModelSerializer):
    contractor_name = serializers.SerializerMethodField()
    contractfinance = ContractFinanceSerializer(read_only=True)
    contractor_data = serializers.PrimaryKeyRelatedField(read_only=True)
    contractor = serializers.PrimaryKeyRelatedField(required=True, queryset=CoreOrganization.objects.all())

    class Meta:
        model = Contract
        fields = (
            'id', '__str__', 'number_contract', 'parent_element', 'start_date',
            'start_of_contract', 'start_accrual',
            'status', 'automatic_number_gen', 'price_additional_services', 'one_time_service',
            'subject_contract', 'copy_contract', 'contractor', 'contractor_name', 'price_contract', 'contract_time',
            'expiration_date', 'price_contract_by_month', 'contractfinance', 'contract_docx', 'unique_uuid',
            'contractor_data', 'change_status_reason')
        expandable_fields = {
            'contractor_data': (
                CoreOrganizationSerializer, {'source': 'contractor', })
        }

    def get_contractor_name(self, obj):
        if obj.contractor:
            return obj.contractor.__str__()
