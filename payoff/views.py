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
    # raise Exception('Invalid origin or referer')
    # data = {
    #     "MID": "0",
    #     "TerminalId": "21457185",
    #     "RefNum": "GmshtyjwKStjkzkZOSyuW18tgJM4KVvrYJZv5mL9Wi",
    #     "ResNum": "1658512602386104",
    #     "State": "OK",
    #     "TraceNo": "101979",
    #     "Amount": "67900",
    #     "AffectiveAmount": "67900",
    #     "Wage": "",
    #     "Rrn": "20467145294",
    #     "SecurePan": "621986******5525",
    #     "Status": "2",
    #     "Token": "335242a94b64474ab60cd8ee8974e2fc",
    #     "HashedCardNumber": "082169094A395EAE49DDACBFDE27396FB503821DAA5A93ACF49FE2E958F146FE",
    # }
    result = Payment.payment_callback(data, ipg_type=Transaction.IPGTypes.SEP)
    code = result.get('code')
    payment_is_succeed = result.get('status') == SUCCESS_STATUS
    if payment_is_succeed:
        return redirect(f'{domain}/cart/payment/success/data?code={code}')
    return redirect(f'{domain}/cart/payment/failure/data?code={code}')
