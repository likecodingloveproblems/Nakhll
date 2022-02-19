import os
from abc import ABC, abstractmethod
from django.shortcuts import redirect
from django.apps import apps
from django.utils.translation import ugettext as _
from rest_framework.validators import ValidationError
from rest_framework.response import Response
from nakhll_market.interface import AlertInterface
from payoff.models import Transaction, TransactionResult, TransactionConfirmation, TransactionReverse
from payoff.exceptions import NoCompletePaymentMethodException, NoTransactionException
from zeep import Client


class PaymentMethod(ABC):
    def __init__(self, *args, **kwargs):
        self.transaction = None

    @abstractmethod
    def initiate_payment(self, data):
        ''' Generate ipg url and redirect user to that url '''

    @abstractmethod
    def callback(self, data):
        ''' Handle returned data from IPG 
        
            Validate IPG response and update transaction result, connect data
            to transaction object
        '''

class Pec(PaymentMethod):

    __SUCCESS_STATUS_CODE = 0
    __SUCCESS_TOKEN_MIN_VALUE = 0
    __SUCCESS_RRN_MIN_VALUE = 0
    SUCCESS_STATUS = 'success'
    FAILURE_STATUS = 'failure'
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        # TODO: These errors should be handled better with better messages
        pec_pin = os.environ.get('PEC_PIN')
        callback_url = format(os.environ.get('CALLBACKURL'))
        if not pec_pin:
            raise ValidationError(_('در حال حاضر امکان اتصال به درگاه بانکی وجود ندارد'))
        if not callback_url:
            raise ValidationError(_('در حال حاضر امکان اتصال به درگاه بانکی وجود ندارد'))
        self.pec_pin = pec_pin
        self.callback_url = callback_url
        self.sale_service = self.__get_sale_serivce()
        self.confirm_service = self.__get_confirm_service()
        self.reverse_service = self.__get_reverse_service()
        self.sale_request_data = self.__get_client_sale_request_data()
        self.confirm_request_data = self.__get_client_confirm_request_data()
        self.reverse_request_data = self.__get_client_reversal_request_data()

    def __get_sale_serivce(self):
        return Client(
            'https://pec.shaparak.ir/NewIPGServices/Sale/SaleService.asmx?wsdl')

    def __get_confirm_service(self):
        return Client(
            'https://pec.shaparak.ir/NewIPGServices/Confirm/ConfirmService.asmx?wsdl')

    def __get_reverse_service(self):
        reverseService = Client('https://pec.shaparak.ir/NewIPGServices/Reverse/ReversalService.asmx?wsdl')
        return reverseService

    def __get_client_sale_request_data(self):
        return self.sale_service.get_type('ns0:ClientSaleRequestData')
        
    def __get_client_reversal_request_data(self):
        return self.reverse_service.get_type('ns0:ClientReversalRequestData')
    
    def __get_client_confirm_request_data(self):
        return self.confirm_service.get_type('ns0:ClientConfirmRequestData')


    def initiate_payment(self, data):
        ''' Get invoice, exchange with token and redirect user to payment page '''
        self.transaction = self._create_transaction(data)
        token_object = self._get_token_object()
        self._save_token_object(token_object)
        if not self.is_token_object_valid(token_object):
            raise ValidationError(f'{token_object.Status} {token_object.Message}')
        url = f'https://pec.shaparak.ir/NewIPG/?token={token_object.Token}'
        return Response({'url': url})

    def _get_token_object(self):
        ''' Get sale service and send invocie data to it, return token if 
            invoice data is valid 
        '''
        token_request_object = self._generate_token_request_object()
        token_response_object = self._get_token_response_object(
            token_request_object)
        return token_response_object

        
    def _generate_token_request_object(self):
        return self.sale_request_data(
            LoginAccount=self.pec_pin,
            Amount=self.transaction.amount,
            OrderId=self.transaction.order_number,
            CallBackUrl=self.callback_url,
            AdditionalData=self.transaction.description,
            Originator=self.transaction.mobile)

    def _get_token_response_object(self, token_request):
        ''' Send token request to IPG and return response object '''
        return self.sale_service.service.SalePaymentRequest(token_request)

    def is_token_object_valid(self, token_object):
        ''' Check if token is valid '''
        return False if token_object.Status != self.__SUCCESS_STATUS_CODE\
            or token_object.Token <= self.__SUCCESS_TOKEN_MIN_VALUE else True

    def _save_token_object(self, token_object):
        ''' Store result of token request from IPG to DB'''
        self.transaction.token_request_status =token_object.Status
        self.transaction.token_request_message = token_object.Message
        self.transaction.token = token_object.Token
        self.transaction.save()


    def callback(self, data):
        ''' Get data from Pec gateway and render it'''
        parsed_data = self._parse_callback_data(data)
        transaction_result = self._create_transaction_result(parsed_data)
        transaction_result = self._link_to_transaction(transaction_result)
        if self._is_tarnsaction_result_succeded(transaction_result):
            response = self.__send_confirmation_request(transaction_result)
            self.__create_transaction_confirmation(response, transaction_result)
            if response and self.__confirmation_response_is_valid(response):
                referrer_object = self._complete_payment(transaction_result)
                return {'status': self.SUCCESS_STATUS, 'code': referrer_object.id}
            else:
                AlertInterface.developer_alert(where='confirm_trans',
                                                trans_id=transaction_result.transaction.id,
                                                trans_res_id=transaction_result.id)
                AlertInterface.payment_not_confirmed(transaction_result)
        self._revert_transaction(transaction_result)
        return {'status': self.FAILURE_STATUS, 'code': transaction_result.order_id}
    
    def _parse_callback_data(self, data):
        ''' Parse data from Pec gateway '''
        return {
            'token': data.get('Token', 0),
            'order_id': data.get('OrderId', 0),
            'terminal_no': data.get('TerminalNo', 0),
            'rrn': data.get('RRN', 0),
            'status': data.get('Status', 0),
            'hash_card_number': data.get('HashCardNumber', ''),
            'amount': self._parse_amount(data.get('Amount', '0')),
            'discounted_amount': self._parse_amount(data.get('SwAmount', '0')),
        }

    def _parse_amount(self, amount):
        ''' Parse amount from Pec gateway '''
        return int(amount.replace(',',''))

    def _create_transaction(self, data):
        transaction = Transaction.objects.create(**data)
        return transaction

    def _create_transaction_result(self, data):
        transaction_result = TransactionResult.objects.create(**data)
        return transaction_result

    def _link_to_transaction(self, transaction_result):
        try:
            transaction = Transaction.objects.get(
                order_number=transaction_result.order_id)
        except Exception as e:
            AlertInterface.developer_alert(where='link_to_trans', trans_res_id=transaction_result.id, error=str(e))
            raise NoTransactionException(f'No transaction found for order_id:\
                {transaction_result.order_id}')
        transaction_result.transaction = transaction
        try:
            transaction_result.save()
        except Exception as e:
            # There may be a TransactionResult.objects.get(transaction=transaction) which cause integrity error
            # This may occure when the response is sent twice from Pec gateway
            # We simply send an alert to Discord and continue,
            AlertInterface.developer_alert(where='link_to_trans', trans_res_id=transaction_result.id, error=str(e))
        return transaction_result

    def _is_tarnsaction_result_succeded(self, transaction_result):
        ''' Send request to IGP validation url and validate transaction '''
        status = int(transaction_result.status)
        rrn = int(transaction_result.rrn)
        if status== self.__SUCCESS_STATUS_CODE and rrn > self.__SUCCESS_RRN_MIN_VALUE:
            return True
        return False

    def _complete_payment(self, transaction_result):
        ''' Send transaction_result to referrer model to finish purchase process'''
        referrer_object = self.__get_referrer_object(transaction_result)
        referrer_object.complete_payment()
        return referrer_object

    def __send_confirmation_request(self, transaction_result):
        ''' Validate payment '''
        try:
            pec_pin = self.pec_pin
            token = transaction_result.transaction.token
            request_data =self.confirm_request_data(LoginAccount=pec_pin, Token=token)
            response = self.confirm_service.service.ConfirmPayment(request_data)
            return response
        except:
            return None

    def __confirmation_response_is_valid(self, response):
        if response.Token > self.__SUCCESS_TOKEN_MIN_VALUE and response.Status == self.__SUCCESS_STATUS_CODE:
            return True
        return False

    def _revert_transaction(self, transaction_result):
        ''' Send transaction_result to referrer model to finish purchase process'''
        self.__reverse_referrer_model(transaction_result)
        self.__send_reverse_request(transaction_result) 
        return transaction_result

    def __reverse_referrer_model(self, transaction_result):
        ''' Send transaction_result to referrer model to cancel purchase process'''
        referrer_object = self.__get_referrer_object(transaction_result)
        referrer_object.revert_payment()

    def __send_reverse_request(self, transaction_result):
        requestData = self.reverse_request_data(LoginAccount=self.pec_pin, Token=transaction_result.token)
        response = self.reverse_service.service.ReversalRequest(requestData)
        if response:
            self.__create_transaction_reverse(response, transaction_result)
        else:
            AlertInterface.reverse_payment_error(transaction_result, desc='No response from Pec gateway', response=response)
        return response

    def __create_transaction_confirmation(self, response, transaction_result):
        try:
            TransactionConfirmation.objects.create(**{
                'status': response.Status,
                'card_number_masked': response.CardNumberMasked,
                'token': response.Token,
                'rrn': response.RRN,
                'transaction_result': transaction_result,
            })
        except Exception as e:
            AlertInterface.developer_alert(where='create_trans_confirm', 
                                            trans_res=transaction_result.id, 
                                            error=e, response=response)

    def __create_transaction_reverse(self, response, transaction_result):
        try:
            TransactionReverse.objects.create(**{
                'status': response.Status,
                'messsage': response.Message,
                'token': response.Token,
                'transaction_result': transaction_result,
            })
        except:
            pass



    def __get_referrer_object(self, transaction_result):
        ''' Get referrer object from transaction_result '''
        order_number = transaction_result.transaction.order_number
        if isinstance(order_number, str):
            order_number = int(order_number)
        app_label = transaction_result.transaction.referrer_app
        model_name = transaction_result.transaction.referrer_model
        referrer_model = apps.get_model(app_label, model_name) 
        if not hasattr(referrer_model, 'complete_payment'):
            raise NoCompletePaymentMethodException()
        return referrer_model.objects.get(payment_unique_id=order_number)
        





class ZarinPal(PaymentMethod):
    ''' Zarinpal ipg implementation '''



class Payment:
    @staticmethod
    def initiate_payment(data):
        ipg_type = data.get('ipg')
        ipg_class = Payment._get_ipg_class(ipg_type)
        ipg = ipg_class()
        return ipg.initiate_payment(data)

    @staticmethod
    def payment_callback(data, ipg_type):
        ipg_class = Payment._get_ipg_class(ipg_type)
        ipg = ipg_class()
        result = ipg.callback(data)
        return result

    @staticmethod
    def _get_ipg_class(ipg_type):
        if ipg_type == Transaction.IPGTypes.PEC:
            return Pec
        if ipg_type == Transaction.IPGTypes.ZARINPAL:
            return ZarinPal


