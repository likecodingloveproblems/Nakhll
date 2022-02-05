from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.exceptions import APIException
class NoItemValidation(APIException):
    """No item in invoice"""

class NoTransactionException(APIException):
    """
    Validation raised when a transaction is not found.
    """
    status_code = HTTP_400_BAD_REQUEST

class NoCompletePaymentMethodException(APIException):
    """
    Validation raised when complete_payment method for given model is not found.
    """
    status_code = HTTP_400_BAD_REQUEST

class NoAddressException(APIException):
    status_code = HTTP_400_BAD_REQUEST
    default_detail = {'error': 'آدرس خریدار را تکمیل کنید'}

class OutOfPostRangeProductsException(APIException):
    invalid_products = []
    status_code = HTTP_400_BAD_REQUEST
    default_detail = 'برخی از محصولات خریداری شده خارج از محدوده ارسال می باشند'

class InvoiceExpiredException(APIException):
    status_code = HTTP_400_BAD_REQUEST
    default_detail = {'error': 'فاکتور منقضی شده است'}

class InvalidInvoiceStatusException(APIException):
    status_code = HTTP_400_BAD_REQUEST
    default_detail = {'error': 'فاکتور در حال حاضر قابل پرداخت نیست'}