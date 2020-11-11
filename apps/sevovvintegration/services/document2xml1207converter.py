import base64
import os
from pathlib import Path

import declxml as xml
from django.conf import settings
from django.utils.timezone import now

from apps.document.models.document_model import BaseDocument
from apps.l_core.models import CoreOrganization
from ..models import get_outgoing_xml_file_path
from ..serializers import DocumentXML1207Serializer

MEDIA_ROOT = settings.MEDIA_ROOT


class Document2Xml1207Converter():
    def __init__(self, document: BaseDocument, message_id: str, consumer: CoreOrganization,sign:str):
        self.message_id = message_id
        self.document: BaseDocument = document
        self.consumer: CoreOrganization = consumer
        self.sign = sign

    def create_xml(self):
        data = self.get_xml_data()
        return xml.serialize_to_string(DocumentXML1207Serializer, data, indent='  ')

    def save_xml(self):
        data = self.get_xml_data()
        save_path,outgoing_path = self.get_path()
        xml.serialize_to_file(DocumentXML1207Serializer, data, save_path, indent='  ')
        return save_path,outgoing_path

    def get_path(self):
        file_name = f'{self.message_id}.xml'
        outgoing_path = get_outgoing_xml_file_path(self, file_name)
        full_path = str(Path.joinpath(Path(MEDIA_ROOT), Path(outgoing_path)).absolute())
        outgoing_dir = os.path.dirname(full_path)

        ##create path is not exist
        Path(outgoing_dir).mkdir(parents=True, exist_ok=True)
        return full_path,outgoing_path

    def get_xml_data(self):
        data = self.get_header_attrs()
        data['Document'] = self.get_document()
        data['Expansion'] = self.get_expansion()
        return data

    def get_document(self):
        """Document"""
        data = {'Addressee': self.get_consumer_org(),
                'Author': self.get_author(),
                'Confident': {'flag': '0'},
                'DocTransfer': self.get_doc_transfer(),
                'RegNumber': self.get_reg_number(),
                'Writer': self.get_producer_org(),
                'annotation': self.document.comment or '',
                'collection': '0',
                'idnumber': self.message_id,
                'kind': 'Лист',
                'purpose_type': '0',
                'type': '0',
                'urgent': '0'}
        return data

    def get_header_attrs(self):
        producer_org: CoreOrganization = self.document.author.organization
        consumer_org: CoreOrganization = self.consumer
        return {'charset': 'UTF-8',
                'from_org_id': producer_org.edrpou,
                'from_organization': producer_org.full_name,
                'from_sys_id': producer_org.system_id,
                'from_system': producer_org.name,
                'msg_acknow': '2',
                'msg_id': self.message_id,
                'msg_type': '1',
                'standart': '1207',  ##https://zakon.rada.gov.ua/laws/show/z1306-11#Text
                'time': now().isoformat(),
                'to_org_id': consumer_org.edrpou,
                'to_organization': consumer_org.full_name,
                'to_sys_id': consumer_org.system_id,
                'to_system': consumer_org.name,
                'version': '1.5'}  ##default version from current XSD

    def get_expansion(self):
        expansion = {
            'StaticExpansion':
                {'SignInfo':
                    {'SignData': {
                        '.': self.sign},
                        ##TODO Правильно підбирати дату підпису
                        'SigningTime': {'.': now().isoformat()  ##self.document.sign_time
                                        },
                        'docTransfer_idnumber': self.document.pk}
                },
            'exp_ver': '1.0',
            'organization': 'BMS Consulting'}
        return expansion

    def get_producer_org(self):
        author = self.document.author
        return {'Organization': {'Address': {'country': 'Україна'},
                                 'fullname': author.organization.full_name,
                                 'inn': '0',
                                 'ogrn': author.organization.edrpou,
                                 'shortname': author.organization.name},
                'type': '0',
                }

    def get_consumer_org(self):
        organization = self.consumer
        return {'Organization': {'Address': {'country': 'Україна'},
                                 'fullname': organization.full_name,
                                 'inn': '0',
                                 'ogrn': organization.edrpou,
                                 'shortname': organization.name},
                'type': '0',
                }

    def get_author(self):
        author = self.get_producer_org()
        author.update({'OutNumber': {'RegNumber': self.get_reg_number()}})
        return author

    def get_reg_number(self):
        ##TODO прибрати "або" та піля ного в реальному прикладі
        return {'.': self.document.reg_number or '', 'regdate': self.document.reg_date or now().utcnow()}

    def get_doc_transfer(self):
        """DocTransfer"""
        file_path = self.document.main_file.path
        file_name = os.path.basename(file_path)
        print('file_name:', file_name)
        file_extension = file_name.split('.')[1]
        print('file_extension:', file_extension)
        with open(file_path, 'rb') as file:
            print('reading file ...:', file_path)
            b_data = file.read()
            print('getting file encoding...:', file_path)
            encoding = 'UTF-8'  ##chardet.detect(b_data).get('encoding', 'UTF-8')
            print('encoding:', encoding)
            doc_b64 = base64.b64encode(b_data).decode()
        doc_data = {
            '.': doc_b64,
            'char_set': encoding,
            'description': file_name,
            'idnumber': self.document.pk,
            'type': file_extension}
        return doc_data
