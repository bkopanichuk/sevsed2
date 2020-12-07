from __future__ import unicode_literals

from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action

from apps.document.models.document_model import BaseDocument
from ...models.document_constants import INNER
from ...models.document_model import REGISTERED,REJECT,ON_REGISTRATION,ON_AGREEMENT,CONCERTED,ON_SIGNING,ARCHIVED,\
    ON_RESOLUTION,ON_CONTROL,PASSED_CONTROL,ON_EXECUTION,COMPLETED,PROJECT

from .document_base_view import OrderingFilterMixin
from ..srializers.document_serializer import InnerDocumentSerializer


class InnerDocumentViewSet(OrderingFilterMixin):
    serializer_class = InnerDocumentSerializer
    queryset = BaseDocument.objects.filter(document_cast=INNER).select_related('main_signer')
    search_fields = ['reg_number', 'title', 'comment']
    filterset_fields = {
        'id': ['in'],
        'reg_number': ['icontains'],
        'case_index': ['icontains'],
          'create_date': ['range'],
        'comment': ['icontains'],
        'main_signer':['exact']
    }
    ### STATUS FILTERS #######################################################################
    @swagger_auto_schema(method='get', responses={200: InnerDocumentSerializer(many=True)})
    @action(detail=False, methods=['get'])
    def registered(self, request, ):
        self.queryset = self.queryset.filter(status=REGISTERED)
        return self.list(request)

    @swagger_auto_schema(method='get', responses={200: InnerDocumentSerializer(many=True)})
    @action(detail=False, methods=['get'])
    def rejected_to_me(self, request, ):
        user_id = request.user.id
        self.queryset = self.queryset.filter(status=REJECT, author_id=user_id)
        return self.list(request)

    @swagger_auto_schema(method='get', responses={200: InnerDocumentSerializer(many=True)})
    @action(detail=False, methods=['get'])
    def on_registration(self, request, ):
        self.queryset = self.queryset.filter(status=ON_REGISTRATION)
        return self.list(request)

    @swagger_auto_schema(method='get', responses={200: InnerDocumentSerializer(many=True)})
    @action(detail=False, methods=['get'])
    def on_agreement(self, request):
        self.queryset = self.queryset.filter(status=ON_AGREEMENT)
        return self.list(request)

    @swagger_auto_schema(method='get', responses={200: InnerDocumentSerializer(many=True)})
    @action(detail=False, methods=['get'])
    def concerted(self, request):
        self.queryset = self.queryset.filter(status=CONCERTED)
        return self.list(request)

    @swagger_auto_schema(method='get', responses={200: InnerDocumentSerializer(many=True)})
    @action(detail=False, methods=['get'])
    def on_sign(self, request):
        self.queryset = self.queryset.filter(status=ON_SIGNING)
        return self.list(request)

    @swagger_auto_schema(method='get', responses={200: InnerDocumentSerializer(many=True)})
    @action(detail=False, methods=['get'])
    def archived(self, request):
        self.queryset = self.queryset.filter(status=ARCHIVED)
        return self.list(request)

    @swagger_auto_schema(method='get', responses={200: InnerDocumentSerializer(many=True)})
    @action(detail=False, methods=['get'])
    def on_resolution(self, request, ):
        """ Зареєстровані вхідні документи передані на формування резолюцій"""
        self.queryset = self.queryset.filter(status=ON_RESOLUTION)
        return self.list(request)

    @swagger_auto_schema(method='get', responses={200: InnerDocumentSerializer(many=True)})
    @action(detail=False, methods=['get'])
    def on_control(self, request, ):
        """ Вхідні документи з виконаними дорученнями (очукують контролю)"""
        self.queryset = self.queryset.filter(status=ON_CONTROL)
        return self.list(request)

    @swagger_auto_schema(method='get', responses={200: InnerDocumentSerializer(many=True)})
    @action(detail=False, methods=['get'])
    def passed_control(self, request, ):
        """ Вхідні документи зняті з контролю (готові до архівування)"""
        self.queryset = self.queryset.filter(status=PASSED_CONTROL)
        return self.list(request)

    @swagger_auto_schema(method='get', responses={200: InnerDocumentSerializer(many=True)})
    @action(detail=False, methods=['get'])
    def on_execution(self, request):
        """ Вхідні документи на виконанні доручень (резолюцій)"""
        self.queryset = self.queryset.filter(status=ON_EXECUTION)
        return self.list(request)

    @swagger_auto_schema(method='get', responses={200: InnerDocumentSerializer(many=True)})
    @action(detail=False, methods=['get'])
    def completed(self, request):
        """ Вхідні документи з виконаними дорученнями"""
        self.queryset = self.queryset.filter(status=COMPLETED)
        return self.list(request)

    @swagger_auto_schema(method='get', responses={200: InnerDocumentSerializer(many=True)})
    @action(detail=False, methods=['get'])
    def my_project(self, request, ):
        self.queryset = self.queryset.filter(author=request.user, status=PROJECT)
        return self.list(request, )
    ###########################################################################################