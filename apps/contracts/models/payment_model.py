
from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models

from apps.l_core.models import CoreBase
MEDIA_ROOT = settings.MEDIA_ROOT
MEDIA_URL = settings.MEDIA_URL

import logging

logger = logging.getLogger(__name__)

def import_client_bunk_directory_path(instance, filename):
    return 'uploads/org_{0}/import_client_bunk/{1}/{2}'.format(instance.contract.organization.id,
                                                                      instance.unique_uuid,
                                                                      filename)

class ImportPayment(CoreBase):
    in_file = models.FileField(upload_to=import_client_bunk_directory_path)
    details = JSONField(editable=False, null=True)
    is_imported = models.BooleanField(default=False, editable=False)

    def __str__(self):
        return str(self.in_file)

