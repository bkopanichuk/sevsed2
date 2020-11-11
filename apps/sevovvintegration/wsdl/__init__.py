from zeep import Client
import logging.config

#
logger = logging.getLogger(__name__)

CLIENT = Client('../wsdl/DIR.wsdl')
IDENTITY = CLIENT.get_type('ns2:Identity')
MESSAGE_INFO = CLIENT.get_type('ns2:MessageInfo')
SESSION_INFO_RESULT = CLIENT.get_type('ns2:GetSessionInfoResult')
