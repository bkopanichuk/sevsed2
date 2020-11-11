from __future__ import unicode_literals

from rest_framework import serializers
from apps.document.models.sign_model import Sign


class SignSerializer(serializers.ModelSerializer):

    class Meta:
        model = Sign
        fields = '__all__'