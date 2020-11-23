from __future__ import unicode_literals

import os

from rest_framework import serializers

from apps.document.models.document_model import BaseDocument
from apps.document.models.document_constants import INCOMING, OUTGOING, INNER, DOCUMENT_CAST
from apps.document.models.document_model import INNER_DOCUMENT_STATUS_CHOICES, OUTGOING_DOCUMENT_STATUS_CHOICES, \
    INCOMING_DOCUMENT_STATUS_CHOICES
from apps.document.models.document_model import ON_REGISTRATION, PROJECT
from apps.document.models.document_model import MAILING_METHODS

from  apps.l_core.models import CoreOrganization



class EmptySerializer(serializers.Serializer):
    pass


class SendDocumentLetterSerializer(serializers.Serializer):
    mailing_method = serializers.ChoiceField(required=True, choices=MAILING_METHODS)



class SendToArchiveSerializer(serializers.ModelSerializer):

    case_index = serializers.CharField(required=True, label="Індекс  та  заголовок справи")
    case_number = serializers.CharField(required=True, label="Номер тому справи")

    class Meta:
        model = BaseDocument
        fields = ['case_index', 'case_number']


class DocumentListSerializer(serializers.ModelSerializer):
    incoming_type_name = serializers.SerializerMethodField()
    correspondent_name = serializers.SerializerMethodField()

    class Meta:
        model = BaseDocument
        fields = ['id', 'outgoing_number', 'outgoing_date', 'document_cast', 'reg_number',
                  'reg_date', 'incoming_type', 'incoming_type_name', 'outgoing_type', 'correspondent','status'

                  'correspondent_name', '__str__', 'author', 'department', 'registration_type','unique_uuid']

    def get_incoming_type_name(self, obj):
        if obj.incoming_type and hasattr(obj.incoming_type, 'name'):
            return obj.incoming_type.name

    def get_correspondent_name(self, obj):
        if obj.correspondent and hasattr(obj.correspondent, 'name'):
            return obj.correspondent.name


class DocumentSerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(
        choices=INCOMING_DOCUMENT_STATUS_CHOICES + OUTGOING_DOCUMENT_STATUS_CHOICES + INNER_DOCUMENT_STATUS_CHOICES)

    class Meta:
        model = BaseDocument
        fields = ['id', 'main_file', 'outgoing_number', 'outgoing_date', 'document_cast', 'reg_number',
                  'reg_date', 'incoming_type', 'outgoing_type', 'approve_type', 'comment', 'correspondent',
                  'signer','reply_date',
                  '__str__', 'author', 'document_linked_to', 'department', 'approvers_list', 'preview',
                  'preview_pdf', 'registration_type','registration', 'execute_task_on_create', 'status','unique_uuid']

        read_only_fields = ['id', 'preview', 'preview_pdf', '__str__', 'author','unique_uuid' ]


class IncomingDocumentSerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(choices=INCOMING_DOCUMENT_STATUS_CHOICES, default=ON_REGISTRATION)
    document_cast = serializers.ChoiceField(choices=DOCUMENT_CAST, default=INCOMING)
    reg_number = serializers.CharField(required=False, allow_null=True, allow_blank=True, label="Реєстраціний номер")
    correspondent_name = serializers.SerializerMethodField()
    incoming_type_name = serializers.SerializerMethodField()

    def get_correspondent_name(self, obj):
        if obj.correspondent and hasattr(obj.correspondent, 'name'):
            return obj.correspondent.name

    def get_incoming_type_name(self, obj):
        if obj.incoming_type and hasattr(obj.incoming_type, 'name'):
            return obj.incoming_type.name

    class Meta:
        model = BaseDocument
        fields = ['id', 'main_file', 'document_cast', 'outgoing_number', 'outgoing_date', 'reg_number',
                  'reg_date', 'incoming_type', 'approve_type', 'comment', 'correspondent', 'correspondent_name',
                  'signer',
                  '__str__', 'author', 'document_linked_to', 'approvers_list', 'preview', 'incoming_type_name',
                  'reply_date',
                  'preview_pdf', 'registration','registration_type', 'execute_task_on_create', 'status','unique_uuid']
        read_only_fields = ['id', 'preview', 'preview_pdf', '__str__', 'author', 'correspondent_name','unique_uuid']


class OutgoingDocumentSerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(choices=OUTGOING_DOCUMENT_STATUS_CHOICES, default=PROJECT)
    document_cast = serializers.ChoiceField(choices=DOCUMENT_CAST, default=OUTGOING)
    reg_number = serializers.CharField(required=False, allow_null=True, allow_blank=True, label="Реєстраціний номер")
    mailing_list = serializers.PrimaryKeyRelatedField(many=True,queryset=CoreOrganization.objects.all(),required=False)

    class Meta:
        model = BaseDocument
        fields = ['id', 'main_file', 'reg_number', 'document_cast',
                  'reg_date', 'outgoing_type', 'approve_type', 'comment', 'correspondent', 'signer','main_signer',
                  '__str__', 'author', 'document_linked_to', 'approvers_list', 'preview','mailing_list','mailing_method',
                  'preview_pdf', 'registration_type','registration', 'execute_task_on_create', 'status','unique_uuid']
        read_only_fields = ['id', 'preview', 'preview_pdf', '__str__', 'author', 'unique_uuid']



class InnerDocumentSerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(choices=INNER_DOCUMENT_STATUS_CHOICES, default=PROJECT)
    document_cast = serializers.ChoiceField(choices=DOCUMENT_CAST, default=INNER)
    reg_number = serializers.CharField(required=False, allow_null=True, allow_blank=True, label="Реєстраціний номер")

    class Meta:
        model = BaseDocument
        fields = ['id', 'main_file', 'reg_number', 'document_cast',
                  'reg_date',  'approve_type', 'comment', 'correspondent', 'main_signer',
                  'inner_type','approve_type',
                  '__str__', 'author', 'document_linked_to', 'approvers_list', 'preview',
                  'preview_pdf', 'registration_type','registration', 'execute_task_on_create', 'status','unique_uuid']
        read_only_fields = ['id', 'preview', 'preview_pdf', '__str__', 'author', 'unique_uuid']



class RelatedDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaseDocument
        fields = ['id', '__str__']


class UploadDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaseDocument
        fields = ['id', 'main_file', '__str__']


class DocumentHistorySerializer(serializers.ModelSerializer):
    history = serializers.SerializerMethodField(method_name='get_history', read_only=True)

    class Meta:
        model = BaseDocument
        fields = ['history', ]

    def get_main_file_name(self, main_file):
        return os.path.basename(main_file)

    def get_history(self, obj: BaseDocument):
        history_q = obj.mainfileversion_set.all().order_by('-add_date').values('main_file', 'add_date')
        data = [obj.update({'main_file': self.get_main_file_name(obj.get('main_file'))}) for obj in history_q]
        return history_q
