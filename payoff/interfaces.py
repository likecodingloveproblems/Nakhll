from django.utils.translation import ugettext as _
from .models import Transaction
from payoff.sep_payment import SepPaymentMethod
from payoff.pec_payment import PecPaymentMethod


class Payment:
    @staticmethod
    def initiate_payment(data):
        ipg_type = data.get('ipg')
        ipg_class = Payment._get_ipg_class(ipg_type)
        ipg = ipg_class()
        return ipg.initiate_payment(data)

    @staticmethod
    def payment_callback(data, ipg_type):
        ipg_class = Payment._get_ipg_class(ipg_type)
        ipg = ipg_class()
        result = ipg.callback(data)
        return result

    @staticmethod
    def _get_ipg_class(ipg_type):
        if ipg_type == Transaction.IPGTypes.PEC:
            return PecPaymentMethod
        if ipg_type == Transaction.IPGTypes.SEP:
            return SepPaymentMethod


class PaymentInterface:
    ''' Interface for converting models to payoff class data '''

    @staticmethod
    def from_invoice(invoice, bank_port):
        ''' Convert invoice to payoff class data '''
        data = {
            'referrer_model': invoice._meta.model.__name__,
            'referrer_app': invoice._meta.app_label,
            'amount': int(invoice.final_price),
            'order_number': str(invoice.payment_unique_id),
            'description': _('Invoice %s') % invoice.id,
            'ipg': bank_port,
            'mobile': invoice.user.username,
        }

        payment = Payment()
        return payment.initiate_payment(data)

    @staticmethod
    def from_shop_feature(shop_feature_invioce, bank_port):
        ''' Convert invoice to payoff class data '''
        id = shop_feature_invioce.id
        mobile = (
            shop_feature_invioce.shop.FK_ShopManager.User_Profile.MobileNumber
        )
        data = {
            'referrer_model': shop_feature_invioce._meta.model.__name__,
            'referrer_app': shop_feature_invioce._meta.app_label,
            'amount': shop_feature_invioce.final_price,
            'order_number': str(
                shop_feature_invioce.payment_unique_id),
            'description': _('Shop Feature Invoice %s') % id,
            'ipg': bank_port,
            'mobile': mobile,
        }
        payment = Payment()
        return payment.initiate_payment(data)
