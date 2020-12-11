import os
from pathlib import Path

import declxml as xml
from django.conf import settings
from lxml import etree
from apps.l_core.models import CoreOrganization
from ..models import get_outgoing_xml_file_path

MEDIA_ROOT = settings.MEDIA_ROOT
xml_schema_path = Path('apps/sevovvintegration/wsdl/Order1207_1 5_v.2.2.xsd').absolute().__str__()
XML_SCHEMA = etree.XMLSchema(file=xml_schema_path)

import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)


class FakeDocument():
    def __init__(self, organization):
        self.organization = organization


class Xml1207Factory():
    def __init__(self, message_id: str, serializer, data, organization: CoreOrganization):
        self.message_id = message_id
        self.serializer = serializer
        self.data = data
        self.document = FakeDocument(organization)

    def create_xml(self):
        return xml.serialize_to_string(self.serializer, self.data, indent='  ')

    def save_xml(self):
        full_path, outgoing_path = self.get_path()
        xml.serialize_to_file(self.serializer, self.data, full_path, indent='  ')
        self.validate_xml(full_path)
        return full_path, outgoing_path

    def validate_xml(self, full_path):
        xml_doc = etree.parse(full_path)
        result = XML_SCHEMA.validate(xml_doc)
        if result:
            logger.error(result)

    def get_path(self):
        file_name = f'{self.message_id}.xml'
        outgoing_path = get_outgoing_xml_file_path(self, file_name)
        full_path = str(Path.joinpath(Path(MEDIA_ROOT), Path(outgoing_path)).absolute())
        outgoing_dir = os.path.dirname(full_path)

        ##create path is not exist
        Path(outgoing_dir).mkdir(parents=True, exist_ok=True)
        return full_path, outgoing_path
