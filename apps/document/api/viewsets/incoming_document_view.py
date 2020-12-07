from __future__ import unicode_literals

from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from .document_base_view import OrderingFilterMixin, BaseOrganizationViewSetMixing
from apps.document.api.srializers.document_serializer import IncomingDocumentSerializer
from apps.document.models.document_model import BaseDocument, ON_RESOLUTION, ON_REGISTRATION, REGISTERED, ON_EXECUTION, \
    COMPLETED, ARCHIVED, ON_CONTROL,PASSED_CONTROL
from ...models.document_constants import INCOMING


class IncomingDocumentViewSet(OrderingFilterMixin):
    serializer_class = IncomingDocumentSerializer
    queryset = BaseDocument.objects.filter(document_cast=INCOMING)
    search_fields = ['reg_number', 'title', 'comment']
    filterset_fields = {
        'id': ['in'],
        'incoming_type': ['exact'],
        'correspondent': ['exact'],
        'reg_number': ['icontains'],
        'create_date': ['range'],
        'case_index': ['icontains'],
        'status': ['exact']
    }

    def get_queryset(self):
        q = super(IncomingDocumentViewSet, self).get_queryset()
        res_q = q.select_related('correspondent', 'incoming_type', )
        return res_q

    @swagger_auto_schema(method='get', responses={200: IncomingDocumentSerializer(many=True)})
    @action(detail=False, methods=['get'])
    def on_registration(self, request, ):
        """ Вхідні документи які очікують реєстрації"""
        self.queryset = self.queryset.filter(status=ON_REGISTRATION)
        return self.list(request)

    @swagger_auto_schema(method='get', responses={200: IncomingDocumentSerializer(many=True)})
    @action(detail=False, methods=['get'])
    def registered(self, request, ):
        """ Зареєстровані вхідні документи"""
        self.queryset = self.queryset.filter(status=REGISTERED)
        return self.list(request)

    @swagger_auto_schema(method='get', responses={200: IncomingDocumentSerializer(many=True)})
    @action(detail=False, methods=['get'])
    def on_resolution(self, request, ):
        """ Зареєстровані вхідні документи передані на формування резолюцій"""
        self.queryset = self.queryset.filter(status=ON_RESOLUTION)
        return self.list(request)

    @swagger_auto_schema(method='get', responses={200: IncomingDocumentSerializer(many=True)})
    @action(detail=False, methods=['get'])
    def on_control(self, request, ):
        """ Вхідні документи з виконаними дорученнями (очукують контролю)"""
        self.queryset = self.queryset.filter(status=ON_CONTROL)
        return self.list(request)

    @swagger_auto_schema(method='get', responses={200: IncomingDocumentSerializer(many=True)})
    @action(detail=False, methods=['get'])
    def passed_control(self, request, ):
        """ Вхідні документи зняті з контролю (готові до архівування)"""
        self.queryset = self.queryset.filter(status=PASSED_CONTROL)
        return self.list(request)

    @swagger_auto_schema(method='get', responses={200: IncomingDocumentSerializer(many=True)})
    @action(detail=False, methods=['get'])
    def on_execution(self, request):
        """ Вхідні документи на виконанні доручень (резолюцій)"""
        self.queryset = self.queryset.filter(status=ON_EXECUTION)
        return self.list(request)

    @swagger_auto_schema(method='get', responses={200: IncomingDocumentSerializer(many=True)})
    @action(detail=False, methods=['get'])
    def completed(self, request):
        """ Вхідні документи з виконаними дорученнями"""
        self.queryset = self.queryset.filter(status=COMPLETED)
        return self.list(request)

    @swagger_auto_schema(method='get', responses={200: IncomingDocumentSerializer(many=True)})
    @action(detail=False, methods=['get'])
    def archived(self, request):
        """ Вхідні документи відправлені в архів"""
        self.queryset = self.queryset.filter(status=ARCHIVED)
        return self.list(request)
