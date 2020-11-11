import datetime

from apps.document.models.document_constants import INCOMING
from apps.document.models.document_model import BaseDocument


class SetReplyDate:
    """ Встановлює кінцеву дату відповіді на документ """
    def __init__(self, doc):
        self.document: BaseDocument = doc

    def run(self):
        self.set_reply_date()
        return self.document

    def set_reply_date(self):
        """ Встановлює кінцеву дату відповіді на документ """
        ##Якщо дата вже вказана пропускаємо
        if self.document.reply_date:
            return

        ## може бути відсутнім при інтеграції з СЕВ ОВВ
        ## TODO точнити, чи вказуються типи листів при інтеграції при СЕВ ОВВ
        if not self.document.incoming_type:
            return

        if self.document.document_cast == INCOMING:
            if self.document.date_add and self.document.incoming_type.execute_interval:
                self.document.reply_date = (self.document.date_add + datetime.timedelta(
                    days=self.document.incoming_type.execute_interval)).date()