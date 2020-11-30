from django.db.models import signals
from apps.document.models.task_model import Task, Flow, TaskExecutor
from apps.document.services.task_service import SetTaskParams, SetChildStatus, HandleExecuteTask, HandleExecuteFlow, \
    HandleRunFlow, SetInitialTaskExecutorParams,SetTaskController\
    #,RunNextTask


def set_parent_task(sender, instance, **kwargs):
    flow = SetTaskParams(task=instance)
    flow.run()


def set_child_status(sender, instance, **kwargs):
    flow = SetChildStatus(task=instance)
    flow.run()


def set_task_executor_organization(sender, instance, **kwargs):
    flow = SetInitialTaskExecutorParams(task_executor=instance)
    flow.run()


def handle_execute_task(sender, instance, created, **kwargs):
    if not created:
        flow = HandleExecuteTask(task=instance)
        flow.run()

# def run_next_task(sender, instance,created, **kwargs):
#     if not created:
#         flow = RunNextTask(task_executor=instance)
#         flow.run()


def handle_execute_flow(sender, instance, **kwargs):
    flow = HandleExecuteFlow(flow=instance)
    flow.run()


def handle_run_flow(sender, instance, created, **kwargs):
    flow = HandleRunFlow(flow=instance)
    flow.run()

def set_task_controller(sender, instance,  **kwargs):
    flow = SetTaskController(task=instance)
    flow.run()

def init_task_signals():
    signals.pre_save.connect(receiver=set_parent_task, sender=Task)
    signals.pre_save.connect(receiver=set_task_controller, sender=Task)
    signals.pre_save.connect(receiver=set_task_executor_organization, sender=TaskExecutor)
    signals.post_save.connect(receiver=set_child_status, sender=Task)
    signals.post_save.connect(receiver=handle_execute_task, sender=Task)
    #signals.post_save.connect(receiver=run_next_task, sender=TaskExecutor)
    signals.post_save.connect(receiver=handle_execute_flow, sender=Flow)
    signals.post_save.connect(receiver=handle_run_flow, sender=Flow)
