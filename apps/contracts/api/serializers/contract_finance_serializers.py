from apps.contracts.models.contract_finance_model import ContractFinance
from apps.l_core.api.base.serializers import DynamicFieldsModelSerializer


class ContractFinanceSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = ContractFinance
        fields = ('id', 'total_size_accrual', 'total_size_pay', 'total_balance')