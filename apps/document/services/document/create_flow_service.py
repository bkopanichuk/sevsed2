import logging

from apps.document.models.document_constants import INNER
from apps.document.models.document_model import BaseDocument
from apps.document.models.task_model import Flow, EXECUTE, PENDING, FlowApprove,SUCCESS

# Get an instance of a logger
logger = logging.getLogger(__name__)


class CreateFlow:
    """Створити процес виконання завдання, або підтвердження(залежно від параметру goal)
    Примітка: до виконання відноситься також візування та підпис докумету
    """

    def __init__(self, doc, goal=None):
        self.document: BaseDocument = doc
        self.flow = Flow
        self.goal = goal or EXECUTE
        self.approvers_list = self.document.approvers_list.all()

    def run(self):
        return self.create_flow()

    def check_if_exist_success_flow(self):
        success_q = self.flow.objects.filter(status=SUCCESS, document=self.document, goal=self.goal)
        return success_q.exists()


    def create_flow(self):
        ## Якщо існуюючий процесс успішно завершено не створюємо новий
        if self.check_if_exist_success_flow():
            return
        ## Додати новий процес розгляду, або повернути існуючий
        flow_q = self.flow.objects.filter(status=PENDING, document=self.document, goal=self.goal)
        if flow_q.exists():
            flow = flow_q.first()
            flow.goal = self.goal
            flow.save()
            flow.approvers_list.clear()
        else:
            # if self.document.document_cast == INNER and self.goal==EXECUTE:
            flow = self.flow.objects.create(author=self.document.author or self.document.editor, status=PENDING,
                                            document=self.document,
                                            goal=self.goal)

        if not self.approvers_list:
            return flow

        flow.approvers_list.add(*self.approvers_list)
        ## Код що нижче додає список розглядачів, для відображення на клієнті.
        ## TODO Автоматично змінювати статус розгляду при відкритті документа розглядачем

        for approver in self.approvers_list:
            if not FlowApprove.objects.filter(flow=flow, approver=approver).exists():
                FlowApprove.objects.create(author=self.document.author or self.document.editor, status=PENDING,
                                           flow=flow, approver=approver)
        logger.error(f'CREATE APPROVE FLOW, goal = {flow.goal}')
        return flow
