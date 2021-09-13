from uuid import uuid1
from django.shortcuts import render
from payoff.payment import Payment
from payoff.interfaces import PaymentInterface

# Create your views here.

def test_pec(request):
    amount = request.GET.get('amount', '10000')
    mobile = request.GET.get('mobile', '09384918664')
    order_number = int(str(uuid1().int>>64)[2:18])
    data = {
        'amount': int(amount),
        'order_number': order_number,
        'description': f'پرداخت فاکتور {order_number}',
        'ipg': 'pec',
        'mobile': mobile,
    }
    payment = Payment(data)
    return payment.initiate_payment()

