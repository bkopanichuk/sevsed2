from rest_framework import routers

from .views import FormSettingsViewSet

router = routers.DefaultRouter()
router.register(r'form-settings', FormSettingsViewSet,basename='form-settings')

urlpatterns = router.urls
