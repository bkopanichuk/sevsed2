from django.conf.urls import url, include

urlpatterns = [
    url(r'document/', include('apps.document.api.router')),
]
