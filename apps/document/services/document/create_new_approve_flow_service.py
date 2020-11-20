from apps.document.models.document_constants import OUTGOING, INNER
from apps.document.models.document_model import BaseDocument, ON_AGREEMENT
from apps.document.services import CreateFlow
from apps.l_core.exceptions import ServiceException


class DocumentCreateNewApproveFlow:
    """ Відкрити новий процес погодження """

    def __init__(self, doc):
        self.document: BaseDocument = doc

    def run(self):
        self.validate_document_cast()
        self.validate_status()
        self.create_approve_flow()
        return self.document

    def validate_document_cast(self):
        if self.document.document_cast not in [OUTGOING, INNER]:
            raise ServiceException('На погодження можна відправити лише Внутрішній, або Вихідний документ')

    def validate_status(self):
        if self.document.status == ON_AGREEMENT:
            raise ServiceException(
                f'Документ вже запушено на погодження. Ви не можете запустити погодження доки попередній процес погодження не закінчено.')

    def create_approve_flow(self):
        flow = CreateFlow(self.document)
        flow.run()