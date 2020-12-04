from django.conf.urls import url, include

urlpatterns = [
    url(r'dict/', include('apps.dict_register.api.router'))]