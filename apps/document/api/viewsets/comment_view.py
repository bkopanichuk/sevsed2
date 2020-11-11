from __future__ import unicode_literals

from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.document.api.srializers.comment_serializer import CommentSerializer
from apps.document.models.comment_model import Comment
from apps.l_core.api.base.serializers import BaseViewSetMixing


class CommentViewSet(BaseViewSetMixing):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter, OrderingFilter)
