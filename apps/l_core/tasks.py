from __future__ import absolute_import, unicode_literals

from celery import shared_task
import time




@shared_task
def simulate_work():
    time.sleep(55)
    return  {'result':'task complete'}
