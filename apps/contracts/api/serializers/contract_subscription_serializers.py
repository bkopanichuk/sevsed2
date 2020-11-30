from apps.contracts.models.contract_product_model import ContractSubscription
from apps.l_core.api.base.serializers import DynamicFieldsModelSerializer


class ContractSubscriptionSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = ContractSubscription
        fields = (
            'id', '__str__', 'count', 'price', 'pdv', 'total_price', 'total_price_pdv', 'is_legal', 'product',
            'contract',
            'start_period', 'end_period')