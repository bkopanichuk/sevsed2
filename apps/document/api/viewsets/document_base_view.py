from __future__ import unicode_literals

from django.db.models import Count
from django_filters import rest_framework as filters
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.document.api.srializers import DocumentSerializer, UploadDocumentSerializer, DocumentHistorySerializer
from apps.document.api.srializers.document_serializer import RelatedDocumentSerializer, EmptySerializer, \
    SendToArchiveSerializer
from apps.document.api.srializers.task_serializer import CreateFlowSerializer
from apps.document.models.document_constants import INCOMING, INNER, OUTGOING
from apps.document.models.document_model import BaseDocument, ON_RESOLUTION, ON_AGREEMENT
from apps.l_core.api.base.serializers import BaseOrganizationViewSetMixing
from apps.document.services.document.resolution_service import ResolutionDocument
from apps.document.services.document.start_approve_service import DocumentStartApprove
from apps.document.services.document.create_new_approve_flow_service import DocumentCreateNewApproveFlow
from apps.document.services.document.consideration_service import DocumentConsideration
from apps.document.services.document.senc_to_archive_service import SendToArchive
from apps.document.services.document.register_document_service import RegisterDocument


class OrderingFilterMixin(BaseOrganizationViewSetMixing):
    filter_backends = (filters.DjangoFilterBackend, SearchFilter, OrderingFilter)
    serializer_class = DocumentSerializer
    # list_serializer_class = DocumentListSerializer
    filterset_fields = {'id': ['in']}
    search_fields = ['reg_number', 'title', 'comment']
    ordering_fields = ['reg_number', 'reg_date', 'outgoing_date']


class BaseDocumentSerializerViewSet(OrderingFilterMixin):
    queryset = BaseDocument.objects.all()
    search_fields = ['reg_number', 'title', 'comment']
    ordering_fields = ['reg_number', 'reg_date']

    def get_queryset(self):
        q = super(BaseDocumentSerializerViewSet, self).get_queryset()
        res_q = q.select_related('incoming_type', 'correspondent', 'outgoing_type', )
        return res_q

    @swagger_auto_schema(method='get', responses={200: DocumentSerializer(many=True)})
    @action(detail=False, methods=['get'])
    def my_resolution(self, request, ):
        self.queryset = BaseDocument.objects.filter(approvers_list__in=[request.user], status=ON_RESOLUTION)
        return self.list(request, )

    @swagger_auto_schema(method='get', responses={200: DocumentSerializer(many=True)})
    @action(detail=False, methods=['get'])
    def my_approve(self, request, ):
        self.queryset = BaseDocument.objects.filter(approvers_list__in=[request.user], status=ON_AGREEMENT)
        return self.list(request, )

    document = openapi.Parameter('document_id', openapi.IN_PATH, description="Ідентифікатор документа",
                                 type=openapi.TYPE_INTEGER)

    @swagger_auto_schema(method='get', responses={200: RelatedDocumentSerializer(many=True)},
                         manual_parameters=[document])
    @action(detail=False, methods=['get'], url_path='get_related_docs/(?P<document_id>[^/.]+)')
    def get_related_docs(self, request, document_id=None):
        self.serializer_class = RelatedDocumentSerializer
        self.queryset = BaseDocument.objects.filter(document_linked_to__id=document_id)
        return self.list(request)

    @swagger_auto_schema(method='post', responses={200: RelatedDocumentSerializer(many=True)},
                         manual_parameters=[document], request_body=None)
    @action(detail=False, methods=['post'],
            url_path='add_related_doc/(?P<document_id>[^/.]+)/(?P<related_document_id>[^/.]+)')
    def add_related_doc(self, request, document_id=None, related_document_id=None):
        self.serializer_class = RelatedDocumentSerializer
        document = BaseDocument.objects.get(pk=document_id)
        related_document = BaseDocument.objects.get(pk=related_document_id)
        document.document_linked_to.add(related_document)
        self.queryset = BaseDocument.objects.filter(document_linked_to=document)
        return self.list(request)

    @swagger_auto_schema(method='delete', responses={200: RelatedDocumentSerializer(many=True)},
                         manual_parameters=[document])
    @action(detail=False, methods=['delete'],
            url_path='remove_related_doc/(?P<document_id>[^/.]+)/(?P<related_document_id>[^/.]+)')
    def remove_related_doc(self, request, document_id=None, related_document_id=None):
        self.serializer_class = RelatedDocumentSerializer
        document = BaseDocument.objects.get(pk=document_id)
        related_document = BaseDocument.objects.get(pk=related_document_id)
        document.document_linked_to.remove(related_document)
        self.queryset = BaseDocument.objects.filter(document_linked_to=document)
        return self.list(request)

    @swagger_auto_schema(request_body=EmptySerializer(), responses={200: DocumentSerializer(many=False)})
    @action(detail=False, methods=['patch'],
            url_path='create_new_approve_flow/(?P<document_id>[^/.]+)')
    def create_new_approve_flow(self, request, document_id):
        doc = BaseDocument.objects.get(pk=document_id)
        process = DocumentCreateNewApproveFlow(doc=doc)
        res = process.run()
        serializer = DocumentSerializer(res, context={'request': request})
        return Response(serializer.data)

    @swagger_auto_schema(request_body=SendToArchiveSerializer(), responses={200: DocumentSerializer(many=False)})
    @action(detail=False, methods=['patch'],
            url_path='send_to_archive/(?P<document_id>[^/.]+)')
    def send_to_archive(self, request, document_id):
        """Відправити документ на архівування"""
        request_serializer = SendToArchiveSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        doc = BaseDocument.objects.get(pk=document_id)
        process = SendToArchive(document=doc, data=request_serializer.validated_data, user=request.user)
        res = process.run()
        serializer = DocumentSerializer(res, context={'request': request})
        return Response(serializer.data)

    @swagger_auto_schema(method='get')
    @action(detail=False, methods=['get'])
    def document_status_count(self, request):
        """ Повертає кількість документів по статусах, розділено за типами документів"""
        q_incoming = self.get_queryset().filter(document_cast=INCOMING).values('status', ).annotate(
            dcount=Count('status'))
        q_inner = self.get_queryset().filter(document_cast=INNER).values('status', ).annotate(dcount=Count('status'))
        q_outgoing = self.get_queryset().filter(document_cast=OUTGOING).values('status', ).annotate(
            dcount=Count('status'))
        data = {
            INCOMING: dict((k['status'], k['dcount']) for k in list(q_incoming)),
            INNER: dict((k['status'], k['dcount']) for k in list(q_inner)),
            OUTGOING: dict((k['status'], k['dcount']) for k in list(q_outgoing)),
        }
        return Response(data)

        ##Members.objects.values('designation').annotate(dcount=Count('designation'))


class UploadDocumentViewSet(BaseOrganizationViewSetMixing):
    queryset = BaseDocument.objects.all()
    serializer_class = UploadDocumentSerializer


class DocumentHistoryView(APIView):
    @swagger_auto_schema(responses={200: DocumentHistorySerializer(many=False)})
    def get(self, request, document_id):
        q = BaseDocument.objects.get(pk=document_id)
        serializer = DocumentHistorySerializer(q)
        return Response(serializer.data)


class RegisterDocumentView(APIView):
    @swagger_auto_schema(responses={200: DocumentSerializer(many=False)})
    def post(self, request, document_id):
        doc = BaseDocument.objects.get(pk=document_id)
        process = RegisterDocument(doc=doc)
        res = process.run()
        serializer = DocumentSerializer(res)
        return Response(serializer.data)


class DocumentConsiderationView(APIView):
    @swagger_auto_schema(responses={200: DocumentSerializer(many=False)})
    def post(self, request, document_id):
        doc = BaseDocument.objects.get(pk=document_id)
        process = DocumentConsideration(doc=doc)
        res = process.run()
        serializer = DocumentSerializer(res)
        return Response(serializer.data)


class DocumentStartApproveView(APIView):
    @swagger_auto_schema(responses={200: DocumentSerializer(many=False)})
    def post(self, request, document_id):
        resolution_flow_serializer = CreateFlowSerializer(data=request.data)
        resolution_flow_serializer.is_valid(raise_exception=True)
        doc = BaseDocument.objects.get(pk=document_id)
        process = DocumentStartApprove(doc=doc, data=resolution_flow_serializer.validated_data)
        res = process.run()
        serializer = DocumentSerializer(res)
        return Response(serializer.data)


class ResolutionDocumentView(APIView):
    @swagger_auto_schema(request_body=CreateFlowSerializer(), responses={200: DocumentSerializer(many=False)})
    def post(self, request, document_id):
        resolution_flow_serializer = CreateFlowSerializer(data=request.data)
        resolution_flow_serializer.is_valid(raise_exception=True)
        doc = BaseDocument.objects.get(pk=document_id)
        process = ResolutionDocument(doc=doc, data=resolution_flow_serializer.validated_data)
        res = process.run()
        serializer = DocumentSerializer(res)
        return Response(serializer.data)
