
class CalculateAccruals():
    def __init__(self,contract):
        self.import_payment = contract

    def calculate_accruals(contract, start_date=None, end_date=None, create_pdf=None, is_comercial=None, is_budget=None):
        """ Розраховує нарахування для всіх договорів"""
        logging.debug('calculate_accruals')
        contracts = contract.objects.filter(expiration_date__gte=(end_date or date.today()))
        result = []
        for contract in contracts:
            res = RegisterAccrual.calculate_accruals(contract=contract, start_date=start_date, end_date=end_date)
            result.append(res)
        return result