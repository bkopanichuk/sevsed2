from apps.contracts.models.stage_propperty_model import StageProperty
from apps.l_core.api.base.serializers import DynamicFieldsModelSerializer


class StagePropertySerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = StageProperty
        fields = (
            'id', '__str__', 'contract', 'name', 'address', 'settlement_account', 'mfo', 'edrpou', 'phone', 'bank_name',
            'ipn', 'main_unit', 'main_unit_state', 'certificate_number', 'email', 'statute_copy', 'work_reason')