
from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models

from apps.l_core.models import CoreBase
MEDIA_ROOT = settings.MEDIA_ROOT
MEDIA_URL = settings.MEDIA_URL

import logging

logger = logging.getLogger(__name__)

class ImportPayment(CoreBase):
    in_file = models.FileField(upload_to='contracts/import_client_bunk/')
    details = JSONField(editable=False, null=True)
    is_imported = models.BooleanField(default=False, editable=False)

    def __str__(self):
        return str(self.in_file)

