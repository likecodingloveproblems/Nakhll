from rest_framework.exceptions import APIException
from rest_framework.status import HTTP_400_BAD_REQUEST

class EmptyCartException(APIException):
    default_detail = {'errors': ['سبد خرید خالی است!']}
    status_code = HTTP_400_BAD_REQUEST
