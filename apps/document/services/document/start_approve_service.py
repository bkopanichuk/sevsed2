from apps.document.models.document_model import BaseDocument, ON_AGREEMENT, WITH_APPROVE
from apps.document.models.task_model import APPROVE, RUNNING
from apps.document.services import CreateFlow
from apps.l_core.exceptions import ServiceException


class DocumentStartApprove:
    """Почати погодження документа"""

    def __init__(self, doc, data):
        self.document: BaseDocument = doc
        self.data = data

    def run(self):
        self.validate_approve_list()
        self.start_approve_document()
        self.create_approve_flow()
        return self.document

    def validate_status(self):
        if self.document.status == ON_AGREEMENT:
            raise ServiceException(
                f'Документ вже запушено на погодження. Ви не можете запустити погодження доки попередній процес погодження не закінчено.')

    def validate_approve_list(self):
        if self.document.approve_type == WITH_APPROVE:
            exist_approve_task = self.document.task_set.filter(task_type=APPROVE).exists()
            if not exist_approve_task:
                raise ServiceException(
                    f'Документ з погодженням повинен включати хоча б один пункт етап погодження.Спочатку вкажіть пункти погодження')

    def start_approve_document(self):
        self.document.status = ON_AGREEMENT
        self.document.save(update_fields=['status'])

    def create_approve_flow(self):
        flow = CreateFlow(self.document, goal=APPROVE)
        res = flow.run()
        self.start_flow(res)

    def start_flow(self, flow):
        flow.status = RUNNING
        flow.execution_type = self.data.get('execution_type')
        flow.save()