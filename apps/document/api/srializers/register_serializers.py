from rest_framework import serializers
from apps.document.models.register_model import RegistrationJournal,RegistrationJournalVolume,RegistrationMask


class RegistrationMaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = RegistrationMask
        fields = ['id','__str__','name','mask','description']


class RegistrationJournalSerializer(serializers.ModelSerializer):

    class Meta:
        model = RegistrationJournal
        fields = ['id','__str__','name','mask','document_cast','max_count_to_new_volume']


class RegistrationJournalVolumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegistrationJournalVolume
        fields = ['id','__str__','name','registration_journal']