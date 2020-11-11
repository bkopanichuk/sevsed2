from __future__ import unicode_literals

from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter, OrderingFilter
from apps.l_core.api.base.serializers import DynamicFieldsModelSerializer
from rest_flex_fields import FlexFieldsModelViewSet
from apps.contracts.models.dict_model import  MainActivity, OrganizationType, PropertyType, TemplateDocument, \
    Product, Subscription,ProductPriceDetails, SubscriptionPriceDetails


##MainActivity-------------------------------------------------------
class MainActivitySerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = MainActivity
        fields = ('name', 'code', '__str__', 'id')


# ViewSets define the view behavior.
class MainActivityViewSet(FlexFieldsModelViewSet):
    queryset = MainActivity.objects.all()
    serializer_class = MainActivitySerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter, OrderingFilter)
    search_fields = ('name', 'code')


##-------------------------------------------------------------


##OrganizationType-------------------------------------------------------
class OrganizationTypeSerializer(MainActivitySerializer):
    class Meta(MainActivitySerializer.Meta):
        model = OrganizationType


# ViewSets define the view behavior.
class OrganizationTypeViewSet(MainActivityViewSet):
    queryset = OrganizationType.objects.all()
    serializer_class = OrganizationTypeSerializer


##-------------------------------------------------------------

##PropertyType-------------------------------------------------------
class PropertyTypeSerializer(MainActivitySerializer):
    class Meta(MainActivitySerializer.Meta):
        model = PropertyType


# ViewSets define the view behavior.
class PropertyTypeViewSet(MainActivityViewSet):
    queryset = PropertyType.objects.all()
    serializer_class = PropertyTypeSerializer


##-------------------------------------------------------------

##-------------------------------------------------------------


##ContractStatus-------------------------------------------------------
class TemplateDocumentSerializer(MainActivitySerializer):
    class Meta(MainActivitySerializer.Meta):
        model = TemplateDocument
        fields = ('id', '__str__', 'template_file', 'related_model_name')


# ViewSets define the view behavior.
class TemplateDocumentViewSet(MainActivityViewSet):
    queryset = TemplateDocument.objects.all()
    serializer_class = TemplateDocumentSerializer
    filterset_fields = {
        'related_model_name': ['exact']}


##-------------------------------------------------------------

##Subscription-------------------------------------------------------
class SubscriptionSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Subscription
        fields = ('id', '__str__', 'code', 'name', 'price', 'pdv', 'price_pdv','s_count','service_type')


# ViewSets define the view behavior.
class SubscriptionViewSet(FlexFieldsModelViewSet):
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
class SubscriptionPriceDetailsViewSet(FlexFieldsModelViewSet):
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
class ProductViewSet(FlexFieldsModelViewSet):
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
class ProductPriceDetailsViewSet(FlexFieldsModelViewSet):
    queryset = ProductPriceDetails.objects.all()
    serializer_class = ProductPriceDetailsSerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_fields = ['product']
    ordering=['-start_period']
##-------------------------------------------------------------

