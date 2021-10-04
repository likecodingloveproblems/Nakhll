from django.utils.translation import ugettext as _
from payoff.payment import Payment


class PaymentInterface:
    ''' Interface for converting models to payoff class data '''

    @staticmethod
    def from_invoice(invoice, bank_port):
        ''' Convert invoice to payoff class data '''
        data = {
            'referrer_model': invoice._meta.model.__name__,
            'referrer_app': invoice._meta.app_label,
            'amount': invoice.final_price,
            'order_number': str(invoice.payment_unique_id),
            'description': _('Invoice %s') % invoice.id,
            'ipg': bank_port,
            'mobile': invoice.address.receiver_mobile_number,
        }

        payment = Payment()
        payment.initiate_payment(data)
        return payment
