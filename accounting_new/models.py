from uuid import uuid4
from datetime import datetime
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.serializers.json import DjangoJSONEncoder
from nakhll_market.interface import AlertInterface
from payoff.models import Transaction
from payoff.interfaces import PaymentInterface
from cart.models import Cart
from accounting_new.interfaces import AccountingInterface
from logistic.models import Address, PostPriceSetting
from sms.services import Kavenegar

# Create your models here.

class Invoice(models.Model, AccountingInterface):
    class Statuses(models.TextChoices):
        AWAIT_PAYING = 'awaiting_paying', _('در انتظار پرداخت')
        PAYING = 'paying', _('در حال پرداخت')
        AWAIT_SHOP_APPROVAL = 'wait_store_approv', _('در انتظار تأیید فروشگاه')
        PREPATING_PRODUCT = 'preparing_product', _('در حال آماده سازی')
        AWAIT_CUSTOMER_APPROVAL = 'wait_customer_approv', _('در انتظار تأیید مشتری')
        AWAIT_SHOP_CHECKOUT = 'wait_store_checkout', _('در انتظار تسویه با فروشگاه') 
        COMPLETED = 'completed', _('تکمیل شده')
        CANCELED = 'canceled', _('لغو شده')
    class Meta:
        verbose_name = _('فاکتور')
        verbose_name_plural = _('فاکتورها')

    source_module = models.CharField(_('مبدا'), max_length=50, null=True, blank=True,
            help_text=_('نام ماژولی که این فاکتور رو ایجاد کرده است. به عنوان مثال: cart'))
    old_id = models.UUIDField(null=True, blank=True)
    FctorNumber = models.CharField(_('شماره فاکتور'), max_length=50, null=True, blank=True, unique=True)
    status = models.CharField(_('وضعیت فاکتور'), max_length=20, 
            default=Statuses.AWAIT_PAYING, choices=Statuses.choices)
    cart = models.OneToOneField(Cart, on_delete=models.PROTECT, related_name='invoice', 
            verbose_name=_('سبد خرید'))
    address = models.ForeignKey(Address, on_delete=models.PROTECT, null=True,
            blank=True, related_name='invoices', verbose_name=_('آدرس'))
    address_json = models.JSONField(_('آدرس ثبت شده نهایی'), null=True, blank=True, encoder=DjangoJSONEncoder)
    created_datetime = models.DateTimeField(_('تاریخ ایجاد فاکتور'), auto_now_add=True)
    last_payment_request = models.DateTimeField(_('آخرین درخواست پرداخت'), null=True, blank=True)
    payment_unique_id = models.UUIDField(_('شماره درخواست پرداخت'), null=True, blank=True)
    extra_data = models.JSONField(null=True, blank=True, encoder=DjangoJSONEncoder)

    @property
    def user(self):
        return self.cart.user

    @property
    def total_price(self):
        return self.cart.total_price

    @property
    def products(self):
        return self.cart.products

    @property
    def shops(self):
        return self.cart.shops

    @property
    def shop_total_weight(self):
        return self.cart.cart_weight

    @property
    def logistic_price(self):
        post_setting, is_created = PostPriceSetting.objects.get_or_create()
        return post_setting.get_post_price(self)

    @property
    def logistic_errors(self):
        post_setting, is_created = PostPriceSetting.objects.get_or_create()
        return post_setting.get_out_of_range_products(self)

    @property
    def coupons_total_price(self):
        final_price = 0
        usages = self.coupon_usages.all()
        for usage in usages:
            final_price += usage.price_applied
        return final_price

    @property
    def final_price(self):
        ''' Total amount of cart_price + logistic - coupon '''
        cart_total_price = self.cart.total_price
        logistic_price = self.logistic_price
        coupon_price = self.coupon_details.get('result') or 0
        return cart_total_price + logistic_price - coupon_price

    def send_to_payment(self, bank_port=Transaction.IPGTypes.PEC):
        self.status = self.Statuses.PAYING
        self.payment_unique_id = int(datetime.now().timestamp() * 1000000)
        self.last_payment_request = datetime.now()
        self.save()
        PaymentInterface.from_invoice(self, bank_port)

    def complete_payment(self):
        ''' Payment is succeeded '''
        self.cart.archive()
        self.cart.reduce_inventory()
        self.send_notifications()
        self.save_address_as_json()
        self.status = self.Statuses.AWAIT_STORE_APPROVAL
        self.save()

    def save_address_as_json(self):
        ''' Save invoice address as json to prevent address loss in case of editing'''
        address_json = self.address.to_json() 
        self.address_json = address_json
        self.save()

    
    def send_notifications(self):
        ''' Send SMS to user and shop_owner and create alert for staff'''
        shops = self.cart.items.all().values_list('product__FK_Shop', flat=True).distinct()
        for shop in shops:
            Kavenegar.shop_new_order(shop.FK_ShopManager.UserProfile.phone_number, self.id)
        AlertInterface.new_order(self)

    @staticmethod
    def revert_payment(self):
        ''' Payment is failed'''
        self.unset_coupons()
        self.status = self.Statuses.COMPLETING
        self.save()

    def unset_coupons(self):
        ''' Delete all coupon usages from invoice '''
        coupon_usages = self.coupon_usages.all()
        for coupon_usage in coupon_usages:
            coupon_usage.delete()



