class Mixin:
    @classmethod
    def valid_choices(cls):
        return [choice[0] for choice in cls.CHOICES ]

    @classmethod
    def dict_choices(cls):
        return {choice[0]:choice[1] for choice in cls.CHOICES }


class ErrorCodes(Mixin):
    """Коди помилок"""
    SUCCESS = 0
    CHOICES = [
        [SUCCESS, "Повідомлення доставлено без помилок"],
    ]

class AcknowledgementAckType(Mixin):
    """Вид Повідомлення"""
    DELIVERED = 1
    ACCEPTED = 2
    REGISTERED = 3
    REJECTED = 4
    CHOICES = [
        [DELIVERED, "Сповіщення про доставку Повідомлення"],
        [ACCEPTED, "Сповіщення про прийняття Повідомлення"],
        [REGISTERED, "Сповіщення про реєстрацію документа в системі-одержувачі"],
        [REJECTED, "Сповіщення про відмову в реєстрації документа в системі-одержувачі"],
    ]



class HeaderMsgKnow(Mixin):
    """Необхідність відправлення Сповіщення"""
    NONE = 0
    ERROR_ONLY = 1
    ALWAYS = 2
    CHOICES = [
        [NONE, "Ні"],
        [ERROR_ONLY, "Тільки при помилках"],
        [ALWAYS, "Завжди.За умовчанням"],
    ]
    DEFAULT = NONE

class HeaderMsgType(Mixin):
    """Вид Повідомлення"""
    MESSAGE = 0
    DOCUMENT = 1
    DOCUMENT_ADD = 2
    DOCUMENT_REPLAY = 3
    DOCUMENT_REPLAY_ADD = 4
    CHOICES = [
        [MESSAGE, "Повідомлення"],
        [DOCUMENT, "Основний документ"],
        [DOCUMENT_ADD, "Доповнення до основного документа"],
        [DOCUMENT_REPLAY, "Документ-відповідь"],
        [DOCUMENT_REPLAY_ADD, "Доповнення до документа-відповіді"],
    ]

class DocumentType(Mixin):
    """Вид Повідомлення"""
    INCOMING = 0
    OUTGOING = 1
    STATEMENT = 2
    CHOICES = [
        [INCOMING, "вихідний"],
        [OUTGOING, "вхідний"],
        [STATEMENT, "звернення громадян"],
    ]
