from rest_framework import routers

from ..serializers.dict_serializers import MainActivityViewSet, OrganizationTypeViewSet, PropertyTypeViewSet, \
    SubscriptionViewSet, ProductViewSet, ProductPriceDetailsViewSet, SubscriptionPriceDetailsViewSet

router = routers.DefaultRouter()

router.register(r'main-activity', MainActivityViewSet)
router.register(r'organization-type', OrganizationTypeViewSet)
router.register(r'property-type', PropertyTypeViewSet)

router.register(r'subscription', SubscriptionViewSet)
router.register(r'product', ProductViewSet)
router.register(r'product-details', ProductPriceDetailsViewSet)
router.register(r'subscription-details', SubscriptionPriceDetailsViewSet)

urlpatterns = router.urls
