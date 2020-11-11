# -*- coding: utf-8 -*-

from django.conf.urls import *
from rest_framework import routers, serializers, viewsets


from .serializers import *
router = routers.DefaultRouter()


router.register(r'region', ATURegionViewSet)
router.register(r'district', ATUDistrictViewSet)


urlpatterns = router.urls

