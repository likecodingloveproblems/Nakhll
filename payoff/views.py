from datetime import datetime
from django.conf import settings
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from .base_payment import SUCCESS_STATUS
from .interfaces import Payment
from .models import Transaction


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

    result = Payment.payment_callback(
        request.POST, ipg_type=Transaction.IPGTypes.PEC)

    code = result.get('code')
    if result.get('status') == SUCCESS_STATUS:
        return redirect(f'{domain}/cart/payment/success/data?code={code}')
    return redirect(f'{domain}/cart/payment/failure/data?code={code}')


@csrf_exempt
def sep_callback(request):
    # TODO
    # test for domain and referer to prevent malicious requests
    domain = settings.DOMAIN_NAME
    data = request.POST
    # data = {
    #     "MID": 0,
    #     "State": "OK",
    #     "Status": 2,
    #     "Rrn": "20403692290",
    #     "RefNum": "GmshtyjwKSsl2nL3Y8NwgR95nIloT0pmWXTiAC%2Fbj9",
    #     "ResNum": 1657655845646725,
    #     "TerminalId": 21457185,
    #     "TraceNo": 403975,
    #     "Amount": 10000,
    #     "Wage": None,
    #     "SecurePan": "585983******9490",
    #     "HashedCardNumber": "AC61BF88CBFFABC9A25B4D5F1116B396D98F5FCE3DC103D94609983DD0E972D4",
    #     "AffectiveAmount": 10000,
    #     "Token": "5cad73340932416d919b2bb57d0d8984",
    # }
    result = Payment.payment_callback(data, ipg_type=Transaction.IPGTypes.SEP)
    code = result.get('code')
    payment_is_succeed = result.get('status') == SUCCESS_STATUS
    if payment_is_succeed:
        return redirect(f'{domain}/cart/payment/success/data?code={code}')
    return redirect(f'{domain}/cart/payment/failure/data?code={code}')
