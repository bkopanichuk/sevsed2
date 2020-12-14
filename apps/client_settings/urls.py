from django.conf.urls import url, include


urlpatterns = [
    url(r'client-settings/', include('apps.client_settings.api.router')),
]
