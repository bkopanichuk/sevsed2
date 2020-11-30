from apps.contracts.models.contract_product_model import ContractProducts
from apps.l_core.api.base.serializers import DynamicFieldsModelSerializer


class ContractProductsSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = ContractProducts
        fields = ('id', '__str__', 'count', 'price', 'pdv', 'total_price', 'total_price_pdv', 'product', 'contract')