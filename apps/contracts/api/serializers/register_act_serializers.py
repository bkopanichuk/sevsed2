from rest_framework import serializers

from apps.contracts.api.serializers.contract_serializers import ContractSerializer
from apps.contracts.api.serializers.register_accrual_serializers import RegisterAccrualSerializer
from apps.contracts.api.serializers.register_payment_serializers import RegisterPaymentSerializer
from apps.contracts.models.register_act_model import RegisterAct
from apps.l_core.api.base.serializers import DynamicFieldsModelSerializer


class RegisterActSerializer(DynamicFieldsModelSerializer):
    ##accrual_data = LCorePrimaryKeyRelatedField(read_only=True)
    payments = RegisterPaymentSerializer(read_only=True, many=True)
    accrual = serializers.PrimaryKeyRelatedField(read_only=True)
    contract = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = RegisterAct
        fields = (
            'id', 'number_act', '__str__', 'date_formation_act', 'is_send_successful', 'date_sending_act',
            'date_return_act', 'accrual', 'copy_act_from_contractor',
            'payments', 'copy_act', 'copy_act_pdf', 'contract')
        expandable_fields = {
            'accrual': (
                RegisterAccrualSerializer, {'source': 'accrual', 'fields': ['id', 'date_accrual', 'size_accrual']}),
            'contract': (
                ContractSerializer, {'source': 'contract', 'fields': ['id', '__str__', 'contractor']}),

        }