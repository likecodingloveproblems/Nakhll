import logging
import requests
from nakhll.settings import KAVENEGAR_KEY
from sms.models import SMS, SMSRequest
logger = logging.getLogger(__name__)


# only for test purposes
def count_sms():
    return SMS.objects.all().count()


def create_sms(**kwargs):
    SMS.objects.create(**kwargs)


def send_sms(Title, Description, PhoneNumber):
    # Change Text
    des_list = Description.split(' ')
    final_des = ''
    count = 0
    for item in des_list:
        if (count + 1) == len(des_list):
            final_des += item
            count += 1
        else:
            final_des += item + '-'
            count += 1

    url = 'https://api.kavenegar.com/v1/{}/verify/lookup.json'.format(KAVENEGAR_KEY)
    params = {'receptor': PhoneNumber, 'token': Title, 'token2': final_des, 'template': 'nakhll-alert'}
    requests.post(url, params=params)


class Kavenegar:
    """Interface for interacting with Kavenegar SMS API

    There is a function for each need in our project to send SMS. Also there is a private low level function to send
    direct SMS using Kavenegar API.
    """
    @staticmethod
    def _raw_send(template, receptor, tokens):
        """Low level function to send SMS using Kavenegar API.

        Args:
            template: The template name of the SMS which should be sumbitted and verified in Kavenegar website.
                These templates contains up to 3 tokens which will replace the tokens in the template.
            receptor: The phone number of the receptor of the SMS.
            tokens: The dictionary of tokens which should be replaced in the template. For example:
                {'token': '12345', 'token2': '67890'}
        """
        url = 'https://api.kavenegar.com/v1/{}/verify/lookup.json'.format(KAVENEGAR_KEY)
        params = {'receptor': receptor, 'template': template, **tokens}
        requests.post(url, params=params)

    @staticmethod
    def alert(receptor, title, description):
        """Not using anymore."""
        tokens = {
            'token': title,
            'token2': description,
        }
        Kavenegar._raw_send('nakhll-alert', receptor, tokens)

    @staticmethod
    def shop_new_order(receptor, order_id):
        """Send order_id to shop owner who has new order."""
        logger.debug('Sending new order SMS to {} for order {}'.format(receptor, order_id))
        tokens = {'token': order_id}
        Kavenegar._raw_send('nakhll-order', receptor, tokens)

    @staticmethod
    def send_auth_code(mobile_number, code):
        """Send auth code to user who wants to perform any auth request."""
        logger.debug('Sending auth code {} to {}'.format(code, mobile_number))
        tokens = {'token': code}
        Kavenegar._raw_send('nakhl-register', mobile_number, tokens)

    @staticmethod
    def invoice_has_been_sent(invoice):
        """Send invoice number and shipping tracking codes to buyer when invoice has been sent."""
        tokens = {
            'token': invoice.id,
            'token2': '-'.join(invoice.barcodes),
        }
        template = 'nakhll-sendpostcode'
        mobile = invoice.user.username
        Kavenegar._raw_send(template, mobile, tokens)

    @staticmethod
    def send_gift_coupon(user, coupon):
        tokens = {
            'token': coupon.code
        }
        mobile = user.username
        template = 'nakhl-sendgiftcoupon'
        Kavenegar._raw_send(template, mobile, tokens)
