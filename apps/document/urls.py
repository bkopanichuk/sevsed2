from django.conf.urls import url, include
from .views import public_document_details

urlpatterns = [
    url(r'document/', include('apps.document.api.router')),
    url(r'document_details/(?P<doc_uuid>[^/.]+)/$', public_document_details),
]
