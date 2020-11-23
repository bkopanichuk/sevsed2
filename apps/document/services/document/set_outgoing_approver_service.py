from apps.document.models.document_model import BaseDocument
from apps.document.models.document_constants import OUTGOING,INNER
import logging
logger = logging.getLogger(__name__)

class SetOutgoingApproval:
    """Назначити власником процесу погодження автора документа, якщо це вихідний документ, або внутрішній
    """
    def __init__(self, doc):
        self.document: BaseDocument = doc

    def run(self):
        return self.set_approval()

    def set_approval(self):
        logger.info('SetOutgoingApproval')
        if self.document.document_cast in [OUTGOING,INNER]:
            self.document.approvers_list.add(self.document.author)