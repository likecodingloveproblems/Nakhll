from django.utils.translation import gettext as _
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.exceptions import APIException


class NoItemException(APIException):
    """No item in invoice"""
    default_detail = _('هیچ محصولی در این فاکتور وجود ندارد. لطفا مجددا سبد خرید خود را ایجاد کنید')


class NoTransactionException(APIException):
    """Validation raised when a transaction is not found."""
    status_code = HTTP_400_BAD_REQUEST


class NoCompletePaymentMethodException(APIException):
    """Validation raised when complete_payment method for given model is not found."""
    status_code = HTTP_400_BAD_REQUEST


class NoAddressException(APIException):
    """Validation raised when user didn't choose any address for invoice."""
    status_code = HTTP_400_BAD_REQUEST
    default_detail = {'error': 'آدرس خریدار را تکمیل کنید'}


class OutOfPostRangeProductsException(APIException):
    """Validation raised when product cannot shipped to user's address."""
    invalid_products = []
    status_code = HTTP_400_BAD_REQUEST
    default_detail = 'برخی از محصولات خریداری شده خارج از محدوده ارسال می باشند'


class InvoiceExpiredException(APIException):
    """Validation raised when time to pay for invoice is expired."""
    status_code = HTTP_400_BAD_REQUEST
    default_detail = {'error': 'فاکتور منقضی شده است'}


class InvalidInvoiceStatusException(APIException):
    """Validation raised when invoice status is invalid."""
    status_code = HTTP_400_BAD_REQUEST
    default_detail = {'error': 'فاکتور در حال حاضر قابل پرداخت نیست'}
