from django.utils.translation import ugettext as _
from payoff.models import Transaction
from .payment import Payment


# def send_request(request, invoice, bank_port=None):
#     invoice.initialize_payment()
#     data = {
#         'invoice': invoice,
#         'amount': invoice.final_price,
#         'order_nubmer': str(invoice.id),
#         'mobile': invoice.address.receiver_mobile_number,
#         'description': _('پرداخت فاکتور %s') % invoice.id,
#         'ipg': bank_port or Transaction.IPGTypes.PEC,
#     }
#     payment = Payment(request)
#     payment.start_payment_process(data)


 

def ipg_callback(request):
    if not request.META['HTTP_ORIGIN'].startswith('https://pec.shaparak.ir') and \
        not request.META['HTTP_REFERER'].startswith('https://pec.shaparak.ir'):
        raise Exception('Invalid Origin or Referer')
    data = {
        'token': request.get('Token'),
        'order_id': request.get('OrderId'),
        'terminal_no': request.get('TerminalNo'),
        'rrn': request.get('RRN'),
        'status': request.get('status'),
        'hash_card_number': request.get('HashCardNumber'),
        'amount': request.get('Amount').replace(',',''),
        'discounted_amount': request.get('SwAmount').replace(',',''),
        'strace_no': request.get('STraceNo'),
    }
    payment = Payment(request)
    payment.transaction_callback(data) 

