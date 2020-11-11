from django_filters import rest_framework as filters
from rest_framework import viewsets
from apps.l_core.api.base.serializers import BaseOrganizationViewSetMixing
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.document.api.srializers.register_serializers import RegistrationJournalSerializer,\
    RegistrationJournalVolumeSerializer,RegistrationMaskSerializer
from apps.document.models.register_model import RegistrationJournal,RegistrationJournalVolume,RegistrationMask


class RegistrationMaskViewSet(BaseOrganizationViewSetMixing):
    queryset = RegistrationMask.objects.all()
    serializer_class = RegistrationMaskSerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter, OrderingFilter)



class RegistrationJournalViewSet(BaseOrganizationViewSetMixing):
    queryset = RegistrationJournal.objects.all()
    serializer_class = RegistrationJournalSerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter, OrderingFilter)

    def get_queryset(self):
        return super(RegistrationJournalViewSet, self).get_queryset()




class RegistrationJournalVolumeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = RegistrationJournalVolume.objects.all()
    serializer_class = RegistrationJournalVolumeSerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter, OrderingFilter)
