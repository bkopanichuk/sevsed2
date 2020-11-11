from __future__ import absolute_import, unicode_literals

from celery import shared_task
import time
from apps.contracts.models import contract_model


@shared_task
def simulate_work():
    time.sleep(5)
    return 'task complete'


@shared_task
def calculate_accruals():
    contract_model.Contract.calculate_accruals()


@shared_task
def generate_acts():
    contract_model.RegisterAct.generate_acts()


@shared_task
def async_create_accrual_doc(id):
    obj = contract_model.RegisterAccrual.objects.get(pk=id)
    obj.set_docx(save=True)

    return 'Success'


@shared_task
def async_create_act_doc(id):
    obj = contract_model.RegisterAct.objects.get(pk=id)
    obj.generate_act_docs()
    return 'Success'
