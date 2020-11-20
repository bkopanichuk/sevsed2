import logging

from apps.document.models.document_model import BaseDocument, ON_AGREEMENT, WITH_APPROVE
from apps.document.models.task_model import APPROVE, RUNNING,PENDING, Task, TaskExecutor, MAIN, SIGN, SIMPLE_SIGN,DIGIT_SIGN

from apps.document.services import CreateFlow
from apps.l_core.exceptions import ServiceException

# Get an instance of a logger
logger = logging.getLogger(__name__)


class DocumentStartApprove:
    """Почати погодження документа"""

    def __init__(self, doc, data):
        self.document: BaseDocument = doc
        self.data = data

    def run(self):
        self.validate_main_file()
        self.validate_status()
        self.validate_main_signer()
        self.validate_approve_list()
        self.start_approve_document()
        self.create_approve_flow()
        return self.document


    def validate_main_file(self):
        if not self.document.main_file:
            raise ServiceException(
            f'Спочатку завантажте документ для узгодження')

    def validate_status(self):
        if self.document.status == ON_AGREEMENT:
            raise ServiceException(
                f'Документ вже запушено на погодження. Ви не можете запустити погодження доки попередній процес погодження не закінчено.')

    def validate_main_signer(self):
        if not self.document.main_signer:
            raise ServiceException(
                f'Спочатку вкажіть підписанта документа')

    def create_task_if_main_signer_exist(self, flow):
        ## Перевіряємо чи ще немає задачі на підпис в головного підписанта
        q = Task.objects.filter(flow=flow,
                        task_type=APPROVE,
                        goal=APPROVE,
                        approve_type=SIGN,
                                task_executors__executor=self.document.main_signer,
                                task_executors__approve_method = DIGIT_SIGN)

        ## Якщо задача вже існує не продовжуємо виконання функції
        if q.exists():
            return

        if self.document.main_signer:
            ## Створюємо завдання на підпис
            task = Task(document=self.document,
                        flow=flow,
                        task_type=APPROVE,
                        goal=APPROVE,
                        approve_type=SIGN,
                        task_status=PENDING,
                        author=self.document.author,
                        organization=self.document.organization
                        )
            task.save()
            ## Прописуємо виконавцем завдання головного підписанта
            task_executor = TaskExecutor(task=task,
                                         executor=self.document.main_signer,
                                         executor_role=MAIN,
                                         author=self.document.author,
                                         organization=self.document.organization,
                                         approve_method = DIGIT_SIGN
                                         )
            task_executor.save()
            ##Якщо
            ##if task.flow.tasks.count()>0:
            ##task.task_status = PENDING
            #task.save()

    def validate_approve_list(self):
        ##Якщо вказано підписанта, не перевіряємо список завдань, завдання буде створено автоматично
        if self.document.main_signer:
            return

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
        flow.execution_type = self.data.get('execution_type')
        self.create_task_if_main_signer_exist(flow)
        flow.status = RUNNING
        flow.save()

