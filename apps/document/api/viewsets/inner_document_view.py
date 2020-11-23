from __future__ import unicode_literals

from apps.document.models.document_model import BaseDocument
from ...models.document_constants import INNER
from .document_base_view import OrderingFilterMixin
from ..srializers.document_serializer import InnerDocumentSerializer


class InnerDocumentViewSet(OrderingFilterMixin):
    serializer_class = InnerDocumentSerializer
    queryset = BaseDocument.objects.filter(document_cast=INNER)
