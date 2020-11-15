from apps.document.models.document_model import BaseDocument
from apps.document.models.document_constants import OUTGOING
import logging
logger = logging.getLogger(__name__)

class SetOutgoingApproval:
    """Назначити власником процесу погодження автора документа, якщо це вихідний документ
    """
    def __init__(self, doc):
        self.document: BaseDocument = doc

    def run(self):
        return self.set_approval()

    def set_approval(self):
        logger.info('SetOutgoingApproval')
        if self.document.document_cast == OUTGOING:
            self.document.approvers_list.add(self.document.author)