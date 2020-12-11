from apps.l_core.models import CoreOrganization
from .abstract import xml1207HeaderMixin
from ..constants import AcknowledgementAckType, ErrorCodes, HeaderMsgType
from .xml1207_factory import Xml1207Factory
from ..serializers.acknowledgement_1207_serialiser import AcknowledgementXML1207Serializer
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)


class Acknowlage2Xml1207Converter(xml1207HeaderMixin):
    def __init__(self, document_message_id: str, message_id: str, consumer: CoreOrganization,
                 producer: CoreOrganization,
                 act_type: int, error_code: int):
        logger.info(
            f'PARAMS: document_message_id:{document_message_id}, message_id:{message_id},'
            f'error_code:{consumer},producer:{producer},act_type:{act_type},error_code:{error_code}')
        super(Acknowlage2Xml1207Converter, self).__init__(message_id, consumer, producer, HeaderMsgType.MESSAGE)
        self.document_message_id = document_message_id
        self.error_code = error_code or ErrorCodes.SUCCESS
        self.act_type = act_type
        self.validate_init_data()

    def validate_init_data(self):
        self.validate_error_code()
        self.validate_ack_type()

    def validate_ack_type(self):
        if self.act_type not in AcknowledgementAckType.valid_choices():
            raise Exception(
                f'"ack_type" = {self.error_code} not in valid choices.Valid choices :{AcknowledgementAckType.valid_choices()}')

    def validate_error_code(self):
        if self.error_code not in ErrorCodes.valid_choices():
            raise Exception(
                f'"error_code" = {self.error_code} not in valid choices.Valid choices :{ErrorCodes.valid_choices()}')

    def get_xml_data(self):
        data = self.get_header_attrs()
        data['Acknowledgement'] = self.get_acknowledgement()
        return data

    def get_acknowledgement(self):
        ack_result = self.get_ack_result()
        acknowledgement = {
            'msg_id': self.document_message_id,
            'ack_type': self.act_type,
            'AckResult': ack_result
        }
        return acknowledgement

    def get_ack_result(self):
        dict_choices = ErrorCodes.dict_choices()
        ack_result = {
            'errorcode': self.error_code,
            'errortext': dict_choices.get(self.error_code)}
        return ack_result


class Acknowlage2Xml1207Factory:
    def __init__(self, document_message_id: str, message_id: str, consumer: CoreOrganization,
                 producer: CoreOrganization,
                 act_type: int, error_code: int):
        logger.info(
            f'PARAMS: document_message_id:{document_message_id}, message_id:{message_id},'
            f'error_code:{consumer},producer:{producer},act_type:{act_type},error_code:{error_code}')
        self.producer = producer
        self.data = Acknowlage2Xml1207Converter(document_message_id, message_id, consumer,
                                                producer, act_type, error_code).get_xml_data()
        self.message_id = message_id

    def create_xml_and_get_path(self):
        xf = Xml1207Factory(self.message_id, AcknowledgementXML1207Serializer, self.data, self.producer)
        return xf.save_xml()
