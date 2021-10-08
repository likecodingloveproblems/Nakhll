from nakhll_market.models import Alert

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