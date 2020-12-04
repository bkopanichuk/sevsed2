from rest_framework import serializers
from apps.dict_register.models import TemplateDocument
from apps.l_core.api.base.serializers import DynamicFieldsModelSerializer


class TemplateDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemplateDocument
        fields = ['name', 'code', 'id','__str__', 'template_file', 'related_model_name']