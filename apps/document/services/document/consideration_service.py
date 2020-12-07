from apps.l_core.exceptions import ServiceException
from apps.document.models.document_constants import INCOMING, INNER
from apps.document.models.document_model import BaseDocument, ON_RESOLUTION
from apps.document.services import CreateFlow


class DocumentConsideration:
    """Передати документ на розгляд"""
    def __init__(self, doc):
        self.document: BaseDocument = doc

    def run(self):
        self.validate_approvers()
        self.considerate_document()
        return self.document

    def validate_approvers(self):
        approvers = self.document.approvers_list.all()
        if not approvers.exists():
            raise ServiceException(f'Заборонено погодження  документа без вказаного списку на розгляд.')

    def considerate_document(self):
        if self.document.document_cast == INCOMING:
            self.considerate_incoming_document()
        elif self.document.document_cast == INNER:
            self.considerate_inner_document()
        else:
            raise ServiceException('document_cast is not set')

    def considerate_incoming_document(self):
        self.document.status = ON_RESOLUTION
        self.document.save(update_fields=['status'])

    def considerate_inner_document(self):
        self.document.status = ON_RESOLUTION
        self.document.save(update_fields=['status'])
        process = CreateFlow(doc=self.document)
        process.run()
