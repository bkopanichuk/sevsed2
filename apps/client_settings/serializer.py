from rest_framework import serializers

from .models import ClientFormSettings, ClientFormElementSettings


class ClientFormElementSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientFormElementSettings
        fields = ['name', 'values', 'visible', 'enabled']


class ClientFormSettingsSerializer(serializers.ModelSerializer):
    elements = ClientFormElementSettingsSerializer(many=True)

    class Meta:
        model = ClientFormSettings
        fields = ['role', 'form_name', 'elements']
