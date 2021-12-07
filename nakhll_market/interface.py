import requests
from django.conf import settings

class AlertInterface:
    @staticmethod
    def new_order(invoice):
        ''' Create new alert for invoice '''
        DiscordAlertInterface.purchase_alert(invoice)
        alert = models.Alert()
        alert.FK_User = invoice.user
        alert.Part = '12'
        alert.Slug = invoice.id
        alert.save()
        return alert

    @staticmethod
    def reverse_payment_error(transaction_result, **kwargs):
        ''' Create alert for transaction that is unsucessfull '''
        desc = ', '.join(f'{key}: {value}' for key, value in kwargs.items())
        DiscordAlertInterface.send_alert(desc)
        alert = models.Alert()
        alert.FK_User = None
        alert.Part = models.Alert.AlertParts.PAYMENT_ERROR
        alert.Slug = transaction_result.id
        alert.alert_description = desc
        alert.save()
        return alert
        
    
    @staticmethod
    def payment_not_confirmed(transaction_result, **kwargs):
        ''' Create alert when transaction_result is valid, but ipg doesn't confirm payment'''
        desc = ', '.join(f'{key}: {value}' for key, value in kwargs.items())
        DiscordAlertInterface.send_alert(desc)
        alert = models.Alert()
        alert.FK_User = None
        alert.Part = models.Alert.AlertParts.PAYMENT_ERROR
        alert.Slug = transaction_result.id
        alert.alert_description = desc
        alert.save()
        return alert

    @staticmethod
    def not_enogth_in_stock(product, count):
        desc = 'Not enogth in stock: {} {}'.format(count, product.Title)
        DiscordAlertInterface.send_alert(desc)
        alert = models.Alert()
        alert.FK_User = None
        alert.Part = models.Alert.AlertParts.PAYMENT_ERROR
        alert.Slug = product.Slug
        alert.alert_description = desc
        alert.save()
        return alert
    
    @staticmethod
    def developer_alert(**kwargs):
        ''' send alert to dicord channel '''
        message = '\n'.join(f'{key}:{value}' for key, value in kwargs.items())
        DiscordAlertInterface.send_alert(message)

        
class DiscordAlertInterface:
    @staticmethod
    def send_alert(message=None, **kwargs):
        ''' send alert to dicord channel '''
        url = settings.DISCORD_WEBHOOKS.get('ALERT')
        if not url:
            return
        headers = { "Content-Type": "application/json" }
        if kwargs:
            message += '\n'.join(f'{key}:{value}' for key, value in kwargs.items())
        data = {'content': message, 'username': 'Nakhll Market',}
        requests.post(url, json=data, headers=headers)

    @staticmethod
    def purchase_alert(invoice):
        ''' send alert to dicord channel '''
        url = settings.DISCORD_WEBHOOKS.get('PURCHASE')
        if not url:
            return
        message = f'{invoice.user.username} has purchased {invoice.items.count()} items'
        headers = { "Content-Type": "application/json" }
        data = {'content': message,'username': 'Nakhll Market',}
        requests.post(url, json=data, headers=headers)

        

from nakhll_market import models