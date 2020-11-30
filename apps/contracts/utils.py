from datetime import date

from dateutil.relativedelta import relativedelta


def default_end_period():
    return date.today() + relativedelta(years=1)