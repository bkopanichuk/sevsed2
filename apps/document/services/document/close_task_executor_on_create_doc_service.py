from django.utils.timezone import localdate

from apps.document.models.document_model import BaseDocument
from apps.document.models.task_model import TaskExecutor, SUCCESS, MAIN


class CloseTaskExecutorOnCreateDoc:
    def __init__(self, task_executor, document):
        self.task_executor: TaskExecutor = task_executor
        self.document: BaseDocument = document

    def run(self):
        self.close_task_executor()
        self.finish_task()

    def close_task_executor(self):
        self.task_executor.status = SUCCESS
        self.task_executor.result_document = self.document
        self.task_executor.save()

    def finish_task(self):
        if self.task_executor.executor_role == MAIN:
            self.task_executor.task.task_status = SUCCESS
            self.task_executor.task.execute_date = localdate()
            if not self.task_executor.task.controller:
                self.task_executor.task.is_completed = True
            self.task_executor.task.save()