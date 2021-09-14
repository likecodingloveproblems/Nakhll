from datetime import datetime
from django.shortcuts import render
from payoff.payment import Payment
from payoff.interfaces import PaymentInterface
from payoff.models import Transaction
from django.views.decorators.csrf import csrf_exempt

# Create your views here.

def test_pec(request):
    amount = request.GET.get('amount', '10000')
    mobile = request.GET.get('mobile', '09384918664')
    order_number = str(int(datetime.now().timestamp() * 1000000)).strip()
    data = {
        'referrer_model': 'Invoice',
        'referrer_app': 'accounting_new',
        'amount': int(amount),
        'order_number': int(order_number),
        'description': f'پرداخت فاکتور {order_number}',
        'ipg': Transaction.IPGTypes.PEC,
        'mobile': mobile,
    }
    return Payment.initiate_payment(data)

@csrf_exempt
def test_pec_callback(request):
    #TODO: Check if shaparak send this request or not
    return Payment.payment_callback(request.POST, ipg_type=Transaction.IPGTypes.PEC)