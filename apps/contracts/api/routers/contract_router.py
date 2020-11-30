from django.conf.urls import *
from rest_framework import routers

from apps.contracts.api.views.contract_views import ContractSerializerViewSet, refresh_total_balance
from apps.contracts.api.views.client_banck_views import UploadClientBankViewSet, upload_client_bank, \
    ConvertClientBankView
from apps.contracts.api.views.contract_product_viewset import ContractProductsViewSet
from apps.contracts.api.views.contract_subscription_viewset import ContractSubscriptionViewSet
from apps.contracts.api.views.stage_propperty_viewset import StagePropertyViewSet
from apps.contracts.api.views.regiater_act_viewset import RegisterActViewSet, generate_acts_view
from apps.contracts.api.views.register_payment_viewset import RegisterPaymentViewSet
from apps.contracts.api.views.register_accrual_viewset import RegisterAccrualViewSet, get_accrual_zip, \
    clear_accrual_data, calculate_accrual, calculate_accrual_in_range
from apps.contracts.api.serializers.xlsx_serializers import XLSXContractSerializerViewSet
from apps.contracts.api.views.report_views import contract_summary_data, contract_accrual_data, contract_largest_debtors

router = routers.DefaultRouter()

router.register(r'contract', ContractSerializerViewSet)
router.register(r'register-accurual', RegisterAccrualViewSet)
router.register(r'register-payment', RegisterPaymentViewSet)
router.register(r'register-act', RegisterActViewSet)
router.register(r'stage-property', StagePropertyViewSet)
router.register(r'contract-subscription', ContractSubscriptionViewSet)
router.register(r'contract-products', ContractProductsViewSet)
router.register(r'import-client-bank', UploadClientBankViewSet)
router.register(r'xlsxcontract', XLSXContractSerializerViewSet)

urlpatterns = [
    url(r'refresh-total-balance', refresh_total_balance),
    url(r'report-contract-summary-data', contract_summary_data),
    url(r'report-contract-accrual-data', contract_accrual_data),
    url(r'report-contract-largest-debtors', contract_largest_debtors),
    url(r'calculate-accrual', calculate_accrual),
    url(r'clear-accrual-data', clear_accrual_data),
    url(r'generate-acts', generate_acts_view),
    url(r'calculate-range-accrual', calculate_accrual_in_range),
    url(r'upload-client-bunk', upload_client_bank),
    url(r'export-accrual-zip', get_accrual_zip),
    url(r'convert-client-bank', ConvertClientBankView.as_view()),

]

urlpatterns += router.urls
