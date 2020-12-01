from django.conf.urls import *
from rest_framework import routers

from apps.document.api.viewsets.comment_view import CommentViewSet
from apps.document.api.viewsets.coverletter_view import CoverLetterSerializerViewSet
from apps.document.api.viewsets.document_base_view import BaseDocumentSerializerViewSet, DocumentConsiderationView, \
    ResolutionDocumentView, \
    DocumentStartApproveView, UploadDocumentViewSet, DocumentHistoryView, RegisterDocumentView
from apps.document.api.viewsets.document_file_view import DocumentFileViewSet
from apps.document.api.viewsets.documenttype_view import IncomingDocumentTypeSerializerViewSet, \
    OutgoingDocumentTypeSerializerViewSet,InnerDocumentTypeViewSet
from apps.document.api.viewsets.incoming_document_view import IncomingDocumentViewSet
from apps.document.api.viewsets.inner_document_view import InnerDocumentViewSet
from apps.document.api.viewsets.outgoing_document_view import OutgoingDocumentViewSet
from apps.document.api.viewsets.registration_views import RegistrationJournalViewSet, RegistrationJournalVolumeViewSet, \
    RegistrationMaskViewSet
from apps.document.api.viewsets.sign_view import SignSerializerViewSet
from apps.document.api.viewsets.task_view import TaskSerializerViewSet, FlowSerializerViewSet, DocumentFlowView, \
    TaskExecutorSerializerViewSet, ApproveTaskSerializerViewSet, ApproveFlowSerializerViewSet, ApproveDocumentFlowView,\
DocumentConciderationView,DocumentResolutionView

router = routers.DefaultRouter()

router.register(r'comment/(?P<document_id>[^/.]+)', CommentViewSet)
router.register(r'registration-journal', RegistrationJournalViewSet)
router.register(r'registration-mask', RegistrationMaskViewSet)
router.register(r'registration-journal-volume', RegistrationJournalVolumeViewSet)
router.register(r'base-document', BaseDocumentSerializerViewSet)
router.register(r'incoming-document', IncomingDocumentViewSet)
router.register(r'outgoing-document', OutgoingDocumentViewSet)
router.register(r'inner-document', InnerDocumentViewSet)
router.register(r'upload-document', UploadDocumentViewSet)
router.register(r'task', TaskSerializerViewSet)
router.register(r'approve-task', ApproveTaskSerializerViewSet)
router.register(r'task-executor', TaskExecutorSerializerViewSet)
router.register(r'flow', FlowSerializerViewSet)
router.register(r'approve-flow', ApproveFlowSerializerViewSet)
router.register(r'sign', SignSerializerViewSet)
router.register(r'incoming-type', IncomingDocumentTypeSerializerViewSet)
router.register(r'outgoing-type', OutgoingDocumentTypeSerializerViewSet)
router.register(r'inner-type', InnerDocumentTypeViewSet)
router.register(r'cover-letter', CoverLetterSerializerViewSet)
router.register(r'additional-file/(?P<document_id>[^/.]+)', DocumentFileViewSet)

urlpatterns = [

    url(r'document-history/(?P<document_id>[^/.]+)/$', DocumentHistoryView.as_view()),
    url(r'document-flow/(?P<document_id>[^/.]+)/$', DocumentFlowView.as_view()),
    url(r'document-resolution/(?P<document_id>[^/.]+)/$', DocumentResolutionView.as_view()),
    url(r'document-consideration/(?P<document_id>[^/.]+)/$', DocumentConciderationView.as_view()),
    url(r'approve-document-flow/(?P<document_id>[^/.]+)/$', ApproveDocumentFlowView.as_view()),
    url(r'action/register/(?P<document_id>[^/.]+)/$', RegisterDocumentView.as_view()),
    url(r'action/consideration/(?P<document_id>[^/.]+)/$', DocumentConsiderationView.as_view()),
    url(r'action/start-approve/(?P<document_id>[^/.]+)/$', DocumentStartApproveView.as_view()),
    url(r'action/resolution/(?P<document_id>[^/.]+)/$', ResolutionDocumentView.as_view()),

]

urlpatterns += router.urls
