
from rest_framework.exceptions import APIException

class ServiceException(APIException):
    status_code = 409
    default_detail = ''
    #default_code = 'service_unavailable'




class AuthorNotSet(Exception):
    pass


class AuthorOrganizationNotSet(Exception):
    pass