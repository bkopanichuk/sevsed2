from django.conf.urls import *
from rest_framework import routers

from apps.contracts.api.views.contract_views import ContractSerializerViewSet, RegisterAccrualViewSet,\
    RegisterPaymentViewSet, RegisterActViewSet, \
    refresh_total_balance, calculate_accrual, clear_accrual_data, StagePropertyViewSet, \
    CoordinationViewSet, generate_acts_view,  ContractSubscriptionViewSet, calculate_accrual_in_range, \
    upload_client_bank, UploadClientBankViewSet, get_accrual_zip, ConvertClientBankView, ContractProductsViewSet
from apps.contracts.api.serializers.xlsx_serializers import XLSXContractSerializerViewSet
from apps.contracts.api.views.report_views import contract_summary_data, contract_accrual_data, contract_largest_debtors

router = routers.DefaultRouter()

router.register(r'contract', ContractSerializerViewSet)
router.register(r'register-accurual', RegisterAccrualViewSet)
router.register(r'register-payment', RegisterPaymentViewSet)
router.register(r'register-act', RegisterActViewSet)
router.register(r'stage-property', StagePropertyViewSet)
router.register(r'coordination', CoordinationViewSet)
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
