import re
from django.core.exceptions import ValidationError


def mask_validator(mask):
    open_count = re.findall('({)', mask)
    close_count = re.findall('(})', mask)
    if not len(open_count) == len(close_count):
        raise ValidationError(
            '%(value)s is not valid mask',
            params={'value': mask},
        )

