from enum import Enum
import requests
from django.apps import apps
from django.conf import settings
from rest_framework.response import Response
from rest_framework.validators import ValidationError
from payoff.exceptions import NoCompletePaymentMethodException
from payoff.models import (
    Transaction, TransactionConfirmation, TransactionResult, TransactionReverse
)
from .base_payment import PaymentMethodAbstract, SUCCESS_STATUS, FAILURE_STATUS


SEP_DOMAIN = 'https://sep.shaparak.ir'


class InvalidResponseFromTokenRequestException(Exception):
    """Exception for invalid response from token request"""


class TokenNotAvailableException(Exception):
    """Exception for token not available"""


class InvalidPaymentException(Exception):
    """Exception for invalid payment"""


class SepResponseConfirmationException(Exception):
    """Exception for invalid response from sep confirmation request"""


class SepResponseRevertationException(Exception):
    """Exception for invalid response from sep revertation request"""


class ReferrerObjectNotFoundException(Exception):
    """Exception for referrer object not found"""


class TransactionNotFoundException(Exception):
    """Exception for transaction not found"""


class SepToken:
    """Token handler for sep payment method"""

    class ResponseStatuses(Enum):
        """Response statuses"""
        SUCCESS = 1
        FAILURE = -1

    class ErrorStatusCodees(Enum):
        """Error status codes"""
        CANCELED_BY_USER = 1
        OK = 2
        FAILED = 3
        SESSINO_IS_NULL = 4
        INVALID_PARAMETERS = 5
        MERCHANT_IP_ADDRESS_IS_INVALID = 8
        TOKEN_NOT_FOUND = 10
        TOKEN_REQUIRED = 11
        TERMINAL_NOT_FOUND = 12

    def __init__(self, token_expiry_in_min: int = 20):
        self.transaction: Transaction = None
        self.action = "token"
        self.amount = 0
        self.wage = 0
        self.terminal_id = settings.SEP_TERMINAL_ID
        self.res_num = None
        self.redirect_url = settings.SEP_CALLBACK_URL
        self.cell_number = None
        self.token_expiry_in_min = token_expiry_in_min
        self.status: self.ResponseStatuses = None
        self.token = None
        self.error_code: self.ErrorStatusCodees = None
        self.error_desc = None

    def send_token_request(self, transaction, save_response_to_db=True):
        """Send token request to sep"""
        self.transaction = transaction
        self.amount = transaction.amount
        self.res_num = transaction.order_number
        self.cell_number = transaction.mobile
        url = f"{SEP_DOMAIN}/onlinepg/onlinepg"
        response = requests.post(url, self._as_json())
        if not response.status_code == 200:
            raise InvalidResponseFromTokenRequestException()
        try:
            data = response.json()
        except requests.JSONDecodeError:
            raise InvalidResponseFromTokenRequestException()

        self._parse_response(data)
        if save_response_to_db:
            self._save_token_response_to_db()

    def _as_json(self):
        return {
            "action": self.action,
            "TerminalId": self.terminal_id,
            "Amount": self.amount,
            "ResNum": self.res_num,
            "RedirectUrl": self.redirect_url,
            "CellNumber": self.cell_number
        }

    def _parse_response(self, data: dict):
        self.status = data['status']
        self.error_code = data.get('errorCode')
        self.error_desc = data.get('errorDesc')
        self.token = data.get('token')

    def get_redirect_url(self):
        """Get redirect url for sep"""
        return f"{SEP_DOMAIN}/OnlinePG/SendToken?token={self.token}"

    def _save_token_response_to_db(self):
        self.transaction.token = self.token
        self.transaction.token_request_status = self.error_code
        self.transaction.token_request_message = self.error_desc
        self.transaction.save()

    def is_valid(self):
        """Check if token is valid"""
        if not self.token:
            return False
        return self.status == self.ResponseStatuses.SUCCESS.value


class SepResponse:
    """Response handler for sep payment method"""

    class ResponseStatusDigitCodes(Enum):
        """Response status digit codes defined by sep"""
        CANCELED_BY_USER = 1
        OK = 2
        FAILED = 3
        SESSION_IS_NULL = 4
        INVALID_PARAMETERS = 5
        MERCHANT_IP_ADDRESS_IS_INVALID = 8
        TOKEN_NOT_FOUND = 10
        TOKEN_REQUIRED = 11
        TERMINAL_NOT_FOUND = 12

    class ResponseStatusTextCodes(Enum):
        """Response status english codes defined by sep"""
        CANCELED_BY_USER = "CanceledByUser"
        OK = "OK"
        FAILED = "Failed"
        SESSION_IS_NULL = "SessionIsNull"
        INVALID_PARAMETERS = "InvalidParameters"
        MERCHANT_IP_ADDRESS_IS_INVALID = "MerchantIpAddressIsInvalid"
        TOKEN_NOT_FOUND = "TokenNotFound"
        TOKEN_REQUIRED = "TokenRequired"
        TERMINAL_NOT_FOUND = "TerminalNotFound"

    class ResponseStatusDesc(Enum):
        """Response status descriptions defined by sep"""
        CANCELED_BY_USER = "کاربر انصراف داده است"
        OK = "پرداخت با موفقیت انجام شد"
        FAILED = "پرداخت انجام نشد."
        SESSION_IS_NULL = "کاربر در بازه زمانی تعیین شده پاسخی ارسال￼نکرده است"
        INVALID_PARAMETERS = "پارامترهای ارسالی نامعتبر است."
        MERCHANT_IP_ADDRESS_IS_INVALID = (
            "آدرس سرور پذیرنده نامعتبر است (در پرداخت های بر پایه توکن)"
        )
        TOKEN_NOT_FOUND = "توکن ارسال شده یافت نشد."
        TOKEN_REQUIRED = (
            "با این شماره ترمینال فقط تراکنش های توکنی قابل پرداخت هستند."
        )
        TERMINAL_NOT_FOUND = "شماره ترمینال ارسال شده یافت نشد."

    def __init__(self, data):
        self.mid = int(data['MID'])
        self.state = data['State']
        self.status = int(data['Status'])
        self.rrn = int(data['Rrn'])
        self.ref_num = data['RefNum']
        self.res_num = int(data['ResNum'])
        self.terminal_id = int(data['TerminalId'])
        self.trance_no = int(data['TraceNo'])
        self.amount = int(data['Amount'])
        self.wage = data['Wage']
        self.secure_pan = data['SecurePan']
        self.hashed_card_number = data['HashedCardNumber']
        self.transaction: Transaction = None
        self.transaction_result: TransactionResult = None

    def save_to_db(self):
        """Save response to db and link it to transaction and transaction result"""
        self.transaction_result = self._create_transaction_result()
        self.transaction = self._get_transaction()
        if TransactionResult.objects.filter(transaction=self.transaction).exists():
            raise InvalidPaymentException()
        self.transaction_result.transaction = self.transaction
        self.transaction_result.save()

    def _create_transaction_result(self):
        transaction_result = TransactionResult()
        transaction_result.order_id = self.res_num
        transaction_result.terminal_no = self.terminal_id
        transaction_result.rrn = self.rrn
        transaction_result.status = self.status
        transaction_result.hash_card_number = self.hashed_card_number
        transaction_result.amount = self.amount
        transaction_result.ref_number = self.ref_num
        extra_data = {
            'mid': self.mid,
            'state': self.state,
            'trance_no': self.trance_no,
            'wage': self.wage,
            'secure_pin': self.secure_pan,
        }
        transaction_result.extra_data = extra_data
        transaction_result.save()
        return transaction_result

    def _get_transaction(self):
        try:
            return Transaction.objects.get(order_number=self.res_num)
        except Transaction.DoesNotExist:
            raise TransactionNotFoundException()
        except Transaction.MultipleObjectsReturned:
            raise InvalidPaymentException()

    def validate_payment(self):
        """Validate payment with sep instructions

        There are 3 main condition to validate payment:
            - status must be integer 2
            - state must be string 'OK'
            - ref_num shouldn't be in our database (ref_num is unique)
        """
        if self.status != self.ResponseStatusDigitCodes.OK.value:
            raise InvalidPaymentException()
        if self.state != self.ResponseStatusTextCodes.OK.value:
            raise InvalidPaymentException()
        if self._ref_num_exists_before():
            raise InvalidPaymentException()

    def confirm_payment(self):
        """Send payment confirmation to sep

        After each success payment, we should send confirmation to sep, otherwise sep will revert payment.
        Our payment is confirmed after sep confirmation is send and saved to db and the result is valid too.
        """
        confirmation = SepResponseConfirmation(self.ref_num, self.terminal_id)
        confirmation.send_request()
        confirmation.save_to_db()
        confirmation.validate_response()

    def revert_payment(self):
        """Revert payment to sep

        This is called when payment confirmation is not valid. so we should revert payment to sep and
        cancel our user purchase process in our system.
        """
        revertation = SepResponseRevertation(self.ref_num, self.terminal_id)
        revertation.send_request()
        revertation.save_to_db()
        revertation.validate_response()

    def _ref_num_exists_before(self):
        ref = self.ref_num
        return TransactionResult.objects.filter(ref_number=ref).count() > 1


class SepResponseConfirmation:
    """Sep response confirmation class"""

    class ResponseStatusCodes(Enum):
        """Response status codes defined by sep"""
        INVALID_IP_ADDRESS = -106
        TERMINAL_NOT_FOUND = -105
        TERMINAL_IS_DEACTIVE = -104
        EXPIERATION_OF_30_MINUTES = -6
        NOT_FOUND = -2
        SUCCESS = 0
        DUPLICAT_REQUEST = 2

    URL = f"{SEP_DOMAIN}/verifyTxnRandomSessionkey/ipg/VerifyTransaction"
    EXCEPTION_CLASS = SepResponseConfirmationException

    def __init__(self, ref_num, terminal_number):
        self.ref_num = ref_num
        self.terminal_number = terminal_number
        self.rrn = None
        self.masked_pan = None
        self.hashed_pan = None
        self.orginal_amount = None
        self.effective_amount = None
        self.strace_date = None
        self.strace_no = None
        self.result_code = None
        self.result_description = None
        self.success = None
        self.transaction_result = None
        self.response = None

    def send_request(self):
        """Send request to sep and parse data to class attributes"""
        data = {
            "RefNum": self.ref_num,
            "TerminalNumber": self.terminal_number,
        }
        response = requests.post(self.URL, data=data)
        if response.status_code != 200:
            raise self.EXCEPTION_CLASS()
        try:
            data = response.json()
        except requests.JSONDecodeError:
            raise self.EXCEPTION_CLASS()
        self._parse_response(data)

    def save_to_db(self):
        """Save response to db as TransactionConfirmation model"""
        transaction_confirmation = TransactionConfirmation()
        transaction_confirmation.status = self.result_code
        transaction_confirmation.card_number_masked = self.masked_pan
        transaction_confirmation.rrn = self.rrn
        transaction_confirmation.transaction_result = self.transaction_result
        transaction_confirmation.extra_data = self.response
        transaction_confirmation.save()

    def validate_response(self):
        """Validate response from sep"""
        if not self.transaction_result:
            raise self.EXCEPTION_CLASS()
        if (
            self.result_code != self.ResponseStatusCodes.SUCCESS.value and
            self.result_code != self.ResponseStatusCodes.DUPLICAT_REQUEST.value
        ):
            raise self.EXCEPTION_CLASS()
        initial_payment_amount = str(self.transaction_result.amount)
        if (
            initial_payment_amount != str(self.effective_amount) or
            initial_payment_amount != str(self.orginal_amount)
        ):
            raise self.EXCEPTION_CLASS()
        if not self.success:
            raise self.EXCEPTION_CLASS()

    def _parse_response(self, response):
        self.response = response
        self.ref_num = response['TransactionDetail']['RefNum']
        self.rrn = response['TransactionDetail']['RRN']
        self.masked_pan = response['TransactionDetail']['MaskedPan']
        self.hashed_pan = response['TransactionDetail']['HashedPan']
        self.terminal_number = response['TransactionDetail']['TerminalNumber']
        self.orginal_amount = response['TransactionDetail']['OrginalAmount']
        self.effective_amount = response['TransactionDetail']['AffectiveAmount']
        self.strace_date = response['TransactionDetail']['StraceDate']
        self.strace_no = response['TransactionDetail']['StraceNo']
        self.result_code = response['ResultCode']
        self.result_description = response['ResultDescription']
        self.success = response['Success']
        self.transaction_result = self._get_transaction_result_or_none()

    def _get_transaction_result_or_none(self):
        ref_num = self.ref_num
        return TransactionResult.objects.filter(ref_number=ref_num).first()


class SepResponseRevertation(SepResponseConfirmation):
    """Sep response revertation class"""

    URL = f"{SEP_DOMAIN}/verifyTxnRandomSessionkey/ipg/ReverseTransaction"
    EXCEPTION_CLASS = SepResponseRevertationException

    def save_to_db(self):
        """Save response to db as TransactionReverse model"""
        transaction_reverse = TransactionReverse()
        transaction_reverse.status = self.result_code
        transaction_reverse.message = self.result_description
        transaction_reverse.transaction_result = self.transaction_result
        transaction_reverse.extra_data = self.response
        transaction_reverse.save()


class SepPaymentMethod(PaymentMethodAbstract):

    def initiate_payment(self, data):
        self.transaction = self._create_transaction(data)
        token = SepToken()
        token.send_token_request(self.transaction, save_response_to_db=True)
        if token.is_valid():
            return Response({
                'url': token.get_redirect_url()
            })
        raise ValidationError(f'{token.error_code} {token.error_desc}')

    def callback(self, data):
        response = SepResponse(data)
        try:
            response.save_to_db()
            referrer_object = self._get_referrer_object(
                response.transaction_result)
            response.validate_payment()
            response.confirm_payment()
            referrer_object.complete_payment()
            return {'status': SUCCESS_STATUS, 'code': referrer_object.id}
        except (InvalidPaymentException, ReferrerObjectNotFoundException):
            pass
        except SepResponseConfirmationException:
            referrer_object.revert_payment()
        self._revert_payment(response)
        return {'status': FAILURE_STATUS, 'code': response.transaction_result.order_id}

    def _revert_payment(self, response):
        try:
            response.revert_payment()
        except:
            pass

    def _create_transaction(self, data):
        transaction = Transaction.objects.create(**data)
        return transaction

    def _get_referrer_object(self, transaction_result):
        """Get referrer object from transaction_result"""
        order_number = transaction_result.transaction.order_number
        if isinstance(order_number, str):
            order_number = int(order_number)
        app_label = transaction_result.transaction.referrer_app
        model_name = transaction_result.transaction.referrer_model
        referrer_model = apps.get_model(app_label, model_name)
        if not hasattr(referrer_model, 'complete_payment'):
            raise NoCompletePaymentMethodException()
        return referrer_model.objects.get(payment_unique_id=order_number)
