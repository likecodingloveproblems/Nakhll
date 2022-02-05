import enum
from urllib.parse import urljoin
from django.conf import settings
from django.utils.timezone import localtime
from discord_webhook import DiscordWebhook, DiscordEmbed, webhook
import jdatetime
import requests

class ProductChangeTypes(enum.Enum):
    CREATE = 'create'
    UPDATE = 'update'
        
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
        message = DiscordAlertInterface.build_message(invoice)
        headers = { "Content-Type": "application/json" }
        data = {'content': message,'username': 'Nakhll Market',}
        requests.post(url, json=data, headers=headers)

    @staticmethod
    def build_message(invoice):
        name = invoice.address.receiver_full_name
        phone = invoice.address.receiver_mobile_number
        dt = localtime(invoice.payment_datetime)
        datetime = jdatetime.datetime.fromgregorian(datetime=dt).strftime('%Y/%m/%d %H:%M:%S')
        message = '```'
        message += '-'*53 + '\n'
        message += '|' + (' '*20) + 'ﺥﺮﯾﺩ ﺍﺯ ﻦﺨﻟ' + (' '*20) + '|' + '\n'
        message += '-'*53 + '\n'
        message += 'ﮎﺍﺮﺑﺭ:' + name.rjust(40) + '\n'
        message += 'ﻡﻮﺑﺎﯿﻟ:' + phone.rjust(40) + '\n'
        message += 'ﻑﺎﮑﺗﻭﺭ:' + str(invoice.id).rjust(40) + '\n'
        message += 'ﺕﺍﺮﯿﺧ:' + datetime.rjust(40) + '\n'
        message += 'ﻢﺒﻠﻏ:' + '{:,} ﺮﯾﺎﻟ'.format(invoice.final_price).rjust(40) + '\n'
        message += '-'*53 + '\n'
        message += '```'
        return message

    @staticmethod
    def product_alert(product, *, change_type=ProductChangeTypes.CREATE, without_image=False):
        title = 'یک محصول جدید!' if change_type == ProductChangeTypes.CREATE else 'تغییر در محصول!'
        base_url = settings.DOMAIN_NAME
        product_url = urljoin(base_url, '/shop/{}/product/{}'.format(product.FK_Shop.Slug, product.Slug))
        webhook_url = settings.DISCORD_WEBHOOKS.get('NEW_PRODUCT')
        webhook = DiscordWebhook(url=webhook_url, username='بازار آنلاین نخل')
        embed = DiscordEmbed(title=title, description='در فروشگاه {}'.format(product.FK_Shop.Title), color=0x007700)
        embed.set_author(
            name=product.FK_Shop.FK_ShopManager.get_full_name(),
            url=product_url,
            icon_url=product.FK_Shop.Image_thumbnail_url(),
        )
        embed.add_embed_field(name='نام', value=product.Title, inline=True)
        embed.add_embed_field(name='دسته بندی', value=product.category.name, inline=True)
        embed.add_embed_field(name='قیمت', value='{:,} ریال'.format(product.Price), inline=True)
        embed.add_embed_field(name='قیمت با تخفیف', value='{:,} ریال'.format(product.OldPrice), inline=True)
        embed.add_embed_field(name='وزن خالص', value=product.Net_Weight, inline=True)
        embed.add_embed_field(name='وزن با بسته بندی', value=product.Weight_With_Packing, inline=True)
        embed.add_embed_field(name='موجودی', value=product.Inventory, inline=True)
        embed.add_embed_field(name='زمان آماده سازی', value=product.PreparationDays, inline=True)
        embed.add_embed_field(name='لینک محصول', value=product_url, inline=False)
        embed.add_embed_field(name='توضیحات', value=product.Description, inline=False)
        webhook.add_embed(embed)
        if not without_image:
            try:
                with open(product.Image.path, 'rb') as f:
                    webhook.add_file(file=f.read(), filename=f'{product.Slug}.png')
            except FileNotFoundError as ex:
                pass
        response = webhook.execute()

        

from nakhll_market import models