import os
from django.db import models
from django.utils.timezone import localdate
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import JSONField
from simple_history.models import HistoricalRecords
from apps.document.models.document_constants import CustomTaskPermissions
from apps.document.models.document_model import BaseDocument
from apps.l_core.models import CoreBase, CoreUser

###########################################TASK_GOAL####################################################################
EXECUTE = "EXECUTE"
APPROVE = "APPROVE"
TASK_GOAL = [(EXECUTE, "На виконання"), (APPROVE, "Погодження")]
########################################################################################################################
######################################TASK_TYPE#########################################################################
TASK = "TASK"
TASK_TYPE = [(TASK, "Виконання завданя"), (APPROVE, "Погодження документа")]
########################################################################################################################
###########################################EXECUTION_TYPE###############################################################
PARALLEL = "PARALLEL"
BY_ORDER = "BY_ORDER"
EXECUTION_TYPE = [(PARALLEL, "Паралельно"), (BY_ORDER, "Послідовно")]
########################################################################################################################

MAIN = "MAIN"
CO_MAIN = "CO_MAIN"
INFORMATION = "INFORMATION"
EXECUTOR_ROLE = [(MAIN, "Головний"), (CO_MAIN, "Співвиконавець"), (INFORMATION, "Для інформації")]

PENDING = "PENDING"
RUNNING = "RUNNING"
SUCCESS = "SUCCESS"
RETRY = "RETRY"
REJECT = "REJECT"
TASK_STATUS = [(PENDING, "Формується"), (RUNNING, "Виконується"), (SUCCESS, "Виконана"),
               (RETRY, "На доопрацювання"), (REJECT, "Скасована")]

#################################################TASK_EXECUTOR_STATUS###################################################
TASK_EXECUTOR_STATUS = [(PENDING, "Очукується виконання"),
                        (RUNNING, "Виконується"),
                        (SUCCESS, "Виконана"),
                        (RETRY, "Доопрацювання"),
                        (REJECT, "Відхилено")]
#################################################FLOW_STATUS№###########################################################

#################################################FLOW_STATUS№###########################################################
FLOW_STATUS = [(PENDING, "Проект"), (RUNNING, "Виконується"), (SUCCESS, "Виконана"),
               (REJECT, "Відхилено")]
########################################################################################################################

#################################################FLOW_APPROVE_STATUS№###################################################
APPROVE_STATUS = [(PENDING, "Очікує підтвердження"), (SUCCESS, "Підтверджено"),
                  (REJECT, "Відхилено")]
########################################################################################################################
#################################################APPROVE_TYPE###########################################################
APPROVE = "APPROVE"
SIGN = "SIGN"
APPROVE_TYPE = [(APPROVE, "Візування"), (SIGN, "Підпис")]
########################################################################################################################
################################################APPROVE_METHODS#########################################################
SIMPLE_SIGN = "SIMPLE_SIGN"
DIGIT_SIGN = "DIGIT_SIGN"
APPROVE_METHODS = [(SIMPLE_SIGN, "Звичайне підтвердження"), (DIGIT_SIGN, "Накладання ЕЦП")]
########################################################################################################################
User = get_user_model()


class Flow(CoreBase):
    goal = models.CharField(verbose_name="Тип завдання", choices=TASK_GOAL, default=EXECUTE,
                            max_length=20)
    document = models.ForeignKey(BaseDocument, verbose_name="До документа", on_delete=models.CASCADE, null=True,
                                 blank=True)
    approvers_list = models.ManyToManyField(User, verbose_name='На розгляд')
    status = models.CharField(max_length=50, choices=FLOW_STATUS, verbose_name='Сатус')
    execution_type = models.CharField(verbose_name="Спосіб виконання", choices=EXECUTION_TYPE, default=BY_ORDER,
                                      max_length=20)

    class Meta:
        unique_together = ('id', 'document')


class FlowApprove(CoreBase):
    flow = models.ForeignKey(Flow, related_name='approvers', on_delete=models.CASCADE)
    approver = models.ForeignKey(User, verbose_name='На розгляд', on_delete=models.PROTECT)
    status = models.CharField(max_length=50, choices=APPROVE_STATUS, verbose_name='Сатус')

    class Meta:
        verbose_name = 'Підтвердження розгляду'

    def __str__(self):
        return self.approver.__str__()


class Task(CoreBase):
    goal = models.CharField(verbose_name="Тип завдання", choices=TASK_GOAL, default=EXECUTE,
                            max_length=20)
    flow = models.ForeignKey(Flow, related_name='tasks', on_delete=models.CASCADE, null=True, blank=True)
    task_status = models.CharField(verbose_name="Статус завдання", choices=TASK_STATUS, max_length=100, default=PENDING)
    document = models.ForeignKey(BaseDocument, verbose_name="До документа", on_delete=models.CASCADE, null=True,
                                 blank=True)
    parent_task = models.ForeignKey('self', related_name='p_task', verbose_name="Резолюція залежна від",
                                    on_delete=models.SET_NULL, null=True, blank=True)
    order = models.PositiveSmallIntegerField(default=0, verbose_name="Порядок виконання завдань")
    # To save hierarchy in UI
    parent_node = models.ForeignKey('self', related_name='p_node', verbose_name="Резолюція до",
                                    on_delete=models.SET_NULL, null=True, blank=True)
    is_completed = models.BooleanField(verbose_name="Чи виконано", default=False)
    title = models.CharField(verbose_name="Завдання", max_length=200)
    controller = models.ForeignKey(CoreUser, related_name='%(class)s_controller', blank=True,
                                   verbose_name="Контролер", on_delete=models.PROTECT, null=True)
    author_is_controller = models.BooleanField(default=False, verbose_name="Я контролер")
    is_controlled = models.BooleanField(verbose_name="Чи перевірено", default=False)
    task_type = models.CharField(verbose_name="Тип завдання", choices=TASK_TYPE, default=TASK, max_length=20)
    start_date = models.DateField(verbose_name="Термін з", null=True, auto_now_add=True)
    end_date = models.DateField(verbose_name="Термін до", null=True, default=None, blank=True)
    execute_date = models.DateField(verbose_name="Дата фактичного виконання", null=True)
    approve_type = models.CharField(verbose_name="Тип підтвердження", choices=APPROVE_TYPE, default=APPROVE, max_length=10)
    controller_comment = models.TextField(null=True,verbose_name="Коментар контролера")
    history = HistoricalRecords()



    class Meta:
        verbose_name = 'Завдання'
        verbose_name_plural = 'Завдання'
        ordering = ['date_add']
        permissions = [
            (CustomTaskPermissions.SET_CONTROLLER, "Встановлювати контролера"),

        ]

    def __str__(self):
        return self.title


def get_result_file_path(instance, filename):
    return os.path.join(
        f'uploads/tasks/org_{instance.organization.id}__author_{instance.author}/task_{instance.task.id}/task_executor_{instance.id}/{filename}')

def get_sign_file_path(instance, filename):
    return os.path.join(
        f'uploads/tasks/org_{instance.organization.id}__author_{instance.author}/task_{instance.task.id}/task_executor_{instance.id}/sign/{filename}')

class TaskExecutor(CoreBase):
    task = models.ForeignKey(Task, related_name='task_executors', on_delete=models.CASCADE, null=True)
    executor = models.ForeignKey(CoreUser, related_name='task_executor_users', verbose_name="Виконавець",
                                 on_delete=models.PROTECT, null=True)
    executor_role = models.CharField(verbose_name="Роль", choices=EXECUTOR_ROLE, null=True, max_length=50)
    detail = models.TextField(verbose_name="Уточення завдання", max_length=500, null=True, )
    result = models.TextField(verbose_name="Деталі виконаного підзавдання", max_length=500, null=True, )
    result_file = models.FileField(upload_to=get_result_file_path, null=True, verbose_name='Результат (файл)')
    result_document = models.ForeignKey(BaseDocument, on_delete=models.PROTECT, related_name='task_executors',
                                        null=True,
                                        help_text="Результатом виконання завдання іноді може бути документ, але не завжти."
                                                  + " Зазвичай достатньо описати результат")
    end_date = models.DateField(verbose_name="Уточнення кінцевого терміну", null=True, default=None, blank=True)
    status = models.CharField(verbose_name="Статус завдання", choices=TASK_EXECUTOR_STATUS, max_length=20,
                              default=PENDING)
    sign = models.TextField(null=True, verbose_name='Цифровий підпис')
    sign_file = models.FileField(upload_to=get_sign_file_path,null=True, verbose_name='Цифровий підпис(файл)')
    approve_method = models.CharField(max_length=20, verbose_name="Метод підтвердження", choices=APPROVE_METHODS,
                                      null=True)
    sign_info = JSONField(null=True, verbose_name='Детальна інформація про накладений цифровий підпис')
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Виконання завдання'
        unique_together = (('task', 'executor'), ('task', 'executor_role'))

    def __str__(self):
        return str(self.executor)

    def save(self, *args, **kwargs):
        self.author = self.task.author
        super(CoreBase, self).save(*args, **kwargs)
