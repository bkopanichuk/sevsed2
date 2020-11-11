from __future__ import unicode_literals

from apps.document.models.document_model import BaseDocument
from ...models.document_constants import INNER
from .incoming_document_view import IncomingDocumentViewSet


class InnerDocumentViewSet(IncomingDocumentViewSet):
    queryset = BaseDocument.objects.filter(document_cast=INNER)
