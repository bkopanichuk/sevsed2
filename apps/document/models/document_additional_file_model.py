import os
from django.db import models
from preview_generator.manager import PreviewManager
from apps.document.models.document_model import BaseDocument
from apps.l_core.models import CoreBase

from django.conf import settings

MEDIA_ROOT = settings.MEDIA_ROOT


def related_uid_directory_path(instance, filename):
    return 'uploads/document/organization_{0}_{1}/files/{2}'.format(instance.document.organization.id,
                                                                    instance.document.reg_number, filename)


class DocumentFile(CoreBase):
    document = models.ForeignKey(BaseDocument, verbose_name="До документа", on_delete=models.CASCADE, null=True,
                                 blank=True)
    upload = models.FileField(upload_to=related_uid_directory_path, max_length=500, editable=True)
    preview = models.FileField(editable=False, max_length=500, null=True)

    class Meta:
        verbose_name = 'Повязаний файл'
        verbose_name_plural = "Повязані файли"

    def create_preview(self):
        full_path = self.upload.path
        cache_path = os.path.dirname(full_path)
        manager = PreviewManager(cache_path, create_folder=True)
        path_to_preview_image = manager.get_jpeg_preview(full_path, width=200, height=200)

        self.preview.name = path_to_preview_image.replace(MEDIA_ROOT,'')
        #raise Exception(self.preview.name,path_to_preview_image)
        self.save()

    @property
    def related_objects(self):
        return []

    @property
    def file_size(self):
        return f'{int(self.upload.size/1024)} КБ'

    @property
    def file_name(self):
        return os.path.basename(self.upload.name)

    def save(self, *args,  **kwargs):
        super(DocumentFile, self).save()
        if not self.preview:
            self.create_preview()

    def __str__(self):
        return f'Файл "{os.path.basename(self.upload.name)}"'
