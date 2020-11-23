from __future__ import unicode_literals

from rest_framework import serializers
from apps.document.models.documenttype_model import IncomingDocumentType,OutgoingDocumentType,InnerDocumentType


class IncomingDocumentTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = IncomingDocumentType
        fields = ['id','__str__','name','execute_interval','execute_interval_reason']


class OutgoingDocumentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = OutgoingDocumentType
        fields = ['id','__str__','name']

class InnerDocumentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = InnerDocumentType
        fields = ['id','__str__','name']
