from django.utils.translation import ugettext as _
from payoff.payment import Payment


class PaymentInterface:
    ''' Interface for converting models to payoff class data '''

    @staticmethod
    def from_invoice(invoice, bank_port):
        ''' Convert invoice to payoff class data '''
        data = {
            'amount': invoice.final_price,
            'order_nubmer': str(invoice.payment_unique_id),
            'description': _('پرداخت فاکتور %s') % invoice.id,
            'ipg': bank_port,
            'mobile': invoice.address.receiver_mobile_number,
        }

        payment = Payment()
        payment.initiate_payment(data)
        return payment
