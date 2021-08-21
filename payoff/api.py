from django.utils.translation import ugettext as _
from payoff.models import Transaction
from .payment import Payment


def send_request(request, invoice, bank_port=None):
    data = {
        'invoice': invoice,
        'amount': invoice.final_price,
        'mobile': invoice.address.receiver_mobile_number,
        'description': _('پرداخت فاکتور %s') % invoice.id,
        'ipg': bank_port or Transaction.IPGTypes.PEC,
    }
    payment = Payment(request)
    payment.start_payment_process(data)


 

def ipg_callback(request):
    if not request.META['HTTP_ORIGIN'].startswith('https://pec.shaparak.ir') and \
        not request.META['HTTP_REFERER'].startswith('https://pec.shaparak.ir'):
        raise Exception('Invalid Origin or Referer')

    payment = Payment(request)
    payment.complete_transaction(request.POST) 

