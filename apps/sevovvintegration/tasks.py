from __future__ import absolute_import, unicode_literals

import logging

import declxml as xml
from celery import shared_task
from django.conf import settings

import apps.sevovvintegration.models as sev_models

from apps.l_core.models import CoreOrganization
from apps.sevovvintegration.serializers.document_1207_serializer import DocumentXML1207Serializer

logger = logging.getLogger(__name__)
MEDIA_ROOT = settings.MEDIA_ROOT


@shared_task
def download_sevovv_documents():
    from  apps.sevovvintegration.services.download_service import DownloadMessages
    logger.debug('START DOWNLOAD DOCUMENTS FROM SEV')
    ds = DownloadMessages()
    res = ds.run()
    return res


def process_xml(path):
    from apps.sevovvintegration.services.download_service import ProcessXml
    service = ProcessXml(path)
    service.run()
