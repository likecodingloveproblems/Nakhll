from nakhll_market.models import Alert
from sms.services import send_sms

class AlertInterface:
    @staticmethod
    def new_order(invoice):
        ''' Create new alert for invoice '''
        alert = Alert()
        alert.FK_User = invoice.user
        alert.Part = '12'
        alert.Slug = invoice.id
        alert.save()
        return alert

    @staticmethod
    def no_reverse_request(transaction_result):
        ''' Create alert for transaction that is unsucessfull '''
        # TODO: no part is available for this type of alert
    
    @staticmethod
    def payment_not_confirmed(transaction_result):
        ''' Create alert when transaction_result is valid, but ipg doesn't confirm payment'''
        # TODO: no part is available for this type of alert

    
    @staticmethod
    def developer_alert(**kwargs):
        ''' send sms to developer '''
        kwargs_string = '__'.join(f'{key}:{value}' for key, value in kwargs.items())
        send_sms('developer_alert', kwargs_string, '09384918664')