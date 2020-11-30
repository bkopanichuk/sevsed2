from __future__ import unicode_literals

import csv
import os
from datetime import datetime

import dicttoxml
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.utils.crypto import get_random_string
from rest_framework import serializers

from apps.contracts.models.payment_model import ImportPayment
from apps.l_core.api.base.serializers import CoreOrganizationSerializer
from apps.l_core.api.base.serializers import DynamicFieldsModelSerializer
from apps.l_core.models import CoreOrganization
from ...models.contract_model import Contract, RegisterAccrual, ContractFinance, RegisterPayment, RegisterAct, \
    StageProperty, Coordination, ContractSubscription, ContractProducts

MEDIA_ROOT = settings.MEDIA_ROOT
MEDIA_URL = settings.MEDIA_URL

from ...settings import IBAN

import logging

logger = logging.getLogger(__name__)


##Contract-------------------------------------------------------
class ContractFinanceSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = ContractFinance
        fields = ('id', 'total_size_accrual', 'total_size_pay', 'total_balance')


##Contract-------------------------------------------------------
class ContractSerializer(DynamicFieldsModelSerializer):
    contractor_name = serializers.SerializerMethodField()
    contractfinance = ContractFinanceSerializer(read_only=True)
    contractor_data = serializers.PrimaryKeyRelatedField(read_only=True)
    contractor = serializers.PrimaryKeyRelatedField(required=True, queryset=CoreOrganization.objects.all())

    class Meta:
        model = Contract
        fields = (
            'id', '__str__', 'number_contract', 'parent_element', 'start_date',
            'start_of_contract', 'start_accrual',
            'status', 'automatic_number_gen', 'price_additional_services', 'one_time_service',
            'subject_contract', 'copy_contract', 'contractor', 'contractor_name', 'price_contract', 'contract_time',
            'expiration_date', 'price_contract_by_month', 'contractfinance', 'contract_docx', 'unique_uuid',
            'contractor_data', 'change_status_reason')
        expandable_fields = {
            'contractor_data': (
                CoreOrganizationSerializer, {'source': 'contractor', })
        }

    def get_contractor_name(self, obj):
        if obj.contractor:
            return obj.contractor.__str__()


##RegisterAccrual-------------------------------------------------------
class RegisterAccrualSerializer(DynamicFieldsModelSerializer):
    contract = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = RegisterAccrual
        fields = (
            'id', '__str__', 'date_accrual', 'size_accrual', 'balance', 'penalty', 'pay_size', 'contract', 'title',
            'accrual_docx', 'date_sending_doc', 'is_doc_send_successful')
        expandable_fields = {
            'contract': (
                ContractSerializer, {'source': 'contract', 'fields': ['id', '__str__']})
        }


##RegisterPayment-------------------------------------------------------
class RegisterPaymentSerializer(DynamicFieldsModelSerializer):
    contract_data = serializers.PrimaryKeyRelatedField(read_only=True)
    contractor_name = serializers.SerializerMethodField()

    class Meta:
        model = RegisterPayment
        fields = (
            'payment_date', 'id', 'sum_payment', 'payment_type', 'contract', '__str__', 'contract_data',
            'contractor_name',
            'outer_doc_number')
        expandable_fields = {
            'contract_data': (
                ContractSerializer, {'source': 'contract', 'fields': ['id', '__str__']})
        }

    def get_contractor_name(self, obj):
        if obj.contract:
            return obj.contract.contractor.__str__()


##RegisterAct-------------------------------------------------------
class RegisterActSerializer(DynamicFieldsModelSerializer):
    ##accrual_data = LCorePrimaryKeyRelatedField(read_only=True)
    payments = RegisterPaymentSerializer(read_only=True, many=True)
    accrual = serializers.PrimaryKeyRelatedField(read_only=True)
    contract = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = RegisterAct
        fields = (
            'id', 'number_act', '__str__', 'date_formation_act', 'is_send_successful', 'date_sending_act',
            'date_return_act', 'accrual', 'copy_act_from_contractor',
            'payments', 'copy_act', 'copy_act_pdf', 'contract')
        expandable_fields = {
            'accrual': (
                RegisterAccrualSerializer, {'source': 'accrual', 'fields': ['id', 'date_accrual', 'size_accrual']}),
            'contract': (
                ContractSerializer, {'source': 'contract', 'fields': ['id', '__str__', 'contractor']}),

        }


##StageProperty-------------------------------------------------------
class StagePropertySerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = StageProperty
        fields = (
            'id', '__str__', 'contract', 'name', 'address', 'settlement_account', 'mfo', 'edrpou', 'phone', 'bank_name',
            'ipn', 'main_unit', 'main_unit_state', 'certificate_number', 'email', 'statute_copy', 'work_reason')


##ContractSubscription-------------------------------------------------------
class ContractSubscriptionSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = ContractSubscription
        fields = (
            'id', '__str__', 'count', 'price', 'pdv', 'total_price', 'total_price_pdv', 'is_legal', 'product',
            'contract',
            'start_period', 'end_period')


##ContractProducts-------------------------------------------------------
class ContractProductsSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = ContractProducts
        fields = ('id', '__str__', 'count', 'price', 'pdv', 'total_price', 'total_price_pdv', 'product', 'contract')


##Coordination-------------------------------------------------------
class CoordinationSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Coordination
        fields = ('id', '__str__', 'object_id', 'content_type', 'subject', 'status', 'start', 'end')


class calculateAccrualSerializer(serializers.Serializer):
    create_pdf = serializers.BooleanField()
    is_budget = serializers.BooleanField()
    is_comercial = serializers.BooleanField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()


class UploadCilentBanklSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = ImportPayment
        fields = ('id', '__str__', 'in_file', 'details', 'is_imported', 'date_add')


class ConvertCilentBanklSerializer(serializers.Serializer):
    in_file = serializers.FileField()

    def convert_data_from_csv(self):
        DATA_KEYS = {
            'Документ': 'Номер',
            'Дата операції': 'Дата',
            'Кредит': 'Сумма',
            'Рахунок кореспондента': 'ПлательщикСчет',
            'Кореспондент': 'Плательщик',
            'ЄДРПОУ кореспондента': 'ПлательщикОКПО',
            'Назва банка': 'ПлательщикБанк',
            'МФО банка': 'ПлательщикМФО',
            'Рахунок': 'ПолучательСчет',
            'ЄДРПОУ': 'ПолучательОКПО',
            'МФО': 'ПолучательМФО',
            'Призначення платежу': 'НазначениеПлатежа',

        }
        """Import payment data from csv file"""
        result = {}
        upload_to = 'temp/'

        dir_path = f'{MEDIA_ROOT}/{upload_to}'
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        n = get_random_string()
        filename = f'{upload_to}{n}.csv'
        file_path = os.path.join(MEDIA_ROOT, filename)
        in_file = self.validated_data['in_file']
        default_storage.save(file_path, ContentFile(in_file.read()))

        body = {
            'ВерсияФормата': 2,
            'Получатель': 'Бухгалтерия для Украины, редакция 2.0',
            'ДатаНачала': '2015-02-19',
            'ДатаКонца': '2025-02-19',
            'РасчСчет': IBAN,
            'СекцияДокумент': []
        }

        with  open(file_path, mode='r', encoding='cp1251') as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=';')
            for row in csv_reader:
                doc = {}
                for key, value in row.items():
                    doc_key = DATA_KEYS.get(key)
                    if key == 'Дата операції':
                        value = datetime.strptime(value, '%d.%m.%Y %H:%M').strftime('%Y-%m-%d')
                    if not doc_key:
                        continue
                    doc[doc_key] = value
                    doc['ВидДокумента'] = 'Платежное поручение'
                body['РасчСчет'] = row['Рахунок']
                body['СекцияДокумент'].append(doc)
                ##print(key, value)
        returnfield = lambda x: 'СекцияДокумент'
        xml = dicttoxml.dicttoxml(body,
                                  custom_root='_1CClientBankExchange',
                                  attr_type=False,
                                  item_func=returnfield).decode('utf-8')
        xml = xml.replace('<СекцияДокумент><СекцияДокумент>', '<СекцияДокумент>')
        xml = xml.replace('</СекцияДокумент></СекцияДокумент>', '</СекцияДокумент>')
        xml = xml.replace('UTF-8', 'Windows-1251')

        f = get_random_string() + '.xml'
        res_file = os.path.join(dir_path, f)
        with open(res_file, 'w', encoding='cp1251') as  file:
            file.write(xml)

        url = os.path.join(MEDIA_URL, upload_to.replace('/', ''), f)
        return url
