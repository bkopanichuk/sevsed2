from apps.document.models.document_model import BaseDocument, ON_EXECUTION
from apps.document.models.task_model import RUNNING
from apps.l_core.exceptions import ServiceException

import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

class ResolutionDocument:
    """Подати документ на резолюцію"""

    def __init__(self, doc, data):
        logger.info(f'INIT ResolutionDocument')
        self.document: BaseDocument = doc
        self.data = data

    def run(self):
        self.validate_flow()
        self.execute_document()
        self.start_flow()

        return self.document

    def validate_flow(self):
        flow = self.document.flow_set.all().last()
        logger.info(f'validate_flow : {flow.id}')
        tasks_exists = flow.tasks.all().exists()
        if not tasks_exists:
            raise ServiceException(f'Заборонена передача документа на виконання без резолюції')

    def start_flow(self):
        flow = self.document.flow_set.all().last()
        logger.info(f'start_flow : {flow.id}')
        flow.status = RUNNING
        flow.execution_type = self.data.get('execution_type')
        flow.save()

    def execute_document(self):
        self.document.status = ON_EXECUTION
        self.document.save(update_fields=['status'])