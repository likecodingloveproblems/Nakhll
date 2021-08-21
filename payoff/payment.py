from abc import ABC, abstractmethod
from django.shortcuts import redirect
from django.conf import settings
from django.utils.translation import ugettext as _
from rest_framework.response import Response
from rest_framework.validators import ValidationError
from payoff.models import Transaction, TransactionResult
from zeep import Client


class PaymentMethod(ABC):
    def __init__(self, transaction):
        self.transaction = transaction
        self.client = Client(settings.PAYMENT_WSDL)
        self.payment_method = self.client.get_type('ns0:PaymentMethod')
        self.payment_method_type = self.client.get_type('ns0:PaymentMethodType')

    def get_payment_method(self):
        return self.payment_method(
            paymentMethodType=self.payment_method_type(
                id=self.transaction.payment_method
            )
        )
    
    @abstractmethod
    def do_transaction(self, transaction):
        pass


class Pec(PaymentMethod):
    pec_pin = settings.get('PEC_PIN')
    callback_url = settings.get('CALLBACKURL')

    def __init__(self):
        # TODO: These errors should be handled better with better messages
        if not self.pec_pin:
            raise ValidationError(_('در حال حاضر امکان اتصال به درگاه بانکی وجود ندارد'))
        if not self.callback_url:
            raise ValidationError(_('در حال حاضر امکان اتصال به درگاه بانکی وجود ندارد'))

    def do_transaction(self, transaction):
        ClientSaleRequestData = self.get_client_sale_request_data()
        requestData = ClientSaleRequestData(LoginAccount=self.pec_pin, Amount=transaction.amount,
                        OrderId=transaction.order_number, CallBackUrl=self.callback_url,
                        AdditionalData=transaction.description, Originator=transaction.mobile)
        saleService = self.get_sale_serivce()
        result = saleService.service.SalePaymentRequest(requestData)
        transaction.message = result['Message']
        transaction.token = result['Token']
        transaction.status = result['Status']
        transaction.save()

        if result['Status'] == 0:
            return redirect('https://pec.shaparak.ir/NewIPG/?token={}'.format(result['Token']))
        else:
            return redirect('SOME_ERROR_MESSAGE_PAGE')



    # TODO we must handle exceptions of SOAP connections
    def get_sale_serivce():
        saleService = Client('https://pec.shaparak.ir/NewIPGServices/Sale/SaleService.asmx?wsdl')
        return saleService

    def get_client_sale_request_data(self):
        saleService = self.get_sale_serivce()
        ClientSaleRequestData = saleService.get_type('ns0:ClientSaleRequestData')
        return ClientSaleRequestData


class ZarinPal(PaymentMethod):
    def __init__(self):
        pass
    # def zarin_pay():
    #     result = client.service.PaymentRequest(MERCHANT, amount, description, email, mobile, CallbackURL)
    #     if result.Status == 100:
    #         return redirect('https://www.zarinpal.com/pg/StartPay/' + str(result.Authority))
    #     else:
    #         return HttpResponse('Error code: ' + str(result.Status))




class Payment():
    def __init__(self, request):
        self.request = request


    def get_ipg_class(self, ipg_type):
        if ipg_type == Transaction.IPGTypes.PEC:
            return Pec
        if ipg_type == Transaction.IPGTypes.ZARINPAL:
            return ZarinPal

    def start_payment_process(self, data):
        self.transaction = Transaction.objects.create(**data)
        ipg_class = self.get_ipg_class(self.transaction.ipg_type)
        ipg = ipg_class()
        ipg.do_transaction(self.transaction)
        # return Response(ipg.transaction.message)

    def complete_transaction(self, posted_data):
        data = {
            'token': posted_data.get('Token'),
            'order_id': posted_data.get('OrderId'),
            'terminal_no': posted_data.get('TerminalNo'),
            'rrn': posted_data.get('RRN'),
            'status': posted_data.get('status'),
            'hash_card_number': posted_data.get('HashCardNumber'),
            'amount': posted_data.get('Amount').replace(',',''),
            'discounted_amount': posted_data.get('SwAmount').replace(',',''),
            'strace_no': posted_data.get('STraceNo'),
        }
        transaction_result = TransactionResult.objects.create(**data)


        try:
            self.transaction = Transaction.objects.get(invoice_id=data.get('order_id'))
            self.transaction.invoice.cart.complete() # TODO: This should change cart status to complete
            self.transaction.invoice.complete() # TODO: This should change invoice status to complete, create alert,
                                                # send email and sms to customer and shop owner, reduce stock, etc.
                                                # create an order for shop owner to send product to customer
            self.transaction.complete() # TODO: This should change transaction status to complete
            transaction_result.transaction = self.transaction
            transaction_result.save()
        except:
            self.no_transaction_error(transaction_result)


    def no_transaction_error(self, transaction_result):
        ''' Set alert for admin to check this transaction '''
