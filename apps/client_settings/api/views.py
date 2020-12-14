from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from ..models import ClientFormSettings
from ..serializer import ClientFormSettingsSerializer


class FormSettingsViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]
    def list(self, request):
        queryset = ClientFormSettings.objects.all()
        serializer = ClientFormSettingsSerializer(queryset, many=True, context=request)
        return Response(serializer.data)
