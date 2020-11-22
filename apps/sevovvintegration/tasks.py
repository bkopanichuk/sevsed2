from __future__ import absolute_import, unicode_literals

import logging

import declxml as xml
from celery import shared_task
from django.conf import settings

import apps.sevovvintegration.models as sev_models
import apps.sevovvintegration.services.download_service as download_service
from apps.l_core.models import CoreOrganization
from apps.sevovvintegration.serializers import DocumentXML1207Serializer

logger = logging.getLogger(__name__)
MEDIA_ROOT = settings.MEDIA_ROOT


@shared_task
def download_sevovv_documents():
    logger.debug('START DOWNLOAD DOCUMENTS FROM SEV')
    ds = download_service.DownloadMessages()
    res = ds.run()
    return res


def process_xml(path):
    data = xml.parse_from_file(DocumentXML1207Serializer, path)
    from_sys_id = data.get('from_sys_id')
    from_org = CoreOrganization.objects.get(system_id=from_sys_id)
    to_sys_id = data.get('to_sys_id')
    to_org = CoreOrganization.objects.get(system_id=to_sys_id)
    xml_relative_path = path.replace(MEDIA_ROOT + '/', '')
    incoming = sev_models.SEVIncoming(from_org=from_org, to_org=to_org)
    incoming.xml_file.name = xml_relative_path
    incoming.save()
    service = download_service.ProcessIncoming(incoming_message=incoming)
    service.run()
