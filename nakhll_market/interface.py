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
        # DEBUG:
        send_sms('unconfirmed_transaction', f'transaction_result_id:{transaction_result.id}', '09384918664')