from django.utils.timezone import localdate
from rest_framework.exceptions import ValidationError

from apps.document.models.document_model import COMPLETED, PASSED_CONTROL, CONCERTED,ON_EXECUTION
from apps.document.models.document_constants import INCOMING, OUTGOING
from apps.document.models.sign_model import Sign
from apps.document.models.task_model import PENDING, SUCCESS, RETRY, REJECT, RUNNING, MAIN, BY_ORDER, PARALLEL, \
    SIMPLE_SIGN
from apps.document.models.task_model import Task, Flow, TaskExecutor
from apps.l_core.exceptions import ServiceException
from apps.l_core.ua_sign import verify_external


class SetTaskParams:
    def __init__(self, task):
        self.task: Task = task
        self.parent = None

    def run(self):
        self.set_parent_task()
        self.set_task_status()

    def set_parent_task(self):
        if not self.task.parent_task:
            q = self.task.flow.tasks.all()

            if q.exists():
                # raise Exception(q)
                self.parent = q.latest('date_add')
                self.task.parent_task = self.parent

    def set_task_status(self):
        if self.task.task_status == SUCCESS:
            return

        if not self.parent and self.task.flow.status == RUNNING:
            self.task.task_status = RUNNING
            return


class SetTaskController:
    def __init__(self, task):
        self.task: Task = task

    def run(self):
        self.set_controller()

    def set_controller(self):
        if self.task.author_is_controller and self.task.author:
            self.task.controller = self.task.author


class SetTaskExecutorOrganization:
    def __init__(self, task_executor):
        self.task_executor: TaskExecutor = task_executor

    def run(self):
        self.set_organization()

    def set_organization(self):
        self.task_executor.organization = self.task_executor.task.organization


class SetChildStatus:
    def __init__(self, task):
        self.task: Task = task

    def run(self):
        self.set_child_task_status()

    def set_child_task_status(self):
        if self.task.task_status == SUCCESS:
            q = self.task.flow.tasks.filter(parent_task=self.task).exclude(task_status__in=[SUCCESS, RUNNING])
            if q.exists():
                self.child = q.earliest('date_add')
                self.child.task_status = RUNNING
                self.child.save()



class ApproveTask:
    """ Підтвердження виконання завдання"""
    def __init__(self, task, user,data):
        self.task: Task = task
        self.user = user
        self.data = data

    def run(self):
        self.validate_user()
        self.approve_task()
        self.change_document_status()
        return self.task

    def validate_user(self):
        if self.user != self.task.controller:
            raise ServiceException('Підтвердити виконання завдання може лише контролер!')

    def approve_task(self):
        self.task.is_controlled = True
        self.task.is_completed = True
        self.task.controller_comment = self.data.get('controller_comment')
        self.task.save()

    def change_document_status(self):
        ## Перевіряємо чи залишились невиконані завдання, якщо залишились то не знімаємо документ(завдання) контролю
        ## Інакше - знімаємо з контролю
        is_all_tasks_completed = (not self.task.document.task_set.filter(is_completed=False).exists())
        if is_all_tasks_completed:
            self.task.document.status = PASSED_CONTROL
            self.task.document.save()


class RetryTask:
    """Повернення завдання на доопрацювання"""
    def __init__(self, task, user,data):
        self.task: Task = task
        self.user = user
        self.data = data

    def run(self):
        self.validate_user()
        self.retry_task()
        self.retry_flow()
        self.change_document_status()
        return self.task

    def validate_user(self):
        """ Перевіряємо користувача, що відправив завдання на доопрацювання"""
        if self.user != self.task.controller:
            raise ServiceException('вернути завдання на доопрацювання може лише контролер!')

    def retry_task(self):
        """ Змінюємо статус завдання 'На доопрацювання'"""
        self.task.is_controlled = False
        self.task.is_completed = False
        self.task.task_status = RETRY
        self.task.controller_comment = self.data.get('controller_comment')
        self.task.save()

    def retry_flow(self):
        self.task.flow.status = RUNNING
        self.task.flow.save()

    def retry_task_executors(self):
        """ Переводимо виконавців завдання в активний статус, інакше виконавці не побачать що задача повернута на доопрацювання"""
        task_executors =  self.task.task_executors.all()
        task_executors.update(status= RETRY)

    def change_document_status(self):
        """ Повертаємо документ в статус  'На виконанні'"""
        self.task.document.status = ON_EXECUTION
        self.task.document.save()

class FinishExecution:
    """Завершити виконання завдання"""
    def __init__(self, task_executor, data, user):
        self.task_executor: TaskExecutor = task_executor
        self.data = data
        self.user = user

    def run(self):
        self.validate_user()
        self.finish_execution()
        self.finish_task()
        return self.task_executor

    def validate_user(self):
        if self.user != self.task_executor.executor:
            raise ServiceException('Задачу може виконувати тільки відповідальний за неї виконавець')

    def finish_execution(self):
        self.task_executor.status = SUCCESS
        if self.data.get('result'):
            self.task_executor.result = self.data.get('result')
        if self.data.get('result_file'):
            self.task_executor.result_file = self.data.get('result_file')
        self.task_executor.save()

    def save_sign(self):
        document = self.task_executor.task.document
        signer = self.task_executor.executor
        sign = self.task_executor.sign
        sign_info = self.task_executor.sign_info
        Sign.objects.create(document=document, signer=signer, sign=sign, sign_info=sign_info)

    def finish_task(self):
        if self.task_executor.executor_role == MAIN:
            if self.task_executor.result:
                self.task_executor.task.task_status = SUCCESS
                self.task_executor.task.execute_date = localdate()
                if not self.task_executor.task.controller:
                    self.task_executor.task.is_completed = True
                self.task_executor.task.save()
                self.save_sign()


class FinishApprove(FinishExecution):
    """ Завершити підтвердження позитивно"""

    def run(self):
        self.validate_user()
        self.finish_execution()
        self.set_simple_result()
        self.finish_approve()
        return self.task_executor

    def finish_execution(self):
        self.task_executor.sign = self.data.get('sign')
        self.check_sign()
        self.validate_sign()
        self.task_executor.status = SUCCESS
        self.task_executor.result = self.data.get('result')
        self.task_executor.save()

    def set_simple_result(self):
        if self.task_executor.approve_method == SIMPLE_SIGN:
            self.task_executor.result = self.data.get('result', 'Підтверджено')

    def validate_sign(self):
        sign_b64 = self.task_executor.sign
        data_path = self.task_executor.task.document.main_file.path
        res = verify_external(data_path=data_path, sign_data=sign_b64)
        if res.get('code') == 1:
            raise ServiceException(res.get('code_message'))
        self.task_executor.sign_info = res

    def check_sign(self):
        if self.task_executor.approve_method == SIMPLE_SIGN:
            return
        if not self.task_executor.sign:
            raise ValidationError({'sign': 'Цифровий підпис обовязковий'})

    def finish_approve(self):
        if self.task_executor.executor_role == MAIN:
            self.task_executor.task.task_status = SUCCESS
            self.task_executor.task.execute_date = localdate()
            if not self.task_executor.task.controller:
                self.task_executor.task.is_completed = True
            self.task_executor.task.save()


class RejectApprove(FinishExecution):
    """ Завершити підтвердження негативно"""

    def run(self):
        self.validate_user()
        self.reject_execution()
        self.reject_task()
        self.reject_flow()
        return self.task_executor

    def reject_execution(self):
        self.task_executor.status = REJECT
        self.task_executor.result = self.task_executor.result = self.data.get('result', 'Відмовлено')
        self.task_executor.save()

    def reject_task(self):
        if self.task_executor.executor_role == MAIN:
            self.task_executor.task.is_completed = True
            self.task_executor.task.task_status = REJECT
            self.task_executor.task.save()

    def reject_flow(self):
        if self.task_executor.executor_role == MAIN:
            self.task_executor.task.flow.status = REJECT
            self.task_executor.task.flow.save()
            self.remove_all_signs()

    def remove_all_signs(self):
        document = self.task_executor.task.document
        q = Sign.objects.filter(document=document)
        q.delete()


class HandleExecuteTask:
    def __init__(self, task):
        self.task: Task = task

    def run(self):
        if self.task.flow.status != RUNNING:
            return
        self.close_flow_if_last_task()

    def close_flow_if_last_task(self):
        if self.task.task_status == SUCCESS:
            if not self.task.flow.tasks.filter(task_status__in=[PENDING, RUNNING, RETRY]).exists():
                self.task.flow.status = SUCCESS
                self.task.flow.save()
                # self.change_document_status()


class HandleExecuteFlow:
    def __init__(self, flow):
        self.flow: Flow = flow

    def run(self):
        self.close_document_if_flow_success()

    def close_document_if_flow_success(self):
        if self.flow.status == SUCCESS:
            if self.flow.document.document_cast == INCOMING:
                self.change_incoming_document_status()
            elif self.flow.document.document_cast == OUTGOING:
                self.change_outgoing_document_status()
        elif self.flow.status == REJECT:
            self.reject_document_if_flow_rejected()

    def change_incoming_document_status(self):
        ## Переносимо документ в статус "знято з контролю" якщо немає контролерів
        is_not_controllers = (
            not self.flow.document.task_set.filter(controller__isnull=False, task_status=SUCCESS).exists())
        if is_not_controllers:
            self.flow.document.status = PASSED_CONTROL
            self.flow.document.save()
        else:
            ## Якщо контролери вказані
            self.flow.document.status = COMPLETED
            self.flow.document.save()

    def reject_document_if_flow_rejected(self):
        self.flow.document.status = REJECT
        self.flow.document.save()

    def change_outgoing_document_status(self):
        self.flow.document.status = CONCERTED
        self.flow.document.save()


class HandleRunFlow:
    def __init__(self, flow):
        self.flow: Flow = flow

    def run(self):
        if self.flow.execution_type == BY_ORDER:
            self.run_first_task_if_flow_running()
        elif self.flow.execution_type == PARALLEL:
            self.run_all_flow_tasks()
        else:
            raise ServiceException('Не вказано "execution_type"')

    def run_first_task_if_flow_running(self):
        if self.flow.status == RUNNING:
            q = self.flow.tasks.filter(parent_task=None).exclude(task_status__in=[RUNNING, RETRY, SUCCESS])
            if q.exists():
                first_task = q.first()
                first_task.task_status = RUNNING
                first_task.save()

    def run_all_flow_tasks(self):
        if self.flow.status == RUNNING:
            q = self.flow.tasks.exclude(task_status__in=[RUNNING, RETRY, SUCCESS])
            for task in q:
                task.task_status = RUNNING
                task.save()


class ExecuteTask:
    def __init__(self, task, user, data):
        self.task: Task = task
        self.user = user
        self.data = data

    def run(self):
        if self.task.flow.status != RUNNING:
            return

        self.validate_task_status()
        self.validate_task_executor()
        self.validate_task_content()
        self.validate_task_execute_date()
        self.change_task_status()
        return self.task

    def validate_task_status(self):
        if self.task.task_status == SUCCESS:
            raise ServiceException(f'Резолюція вже виконана, Ви не можете виконати її повторно.')

        if self.task.task_status == PENDING:
            raise ServiceException(
                f'Ви не можете виконати резоліюцію оскільки попередня резолюція по цьому документу ще не виконана.')

    def validate_task_executor(self):
        user_in_task_executor_list = self.task.task_executors.all().filter(executor=self.user).exists()
        if not user_in_task_executor_list:
            raise ServiceException(f'Заборонено виконання завдання користувачами не вказаними в списку виконанвців.')

    def validate_task_content(self):
        pass
        # if not self.data.get('content'):
        #     raise ValidationError({'content': 'Не заповнено  результат виконання завдання.'})
        # self.task.content = self.data.get('content')

    def validate_task_execute_date(self):

        if self.data.get('execute_date') > localdate():
            raise ValidationError({'execute_date': 'Вказана Вами дата перевищує поточну, вкажіть правильну дату.'})
        self.task.execute_date = self.data.get('execute_date')

    def change_task_status(self):
        main_executor = self.task.task_executors.filter(executor_role=MAIN).first()
        if main_executor.executor == self.user:
            self.task.task_status = SUCCESS

    def save_result(self):
        self.task.save()
