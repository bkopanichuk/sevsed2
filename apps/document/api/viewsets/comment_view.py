from __future__ import unicode_literals

from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.request import QueryDict

from apps.document.api.srializers.comment_serializer import CommentSerializer
from apps.document.models.comment_model import Comment
from apps.l_core.api.base.serializers import BaseOrganizationViewSetMixing


class CommentViewSet(BaseOrganizationViewSetMixing):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter, OrderingFilter)
    ordering_fields = ['date_add',]
    ordering = ['date_add']

    def get_queryset(self):
        q = super(CommentViewSet, self).get_queryset()
        return q.filter(document__id=self.document_id)

    def list(self, request, document_id, *args, **kwargs):
        self.document_id = int(document_id)
        return super(CommentViewSet, self).list(request, *args, **kwargs)

    def create(self, request, document_id, *args, **kwargs):
        if isinstance(request.data, QueryDict):
            setattr(request.data, '_mutable', True)
        self.document_id = int(document_id)
        request.data['document'] = self.document_id
        return super(CommentViewSet, self).create(request, *args, **kwargs)

    def destroy(self, request, document_id, *args, pk=None, **kwargs):
        if isinstance(request.data, QueryDict):
            setattr(request.data, '_mutable', True)
        self.document_id = int(document_id)
        request.data['document'] = self.document_id
        return super(CommentViewSet, self).destroy(request, *args, pk=None, **kwargs)

    def retrieve(self, request, document_id, *args, **kwargs):
        if isinstance(request.data, QueryDict):
            setattr(request.data, '_mutable', True)
        self.document_id = int(document_id)
        request.data['document'] = self.document_id
        return super(CommentViewSet, self).retrieve(request, *args, **kwargs)
