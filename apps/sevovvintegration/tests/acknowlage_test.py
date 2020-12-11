from pprint import pprint
from pathlib import Path
import declxml as xml
import logging
import tempfile
from lxml import etree
from django.conf import settings
from django.test import SimpleTestCase
import os
from ..serializers.acknowledgement_1207_serialiser import AcknowledgementXML1207Serializer

MEDIA_ROOT = settings.MEDIA_ROOT
xml_schema_path = Path('apps/sevovvintegration/wsdl/Order1207_1 5_v.2.2.xsd').absolute().__str__()

logger = logging.getLogger(__name__)
#xml_test_path = '/home/geo/Documents/DIR/sed_server/sevsed2/apps/sevovvintegration/test_data/test_res.xml'
#xml_valid_path = '/home/geo/Documents/DIR/sed_server/sevsed2/apps/sevovvintegration/test_data/t3.xml'
print(xml_schema_path)
XML_SCHEMA = etree.XMLSchema(file=xml_schema_path)

class TestCase(SimpleTestCase):
    def test_1(self):
        print('test_deserialize'.upper()+'-'*50)
        ack_path = Path('apps/sevovvintegration/test_data/ДС13. Сповіщення про доставку.xml').absolute().__str__()
        data = xml.parse_from_file(AcknowledgementXML1207Serializer,ack_path)
        self.data = data
        pprint(data)
        # xml.serialize_to_file(AcknowledgementXML1207Serializer, data, xml_test_path)
        # xml_doc = etree.parse(
        #     r'C:\Users\o.lec\PycharmProjects\sevsed2\media\sevovv_integration\organization_1\outgoing\2020\11\13\34D39B22-BB84-4E7F-B425-87A138A55CE2.xml')
        # result = XML_SCHEMA.assertValid(xml_doc)
    def test_2(self):
        self.test_1()
        print('test_serialize'.upper()+'-'*50)
        with tempfile.NamedTemporaryFile(suffix='.xml') as tf:
            temp_path_name = tf.name
            xml.serialize_to_file(AcknowledgementXML1207Serializer, self.data, temp_path_name)
            xml_doc = etree.parse(temp_path_name)
            result = XML_SCHEMA.assertValid(xml_doc)
            print('has_errors'.upper()+'-'*50+'?',result)

