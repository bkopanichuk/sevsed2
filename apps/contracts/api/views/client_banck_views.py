from django.http import JsonResponse
from django_filters import rest_framework as filters
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.contracts.api.serializers.client_bank_serializers import UploadCilentBanklSerializer, \
    ConvertCilentBanklSerializer
from apps.contracts.models.payment_model import ImportPayment
from apps.l_core.api.base.serializers import BaseOrganizationViewSetMixing


class UploadClientBankViewSet(BaseOrganizationViewSetMixing):
    """Дані проплат за договорами"""
    queryset = ImportPayment.objects.all()
    serializer_class = UploadCilentBanklSerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter, OrderingFilter)


@api_view(['POST'])
def upload_client_bank(request):
    """Завантажити дані проплат за договорами з клієнт-банку"""
    serializer = UploadCilentBanklSerializer(data=request.data)
    if serializer.is_valid():
        res = serializer.save()
        return JsonResponse(res.details, safe=False)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConvertClientBankView(APIView):
    """Конвертувати дані Клієнт-банку з CSV в XML - який здатен прочитати 1C"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ConvertCilentBanklSerializer(data=request.data)
        if serializer.is_valid():
            url = serializer.convert_data_from_csv()
            return JsonResponse({'url': url})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)