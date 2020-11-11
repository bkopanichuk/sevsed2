from __future__ import unicode_literals

from rest_framework import serializers
from apps.document.models.coverletter_model import CoverLetter


class CoverLetterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoverLetter
        fields = '__all__'
