from __future__ import absolute_import, unicode_literals

from celery import shared_task
from apps.sevovvintegration.services import download_service


import logging

logger = logging.getLogger(__name__)

@shared_task
def download_sevovv_documents():
    logger.debug('START DOWNLOAD DOCUMENTS FROM SEV')
    ds = download_service.DownloadMessages()
    res = ds.run()
    return res


