from django.conf.urls import url, include

urlpatterns = [
    url(r'contracts/', include('apps.contracts.api.routers.contract_router')),
    url(r'contracts-dict/', include('apps.contracts.api.routers.dict_router')),
]
