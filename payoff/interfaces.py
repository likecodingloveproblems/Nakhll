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
        return payment.initiate_payment(data)

    @staticmethod
    def from_shop_feature(shop_feature_invioce, bank_port):
        ''' Convert invoice to payoff class data '''
        data = {
            'referrer_model': shop_feature_invioce._meta.model.__name__,
            'referrer_app': shop_feature_invioce._meta.app_label,
            'amount': shop_feature_invioce.final_price,
            'order_number': str(shop_feature_invioce.payment_unique_id),
            'description': _('Shop Feature Invoice %s') % shop_feature_invioce.id,
            'ipg': bank_port,
            'mobile': shop_feature_invioce.shop.FK_ShopManager.User_Profile.MobileNumber,
        }
        payment = Payment()
        return payment.initiate_payment(data)

