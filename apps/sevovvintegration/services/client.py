import logging.config
import os
from datetime import datetime
from pathlib import Path
from typing import Text

from django.conf import settings
from django.utils.timezone import now
from filehash import FileHash
from zeep import Client
from ..exceptions import SessionInfoException

MEDIA_ROOT = settings.MEDIA_ROOT

#
logger = logging.getLogger(__name__)

CLIENT = Client('apps/sevovvintegration/wsdl/DIR.wsdl')
IDENTITY = CLIENT.get_type('ns2:Identity')
MESSAGE_INFO = CLIENT.get_type('ns2:MessageInfo')
SESSION_INFO_RESULT = CLIENT.get_type('ns2:SessionInfo')
ARRAY_OF_MESSAGE_INFO = CLIENT.get_type('ns2:ArrayOfMessageInfo')
DOWNLOAD_CHUNK_RESPONSE = CLIENT.get_type('ns2:DownloadChunkResponse')
MESSAGE_VALIDATION_INFO = CLIENT.get_type('ns2:MessageValidationInfo')

SHA256HASHER = FileHash('sha256')

SED = 'Sed'
PLAIN = 'Plain'
DOCUMENT = 'Document'

INPUT_MESSAGE_COUNT = 1000
MAX_CHUNK_SIZE = 2500000






def get_incoming_xml_path(consumer):
    _now = now()

    path = os.path.join(MEDIA_ROOT,
                        f'sevovv_integration/org_{consumer.id}/incoming/{_now.year}/{_now.month}/{_now.day}')
    if not os.path.exists(path):
        os.makedirs(path)
    return path


class CompanyInfo():
    def __init__(self, id, edrpou, system_id, password=None):
        self.id = id
        self.edrpou = edrpou
        self.system_id = system_id
        self.password = password

    @property
    def identity(self):
        if not self.password:
            raise Exception(f'password not exist "{self.password}"', )
        __identity = IDENTITY(SystemId=self.system_id, Password=self.password)
        return __identity

    @property
    def OrgId(self):
        return self.edrpou


class Message():
    def __call__(self, producer: CompanyInfo, consumer: CompanyInfo, document_xml_path: Path,
                 message_id: str) -> MESSAGE_INFO:
        return self.get_message_info(producer, consumer, document_xml_path, message_id)

    def get_document_xml_size(self, document_xml_path: Path) -> int:
        return os.path.getsize(document_xml_path)

    def get_message_info(self, producer: CompanyInfo, consumer: CompanyInfo, document_xml_path: Path,
                         message_id: str) -> MESSAGE_INFO:
        date = datetime.today()
        message_info = MESSAGE_INFO(CreationDate=date,
                            Creator=SED,
                            Format=PLAIN,
                            FromOrgId=producer.OrgId,
                            FromSysId=producer.system_id,
                            MessageId=message_id,
                            SessionId=0,
                            Size=self.get_document_xml_size(document_xml_path),
                            ToOrgId=consumer.OrgId,
                            ToSysId=consumer.system_id,
                            Type=DOCUMENT)
        print('MESSAGE_INFO: ',message_info)
        return message_info


class SEVUploadClient():
    def __init__(self):
        self.client = CLIENT

    def send_document(self, document_path: Path, producer: CompanyInfo, consumer: CompanyInfo, message_id: str):
        document_xml_hash = self.get_document_hash(document_path)
        message = Message()(producer=producer, consumer=consumer,
                            document_xml_path=document_path, message_id=message_id)
        session_id, max_chunk_size = self.open_uploading_session(producer, message, document_xml_hash)

        self.upload_document(producer, session_id, document_path, max_chunk_size)
        result = self.check_session_info(producer, session_id)
        logger.debug(result)
        dict_result = {"Error":result.Error,
                       'MaxPartSize': result.MaxPartSize,
                       'MessageId': result.MaxPartSize,
                       'MessageSize': result.MessageSize,
                       'SessionId': result.SessionId,
                       'Status': result.Status,
                       'TransferredBytesCount': result.TransferredBytesCount,
                       'Type': result.Type
                       }
        return dict_result

    # def generate_message_id(self) -> Text:
    #     return uuid.uuid4().__str__().upper()

    def check_session_info(self, producer: CompanyInfo, session_id: int) -> SESSION_INFO_RESULT:
        print('producer:',producer.identity, 'session_id: ',session_id)
        print('CHECKING SESSION INFO')
        session_info: SESSION_INFO_RESULT = self.client.service.GetSessionInfo(identity=producer.identity,
                                                                               sessionId=session_id)
        print('SESSION INFO:',session_info)
        if session_info.Error:
            raise SessionInfoException(session_info.Error)

        if not session_info.MessageSize == session_info.TransferredBytesCount:
            raise SessionInfoException('MessageSize and TransferredBytesCount is no equal')

        return session_info

    def get_document_hash(self, document_xml_path: Path) -> Text:
        return SHA256HASHER.hash_file(document_xml_path).upper()

    def open_uploading_session(self, producer: CompanyInfo, message: MESSAGE_INFO, document_xml_hash: str) -> (
    int, int):
        print('OPENING UPLOADING SESSION')
        print('producer identity: ',producer.identity)
        pack = self.client.service.OpenUploadingSession(identity=producer.identity, messageInfo=message,
                                                        hash=document_xml_hash)
        print('SESSION INFO:',pack)
        return pack.SessionId, pack.MaxPartSize

    def upload_chunk(self, producer_identity, session_id, chunk):
        print('UPLOADING CHUNK')
        print('producer identity: ',producer_identity)
        print('session_id: ',session_id)
        response = self.client.service.UploadMessageChunk(identity=producer_identity, sessionId=session_id, messageChunk=chunk)
        print(response)

    def get_generator(self, document_xml_path: Path, max_chunk_size: int) -> bytes:
        print('GET GENERATOR:', document_xml_path)
        print('max_chunk_size:', max_chunk_size)

        with open(document_xml_path, 'rb') as entry:
            for chunk in iter(lambda: entry.read(max_chunk_size), b''):
                print('CHUNK SIZE',len(chunk))
                yield chunk

    def upload_document(self, producer, session_id, document_xml_path, max_chunk_size):
        print('UPLOADING DOCUMENT')
        document_xml_streaming = self.get_generator(document_xml_path, max_chunk_size)

        for chunk in document_xml_streaming:
            self.upload_chunk(producer.identity, session_id, chunk)


class SEVDownloadClient():
    def __init__(self):
        self.client = CLIENT

    def download_messages(self, consumer: CompanyInfo):
        logger.debug('START downloading messages')
        path = get_incoming_xml_path(consumer)
        messages = self.get_input_messages(consumer.identity)
        if messages:
            return self.process_messages(consumer.identity, messages, path)
        else:
            return []

    def process_messages(self, consumer, messages: ARRAY_OF_MESSAGE_INFO, path):
        documents = []
        for message in messages:
            session_id = self.open_downloading_session(consumer, message.MessageId)
            document = self.download_document(message.Size, session_id, consumer, message.MessageId, path)
            documents.append(document)
        return documents

    def check_document_hash(self, consumer, session_id, xml_path):
        message_validation_info = self.client.service.GetMessageValidationInfo(consumer, session_id)
        file_hash = SHA256HASHER.hash_file(xml_path).upper()
        if not file_hash == message_validation_info.Hash:
            raise Exception('xml is not valid, Hash is not equal')
        return message_validation_info.Session

    def download_document(self, message_size, session_id, consumer, message_id, path):
        logger.debug('DOWNLOADING DOCUMENT:', message_id)
        downloaded_bites = 0
        if message_size < MAX_CHUNK_SIZE:
            chunk_size = message_size

        else:
            chunk_size = MAX_CHUNK_SIZE

        file_name = message_id + '.xml'
        file_full_path = os.path.join(path, file_name)

        with open(file_full_path, 'wb') as file:
            while downloaded_bites < message_size:
                if message_size - downloaded_bites < chunk_size:
                    chunk_size = message_size - downloaded_bites
                data = self.download_chunk(consumer, session_id, downloaded_bites, chunk_size)
                file.write(data)
                downloaded_bites += chunk_size

        session_info = self.check_document_hash(consumer, session_id, file_full_path)
        self.end_document_downloading(consumer, session_info, message_size)
        return file_full_path

    def end_document_downloading(self, consumer, session_info, downloaded_bites):
        session_info.TransferredBytesCount = downloaded_bites
        session_info.MaxPartSize = MAX_CHUNK_SIZE
        session_info.Status = 'Delivered'  # Щоб закрити сесію, і виключити повторне скачування документа
        s_info = self.client.service.EndProcessingDownloadedMessage(consumer, session_info)
        logger.info(s_info)

    def download_chunk(self, consumer, session_id, from_position, count):
        logger.info('DOWNLOADING CHUNK')
        res = self.client.service.DownloadMessageChunk(consumer, session_id, from_position, count)
        return res.MessageChunk

    def get_input_messages(self, consumer) -> ARRAY_OF_MESSAGE_INFO:
        logger.debug('GETTING input messages')
        result: ARRAY_OF_MESSAGE_INFO = self.client.service.GetInputMessages(identity=consumer,
                                                                             сount=INPUT_MESSAGE_COUNT)
        logger.debug('MESSAGES', result)
        return result

    def open_downloading_session(self, consumer, message_id: str):
        logger.debug('OPENING DOWNLOADING SESSION')
        session_info: SESSION_INFO_RESULT = self.client.service.OpenDownloadingSession(identity=consumer,
                                                                                       messageId=message_id)
        logger.debug('SESSION ID:', session_info.SessionId)
        return session_info.SessionId
