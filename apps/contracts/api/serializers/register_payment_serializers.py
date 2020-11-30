from rest_framework import serializers

from apps.contracts.api.serializers.contract_serializers import ContractSerializer
from apps.contracts.models.register_payment_model import RegisterPayment
from apps.l_core.api.base.serializers import DynamicFieldsModelSerializer


class RegisterPaymentSerializer(DynamicFieldsModelSerializer):
    contract_data = serializers.PrimaryKeyRelatedField(read_only=True)
    contractor_name = serializers.SerializerMethodField()

    class Meta:
        model = RegisterPayment
        fields = (
            'payment_date', 'id', 'sum_payment', 'payment_type', 'contract', '__str__', 'contract_data',
            'contractor_name',
            'outer_doc_number')
        expandable_fields = {
            'contract_data': (
                ContractSerializer, {'source': 'contract', 'fields': ['id', '__str__']})
        }

    def get_contractor_name(self, obj):
        if obj.contract:
            return obj.contract.contractor.__str__()