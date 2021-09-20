import json
from datetime import datetime
from django.http.response import HttpResponse
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
    sample_data = {
        'Token': request.GET.get('token') or 12863129837,
        'OrderId': request.GET.get('order') or 98712341264,
        'TerminalNo':  request.GET.get('term') or 1321,
        'RRN': request.GET.get('rrn') or 357823,
        'Status': request.GET.get('status') or 0,
        'HashCardNumber': request.GET.get('card') or '585983***9490',
        'Amount': request.GET.get('amount') or '120000',
    }
    # result = Payment.payment_callback(request.POST, ipg_type=Transaction.IPGTypes.PEC)
    result = Payment.payment_callback(sample_data, ipg_type=Transaction.IPGTypes.PEC)
    result_dict = result.__dict__
    result_dict['_state'] = None
    result_dict['created_datetime'] = None
    return HttpResponse(json.dumps(result_dict), content_type='application/json')