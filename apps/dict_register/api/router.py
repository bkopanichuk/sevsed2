from rest_framework import routers

from apps.dict_register.api.viewset import TemplateDocumentViewSet

router = routers.DefaultRouter()

router.register('doc-templates', TemplateDocumentViewSet)

urlpatterns = router.urls
