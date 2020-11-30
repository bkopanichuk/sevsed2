import csv
import os
from datetime import datetime

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.utils.crypto import get_random_string
from rest_framework import serializers

from apps.contracts.api.serializers.contract_serializers import MEDIA_ROOT, MEDIA_URL
from apps.contracts.models.payment_model import ImportPayment
from apps.contracts.settings import IBAN
from apps.l_core.api.base.serializers import DynamicFieldsModelSerializer


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