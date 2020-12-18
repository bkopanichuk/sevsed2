from django.conf.urls import url, include
from .views import component_permission_view


urlpatterns = [
    url(r'client-settings/', include('apps.client_settings.api.router')),
    url(r'client-settings-doc/', component_permission_view),
]
