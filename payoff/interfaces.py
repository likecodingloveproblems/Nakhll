"""Interface for all django apps to connect to an Internet Payment Gateway."""
from django.utils.translation import ugettext as _
from .models import Transaction
from payoff.sep_payment import SepPaymentMethod
from payoff.pec_payment import PecPaymentMethod


class Payment:
    """Interface for all django apps to connect to an Internet Payment Gateway using a payment method.

    This class is just an intermidiate class which connects PaymentInterface to selected payment class.
    TODO: it's better to merge this class with PaymentInterface class due to the small amount of operations
    that it performs.
    """
    @staticmethod
    def initiate_payment(data):
        """This is the start of the payment process.

        This method is responsible for generating a payment url and redirecting the user to that url.

        Args:
            data (dict): Data to create a :attr:`Transaction` object. All necessary data for creating a 
            transaction should be included in this dict.

        Returns:
            :attr:`response.Response`: Response object with the url of IPG. for example:
            Response({'url': 'https://www.example_ipg.com/token/12345'})
        """
        ipg_type = data.get('ipg')
        ipg_class = Payment._get_ipg_class(ipg_type)
        ipg = ipg_class()
        return ipg.initiate_payment(data)

    @staticmethod
    def payment_callback(data, ipg_type):
        """The process of receiving the payment result from the IPG.

        Args:
            data (dict): All data that IPG sent to our server.
            ipg_type (Transaction.IPGTypes): The type of IPG that sent the data.
                we choose our IPG class to handle the data based on this type.

        Returns:
            dict: the result of the payment. This dict has the following keys:
                - 'status': can be either :attr:`payoff.base_payment.SUCCESS_STATUS` or
                    :attr:`payoff.base_payment.FAILURE_STATUS` which indicates the status of the payment.
                - 'code': a code for user to identify and track the payment (mostly for failure payments).
        """
        ipg_class = Payment._get_ipg_class(ipg_type)
        ipg = ipg_class()
        result = ipg.callback(data)
        return result

    @staticmethod
    def _get_ipg_class(ipg_type):
        """Return the class of the IPG that is responsible for handling the data based on ipg_type."""
        if ipg_type == Transaction.IPGTypes.PEC:
            return PecPaymentMethod
        if ipg_type == Transaction.IPGTypes.SEP:
            return SepPaymentMethod


class PaymentInterface:
    """Interface for converting other classes and models to payoff class data

    Instead of directly using the payoff class, we use this interface to convert other classes and models to payoff class data.
    """

    @staticmethod
    def from_invoice(invoice, bank_port):
        """Convert :attr:`invoice.models.Invoice` to payoff class data"""
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
        """Convert :attr:`shop.models.ShopFeatureInvoice` to payoff class data"""
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
