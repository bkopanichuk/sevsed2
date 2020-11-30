from rest_framework import serializers

from apps.contracts.api.serializers.contract_serializers import ContractSerializer
from apps.contracts.models.register_accrual_model import RegisterAccrual
from apps.l_core.api.base.serializers import DynamicFieldsModelSerializer


class RegisterAccrualSerializer(DynamicFieldsModelSerializer):
    contract = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = RegisterAccrual
        fields = (
            'id', '__str__', 'date_accrual', 'size_accrual', 'balance', 'penalty', 'pay_size', 'contract', 'title',
            'accrual_docx', 'date_sending_doc', 'is_doc_send_successful')
        expandable_fields = {
            'contract': (
                ContractSerializer, {'source': 'contract', 'fields': ['id', '__str__']})
        }


class calculateAccrualSerializer(serializers.Serializer):
    create_pdf = serializers.BooleanField()
    is_budget = serializers.BooleanField()
    is_comercial = serializers.BooleanField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()