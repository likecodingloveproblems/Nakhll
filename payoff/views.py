from uuid import uuid4
from django.shortcuts import render
from payoff.payment import Payment
from payoff.interfaces import PaymentInterface

# Create your views here.

def test_pec(request):
    order_number = str(uuid4())
    data = {
        'amount': 100000,
        'order_nubmer': order_number,
        'description': f'پرداخت فاکتور {order_number}',
        'ipg': 'PEC',
        'mobile': '09384918664',
    }
    payment = Payment()
    payment.initiate_payment(data)
    return payment

