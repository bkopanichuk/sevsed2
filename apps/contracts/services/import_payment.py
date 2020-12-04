import csv
import os
from datetime import datetime

from django.conf import settings
from apps.l_core.models import CoreOrganization
from apps.contracts.models.contract_model import Contract
from apps.contracts.models.contract_constants import CONTRACT_STATUS_ACTUAL
from apps.contracts.models.register_payment_model import RegisterPayment
import logging

logger = logging.getLogger(__name__)


MEDIA_ROOT = settings.MEDIA_ROOT
MEDIA_URL = settings.MEDIA_URL


class ImportClientBank():
    def __init__(self,import_payment):
        self.import_payment = import_payment

    def run(self):
        self.import_data_from_csv()

    def import_data_from_csv(self):
        """Import payment data from csv file"""
        result = []
        full_path = os.path.join(MEDIA_ROOT, self.import_payment.in_file.path)
        with  open(full_path, mode='r', encoding='cp1251') as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=';')
            for row in csv_reader:
                item = row  ##dict(row)
                edrpou: str = item.get('ЄДРПОУ кореспондента')
                corespondent: str = item.get('Кореспондент')
                kredit = item.get('Кредит')
                outer_doc_number = item.get('Документ')
                date_add = item.get('Дата документа')
                ## Знайти контрагента
                org = CoreOrganization.objects.filter(edrpou=edrpou.strip()).first()
                ## Знайти договір контрагента
                if org:
                    contracts = Contract.objects.filter(contractor=org, status=CONTRACT_STATUS_ACTUAL)
                    ## Перевіряємо кілксть дійсних договорів контрагента, якщо більше одного не імпортуємо нарахування
                    if contracts.count() > 1:
                        d = {'edrpou': edrpou,
                             'message': f'Контрагент "{corespondent}"  має {contracts.count()}  дійсних договори',
                             'status': 'error'}
                        result.append(d)
                        continue

                    elif contracts.count() == 1:
                        ## Зробити зарахування коштів
                        payment_date = datetime.strptime(date_add, '%d.%m.%Y').date()
                        contract = contracts.first()

                        try:
                            sum_payment = float(kredit)
                        except:
                            sum_payment = 0
                        logger.debug('CONTRACT:', contract, 'PAYMENT SIZE:', sum_payment)

                        payment = RegisterPayment(importer=self.import_payment, outer_doc_number=outer_doc_number, contract=contract,
                                                  payment_date=payment_date,
                                                  payment_type='import',
                                                  sum_payment=sum_payment)
                        payment.save()
                        d = {'edrpou': edrpou, 'message': f'Платіж  контрагента "{corespondent}" успішно збережено',
                             'status': 'sucess'}
                        result.append(d)
                    else:
                        d = {'edrpou': edrpou, 'message': f'Контрагент "{corespondent}" не має  дійсних договори',
                             'status': 'wrning'}
                        result.append(d)
                else:
                    d = {'edrpou': edrpou, 'message': f'Контрагента  з єдрпоу: {edrpou} не знайдено в системі',
                         'status': 'info'}
                    result.append(d)
        self.import_payment.details = result
        self.import_payment.is_imported = True
        self.import_payment.save()
        return result