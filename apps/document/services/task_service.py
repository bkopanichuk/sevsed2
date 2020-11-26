from django.utils.timezone import localdate
import base64
from django.db.models import Max, Min
from rest_framework.exceptions import ValidationError

from apps.document.models.document_model import COMPLETED, PASSED_CONTROL, CONCERTED, ON_EXECUTION, ON_REGISTRATION, \
    ON_CONTROL, \
    ON_AGREEMENT
from apps.document.models.document_constants import INCOMING, OUTGOING, INNER
from apps.document.models.sign_model import Sign
from apps.document.models.task_model import PENDING, SUCCESS, RETRY, REJECT, RUNNING, MAIN, BY_ORDER, PARALLEL, \
    SIMPLE_SIGN, SIGN, DIGIT_SIGN
from apps.document.models.task_model import Task, Flow, TaskExecutor
from apps.l_core.exceptions import ServiceException
from apps.l_core.ua_sign import verify_external

import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)


class SetTaskParams:
    def __init__(self, task):
        logger.info(f'INIT   SetTaskParams')
        self.task: Task = task
        self.parent = None

    def run(self):
        # self.set_parent_task()
        self.set_order()
        self.set_task_status()

    def set_order(self):
        if self.task.order:
            return
        res = self.task.flow.tasks.aggregate(Max('order'))
        logger.info(f'order aggregate: {res}')
        order__max = res.get('order__max') or 0
        logger.info(f'order__max: {order__max}')
        self.task.order = order__max + 1
        logger.info(f'self.task.order: {self.task.order}')

    # def set_parent_task(self):
    #     logger.info(f'set_parent_task')
    #     ## Перевіряємо чи встановлена задача вище по ієрархії
    #     if not self.task.parent_task:
    #         ## перевіряємо чи існують задачів потоці виконання
    #         q = self.task.flow.tasks.all().exclude(id=self.task.id)
    #         logger.info(f'parent_tasks_q {q}')
    #         if q.exists():
    #             ## Якщо задачі існують, вибираємо найдавнішу
    #             latest_task =  q.latest('date_add')
    #             logger.info(f'latest_task: {latest_task}')
    #             ## Якщо не встановлено дату створення, або дата створення бульша за найдавнішу існуючу,
    #             # встановлюємо батьківську найдавнішу
    #             if not self.task.date_add or self.task.date_add > latest_task.date_add:
    #                 self.parent = q.latest('date_add')
    #                 self.task.parent_task = self.parent
    #
    #         logger.info(f'self.parent {self.parent}')
    #         logger.info(f'self.task.parent_task {self.task.parent_task}')

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
        self.set_end_date()

    def set_controller(self):
        if self.task.author_is_controller:
            self.task.controller = self.task.editor or self.task.author

    def set_end_date(self):
        if not self.task.end_date:
            self.task.end_date = self.task.document.reply_date


class SetInitialTaskExecutorParams:
    def __init__(self, task_executor):
        self.task_executor: TaskExecutor = task_executor

    def run(self):
        self.set_organization()
        self.set_end_date()

    def set_organization(self):
        self.task_executor.organization = self.task_executor.task.organization

    def set_end_date(self):
        if not self.task_executor.end_date:
            self.task_executor.end_date = self.task_executor.task.end_date


class SetChildStatus:
    """Змінити статус дочірніх завдань"""

    def __init__(self, task):
        self.task: Task = task

    def run(self):
        self.set_child_task_status()

    def set_child_task_status(self):
        """Відмітити """
        logger.info(f'set_child_task_status:  -  task_status: {self.task.task_status}')
        if self.task.task_status == SUCCESS:
            q = self.task.flow.tasks.filter(parent_task=self.task)  ##.exclude(task_status__in=[SUCCESS, RUNNING])
            if q.exists():
                self.child = q.earliest('date_add')
                self.child.task_status = SUCCESS
                self.child.save()


class ChangeTaskOrder:
    """Змінити порядок виконання завдань"""

    ## TODO Додати функціональність зміни порядку виконання завдан
    def __init__(self, task: Task, order: str):
        self.task: Task = task
        self.order = order

    def run(self):
        self.change_order()

    def change_order(self):
        """змінити порядок """
        pass

    def down_order(self):
        """підняти задачу на пункт вище"""
        pass

    def up_order(self):
        """опустити задачу на пункт нижче"""
        pass


class ApproveTask:
    """ Підтвердження виконання завдання"""

    def __init__(self, task, user, data):
        logger.info(f'START: ApproveTask------------------------------------')
        self.task: Task = task
        self.user = user
        self.data = data

    def run(self):
        self.validate_user()
        self.approve_task()
        self.change_document_status()
        logger.info(f'FINISH: ApproveTask-----------------------------------')
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
        # logger.debug(self.task.document.task_set.filter(is_completed=False).query)
        logger.info(f'is_all_tasks_completed = {is_all_tasks_completed} ')
        if is_all_tasks_completed:
            self.task.document.status = PASSED_CONTROL
            self.task.document.save()


class RetryTask:
    """Повернення завдання на доопрацювання"""

    def __init__(self, task, user, data):
        self.task: Task = task
        self.user = user
        self.data = data

    def run(self):
        self.validate_user()
        self.retry_task()
        self.retry_task_executors()
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
        """ Переводимо виконавців завдання в активний статус,
         інакше виконавці не побачать що задача повернута на доопрацювання"""
        task_executors = self.task.task_executors.all()
        task_executors.update(status=RETRY)

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

    def finish_task(self):
        if self.task_executor.executor_role == MAIN:
            if self.task_executor.result:
                self.task_executor.task.task_status = SUCCESS
                self.task_executor.task.execute_date = localdate()
                if not self.task_executor.task.controller:
                    self.task_executor.task.is_completed = True
                self.task_executor.task.save()


class FinishApprove(FinishExecution):
    """ Завершити підтвердження позитивно"""

    def run(self):
        self.validate_user()
        self.validate_data()
        self.validate_signer()
        self.finish_execution()
        self.set_simple_result()
        self.finish_approve()
        return self.task_executor

    def validate_data(self):
        if self.task_executor.task.approve_type == SIGN and self.task_executor.approve_method == DIGIT_SIGN:
            if not self.data.get('sign_file') and not self.data.get('sign'):
                raise ServiceException('Завантажте файл з підписом, або підпишіть скориставшись віджетом підпису')

    def validate_signer(self):
        ##TODO додати перевірку підписанта чи співпадаться реквізити в ЕЦП з вказаним підписантом
        pass

    def extract_sign_from_file(self):
        if self.data.get('sign_file'):
            sign_file = self.data.get('sign_file')
            self.task_executor.sign_file = sign_file
            sign_b64 = base64.b64encode(sign_file.read()).decode()
            self.task_executor.sign = sign_b64

    def finish_execution(self):
        if self.data.get('sign_file') and not self.data.get('sign'):
            self.extract_sign_from_file()
        else:
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

    def save_sign(self):
        if self.task_executor.approve_method == DIGIT_SIGN:
            document = self.task_executor.task.document
            signer = self.task_executor.executor
            sign = self.task_executor.sign
            sign_info = self.task_executor.sign_info
            Sign.objects.create(document=document, signer=signer, sign=sign, sign_info=sign_info)

    def finish_approve(self):
        if self.task_executor.executor_role == MAIN:
            self.task_executor.task.task_status = SUCCESS
            self.task_executor.task.execute_date = localdate()
            if not self.task_executor.task.controller:
                self.task_executor.task.is_completed = True
            self.task_executor.task.save()
        self.save_sign()


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
        logger.warning('START HandleExecuteTask: -------------------------')
        self.task: Task = task

    def run(self):
        if self.task.flow.status != RUNNING:
            return
        self.close_flow_if_last_task()
        logger.warning('FINISH HandleExecuteTask: -------------------------')

    def close_flow_if_last_task(self):
        if self.task.task_status == SUCCESS:
            if not self.task.flow.tasks.filter(task_status__in=[PENDING, RUNNING, RETRY]).exists():
                self.task.flow.status = SUCCESS
                self.task.flow.save()
                # self.change_document_status()
            self.run_next_task_if_this_success()

    def run_next_task_if_this_success(self):
        logger.info(f'run_next_task_if_this_success')
        q = self.task.flow.tasks.filter(task_status__in=[PENDING, RUNNING, RETRY]).exclude(id=self.task.id)
        if q.exists():
            res = q.aggregate(Min('order'))
            order__min = res.get('order__min')
            if order__min:
                task_by_order = self.task.flow.tasks.get(order=order__min)
                task_by_order.task_status = RUNNING
                task_by_order.save()


# class RunNextTask:
#     def __init__(self, task_executor):
#         logger.info(f'INIT RunNextTask')
#         self.task_executor: TaskExecutor = task_executor
#         self.task = self.task_executor.task
#
#     def run(self):
#         logger.info(f'self.task.task_status: {self.task.task_status}')
#
#
#     def set_succes_status_if_main(self):
#         if self.task_executor.status == SUCCESS:
#             if self.task.task_status == SUCCESS:
#                 self.run_next_task_if_this_success()
#
#
#     def run_next_task_if_this_success(self):
#         logger.info(f'run_next_task_if_this_success')
#         q = self.task.flow.tasks.filter(task_status__in=[PENDING,RUNNING,RETRY]).exclude(id = self.task.id)
#         if q.exists():
#             res= q.aggregate(Min('order'))
#             order__min = res.get('order__min')
#             if order__min:
#                 task_by_order = self.task.flow.tasks.get(order=order__min)
#                 task_by_order.task_status = RUNNING
#                 task_by_order.save()


class HandleExecuteFlow:
    def __init__(self, flow):
        logger.warning('START HandleExecuteFlow: -------------------------')
        self.flow: Flow = flow

    def run(self):
        self.close_document_if_flow_success()
        logger.warning('FINISH HandleExecuteTask: -------------------------')

    def close_document_if_flow_success(self):
        if self.flow.status == SUCCESS:
            if self.flow.document.document_cast == INCOMING:
                self.change_incoming_document_status()
            elif self.flow.document.document_cast == OUTGOING:
                self.change_outgoing_document_status()
            elif self.flow.document.document_cast == INNER:
                self.change_inner_document_status()
        elif self.flow.status == REJECT:
            self.reject_document_if_flow_rejected()

    def change_incoming_document_status(self):
        self.change_on_control_document_status()
        self.flow.document.save()

    def change_on_control_document_status(self):
        ## Переносимо документ в статус "знято з контролю" якщо немає контролерів
        is_not_controllers = (
            not self.flow.document.task_set.filter(controller__isnull=False, task_status=SUCCESS).exists())
        if is_not_controllers:
            self.flow.document.status = PASSED_CONTROL
        else:
            ## Якщо контролери вказані
            self.flow.document.status = COMPLETED

    def reject_document_if_flow_rejected(self):
        self.flow.document.status = REJECT
        self.flow.document.save()

    def change_outgoing_document_status(self):
        self.flow.document.status = ON_REGISTRATION
        self.flow.document.save()

    def change_inner_document_status(self):
        logger.info(f' document status before change: {self.flow.document.status}')
        if self.flow.document.status == ON_EXECUTION:
            self.change_on_control_document_status()
        if self.flow.document.status == ON_AGREEMENT:
            self.flow.document.status = ON_REGISTRATION
        logger.info(f' document status after change: {self.flow.document.status}')
        self.flow.document.save()


class HandleRunFlow:
    """Обробник сигналу запуску пректу завдань на виконання"""

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
        logger.info(f'run_first_task_if_flow_running')
        logger.info(f'flow status:  {self.flow.status}')
        if self.flow.status == RUNNING:
            q = self.flow.tasks.filter(parent_task=None).exclude(task_status__in=[RUNNING, RETRY, SUCCESS])
            logger.info(f'all flow (id:{self.flow.id}) tasks:  {self.flow.tasks.all()}')
            logger.info(f'task_status__in=[RUNNING, RETRY, SUCCESS]:  {q}')
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
