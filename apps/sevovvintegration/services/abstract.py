from django.utils.timezone import now
from apps.l_core.models import CoreOrganization

import logging

logger = logging.getLogger(__name__)

class xml1207HeaderMixin():
    def __init__(self,  message_id: str, consumer: CoreOrganization, producer: CoreOrganization, msg_type:int ):
        self.message_id = message_id
        self.consumer: CoreOrganization = consumer
        self.producer: CoreOrganization = producer
        self.msg_type = msg_type

    def get_header_attrs(self):
        producer_org: CoreOrganization = self.producer
        consumer_org: CoreOrganization = self.consumer
        return {'charset': 'UTF-8',
                'from_org_id': producer_org.edrpou,
                'from_organization': producer_org.full_name,
                'from_sys_id': producer_org.system_id,
                'from_system': producer_org.name,
                'msg_acknow': '2',
                'msg_id': self.message_id,
                'msg_type': self.msg_type,
                'standart': '1207',  ##https://zakon.rada.gov.ua/laws/show/z1306-11#Text
                'time': now().isoformat(),
                'to_org_id': consumer_org.edrpou,
                'to_organization': consumer_org.full_name,
                'to_sys_id': consumer_org.system_id,
                'to_system': consumer_org.name,
                'version': '1.5'}  ##default version from current XSD
