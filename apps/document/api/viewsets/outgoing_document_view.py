from __future__ import unicode_literals

from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from .document_base_view import OrderingFilterMixin
from apps.document.api.srializers.document_serializer import OutgoingDocumentSerializer
from apps.document.models.document_model import BaseDocument, ON_REGISTRATION, REGISTERED, \
    ON_AGREEMENT, ON_SIGNING, CONCERTED, TRANSFERRED,REJECT,ARCHIVED
from ...models.document_constants import OUTGOING


class OutgoingDocumentViewSet(OrderingFilterMixin):
    serializer_class = OutgoingDocumentSerializer
    queryset = BaseDocument.objects.filter(document_cast=OUTGOING)
    filterset_fields = OrderingFilterMixin.filterset_fields.update(
        {'outgoing_type': ['exact'],
         'status': ['exact']
         })

    def get_queryset(self):
        q = super(OutgoingDocumentViewSet,self).get_queryset()
        res_q = q.select_related('correspondent','outgoing_type')
        return res_q

    ### STATUS FILTERS #######################################################################
    @swagger_auto_schema(method='get', responses={200: OutgoingDocumentSerializer(many=True)})
    @action(detail=False, methods=['get'])
    def registered(self, request, ):
        self.queryset = self.queryset.filter(status=REGISTERED)
        return self.list(request)


    @swagger_auto_schema(method='get', responses={200: OutgoingDocumentSerializer(many=True)})
    @action(detail=False, methods=['get'])
    def rejected_to_me(self, request, ):
        user_id = request.user.id
        self.queryset = self.queryset.filter(status=REJECT, author_id=user_id)
        return self.list(request)

    @swagger_auto_schema(method='get', responses={200: OutgoingDocumentSerializer(many=True)})
    @action(detail=False, methods=['get'])
    def on_registration(self, request, ):
        self.queryset = self.queryset.filter(status=ON_REGISTRATION)
        return self.list(request)

    @swagger_auto_schema(method='get', responses={200: OutgoingDocumentSerializer(many=True)})
    @action(detail=False, methods=['get'])
    def on_agreement(self, request):
        self.queryset = self.queryset.filter(status=ON_AGREEMENT)
        return self.list(request)

    @swagger_auto_schema(method='get', responses={200: OutgoingDocumentSerializer(many=True)})
    @action(detail=False, methods=['get'])
    def concerted(self, request):
        self.queryset = self.queryset.filter(status=CONCERTED)
        return self.list(request)

    @swagger_auto_schema(method='get', responses={200: OutgoingDocumentSerializer(many=True)})
    @action(detail=False, methods=['get'])
    def on_sign(self, request):
        self.queryset = self.queryset.filter(status=ON_SIGNING)
        return self.list(request)

    @swagger_auto_schema(method='get', responses={200: OutgoingDocumentSerializer(many=True)})
    @action(detail=False, methods=['get'])
    def archived(self, request):
        self.queryset = self.queryset.filter(status=ARCHIVED)
        return self.list(request)

    @swagger_auto_schema(method='get', responses={200: OutgoingDocumentSerializer(many=True)})
    @action(detail=False, methods=['get'])
    def transferred(self, request):
        self.queryset = self.queryset.filter(status=TRANSFERRED)
        return self.list(request)
    ###########################################################################################
    ###################SPECIAL METHODS#########################################################

