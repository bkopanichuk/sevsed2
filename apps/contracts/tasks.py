from __future__ import absolute_import, unicode_literals

from celery import shared_task
import time
import logging
logger = logging.getLogger(__name__)

@shared_task
def simulate_work():
    time.sleep(5)
    return 'task complete'


@shared_task
def calculate_accruals():
    from apps.contracts.models.contract_model import Contract
    Contract.calculate_accruals()


@shared_task
def generate_acts():
    from apps.contracts.models.register_act_model import RegisterAct
    RegisterAct.generate_acts()


@shared_task
def async_create_accrual_doc(id):
    from apps.contracts.models.register_accrual_model import RegisterAccrual
    obj = RegisterAccrual.objects.get(pk=id)
    obj.set_docx(save=True)
    return 'Success'


@shared_task
def async_create_act_doc(id):
    from apps.contracts.models.register_act_model import RegisterAct
    obj = RegisterAct.objects.get(pk=id)
    obj.generate_act_docs()
    return 'Success'
