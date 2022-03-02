import json
from datetime import datetime
from re import I
from django.conf import settings
from django.http.response import HttpResponse
from django.shortcuts import redirect, render
from payoff.payment import Payment, Pec
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
        'referrer_app': 'invoice',
        'amount': int(amount),
        'order_number': int(order_number),
        'description': f'Paying invioce {order_number}',
        'ipg': Transaction.IPGTypes.PEC,
        'mobile': mobile,
    }
    return Payment.initiate_payment(data)

@csrf_exempt
def test_pec_callback(request):
    # TODO
    # if not request.META['HTTP_ORIGIN'].startswith('https://pec.shaparak.ir')\
        # or not request.META['HTTP_REFERER'].startswith('https://pec.shaparak.ir'):
        # raise Exception('Invalid origin or referer')
    domain = settings.DOMAIN_NAME

    # FAKE DATA FOR TESTING
    # sample_data = {
    #     'OrderId': '1633353467624477',
    #     'Token': 123131,
    #     'Stauts': 0,
    #     'RRN': 133,
    #     'TerminalNo': 1345214,
    #     'Amount': '2180000'
    # }
    # result = Payment.payment_callback(sample_data, ipg_type=Transaction.IPGTypes.PEC)
    # result_dict = result.__dict__
    # result_dict['_state'] = None
    # result_dict['created_datetime'] = None

    result = Payment.payment_callback(request.POST, ipg_type=Transaction.IPGTypes.PEC)

    code = result.get('code')
    if result.get('status') == Pec.SUCCESS_STATUS:
        return redirect(f'{domain}/cart/payment/success/data?code={code}')
    return redirect(f'{domain}/cart/payment/failure/data?code={code}')