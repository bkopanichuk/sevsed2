from __future__ import unicode_literals

from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.l_core.api.base.serializers import DynamicFieldsModelSerializer,BaseOrganizationViewSetMixing
from rest_flex_fields import FlexFieldsModelViewSet
from apps.contracts.models.dict_model import Product, Subscription,ProductPriceDetails, SubscriptionPriceDetails
from apps.dict_register.models import MainActivity, OrganizationType, PropertyType


##MainActivity-------------------------------------------------------
class MainActivitySerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = MainActivity
        fields = ('name', 'code', '__str__', 'id')


# ViewSets define the view behavior.
class MainActivityViewSet(BaseOrganizationViewSetMixing):
    queryset = MainActivity.objects.all()
    serializer_class = MainActivitySerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter, OrderingFilter)
    search_fields = ('name', 'code')


##-------------------------------------------------------------


##OrganizationType-------------------------------------------------------
class OrganizationTypeSerializer(DynamicFieldsModelSerializer):
    class Meta(MainActivitySerializer.Meta):
        model = OrganizationType


# ViewSets define the view behavior.
class OrganizationTypeViewSet(BaseOrganizationViewSetMixing):
    queryset = OrganizationType.objects.all()
    serializer_class = OrganizationTypeSerializer


##-------------------------------------------------------------

##PropertyType-------------------------------------------------------
class PropertyTypeSerializer(MainActivitySerializer):
    class Meta(MainActivitySerializer.Meta):
        model = PropertyType


# ViewSets define the view behavior.
class PropertyTypeViewSet(BaseOrganizationViewSetMixing):
    queryset = PropertyType.objects.all()
    serializer_class = PropertyTypeSerializer


##-------------------------------------------------------------

##-------------------------------------------------------------

##-------------------------------------------------------------

##Subscription-------------------------------------------------------
class SubscriptionSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Subscription
        fields = ['id', '__str__', 'code', 'name', 'price', 'pdv', 'price_pdv','s_count','service_type']


# ViewSets define the view behavior.
class SubscriptionViewSet(BaseOrganizationViewSetMixing):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter, OrderingFilter)
    search_fields = ('name', 'code')
    filterset_fields = ['service_type']



##Product-------------------------------------------------------
class SubscriptionPriceDetailsSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = SubscriptionPriceDetails
        fields = ('id','subscription', 'price', 'pdv', 'price_pdv','start_period','unit','s_count')


# ViewSets define the view behavior.
class SubscriptionPriceDetailsViewSet(BaseOrganizationViewSetMixing):
    queryset = SubscriptionPriceDetails.objects.all()
    serializer_class = SubscriptionPriceDetailsSerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_fields = ['subscription']
    ordering=['-start_period']
##-------------------------------------------------------------

##-------------------------------------------------------------


##Product-------------------------------------------------------
class ProductSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Product
        fields = ('id', '__str__', 'code', 'name', 'price', 'pdv', 'price_pdv')


# ViewSets define the view behavior.
class ProductViewSet(BaseOrganizationViewSetMixing):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter, OrderingFilter)
    search_fields = ('name', 'code')
##-------------------------------------------------------------

##Product-------------------------------------------------------
class ProductPriceDetailsSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = ProductPriceDetails
        fields = ('id','product', 'price', 'pdv', 'price_pdv','start_period')


# ViewSets define the view behavior.
class ProductPriceDetailsViewSet(BaseOrganizationViewSetMixing):
    queryset = ProductPriceDetails.objects.all()
    serializer_class = ProductPriceDetailsSerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_fields = ['product']
    ordering=['-start_period']
##-------------------------------------------------------------

