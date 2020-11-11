from __future__ import unicode_literals

from rest_framework import serializers
from apps.document.models.document_additional_file_model import DocumentFile


class DocumentFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentFile
        fields = ('document', 'upload', 'preview', 'id','file_name','file_size','date_add','__str__')
        read_only_fields = ['preview', 'id']
