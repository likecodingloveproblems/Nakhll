from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from nakhll_market.models import Product
from cart.models import Cart
from logistic.models import Address, PostPriceSetting
from coupon.models import Coupon
from accounting_new.interfaces import AccountingInterface
from accounting_new.managers import AccountingManager

# Create your models here.

class Invoice(models.Model, AccountingInterface):
    class Statuses(models.TextChoices):
        COMPLETING = 'completing', _('در حال تکمیل')
        PAYING = 'paying', _('در حال پرداخت')
        FAILURE = 'failure', _('پرداخت ناموفق')
        SUCCESS = 'success', _('پرداخت موفق')
    class Meta:
        verbose_name = _('فاکتور')
        verbose_name_plural = _('فاکتورها')

    source_module = models.CharField(_('مبدا'), max_length=50, null=True, blank=True,
            help_text=_('نام ماژولی که این فاکتور رو ایجاد کرده است. به عنوان مثال: cart'))
    status = models.CharField(_('وضعیت فاکتور'), max_length=10, 
            default=Statuses.COMPLETING, choices=Statuses.choices)
    cart = models.ForeignKey(Cart, on_delete=models.PROTECT, related_name='factors', 
            verbose_name=_('سبد خرید'))
    address = models.ForeignKey(Address, on_delete=models.PROTECT, null=True,
            blank=True, related_name='invoices', verbose_name=_('آدرس'))
    coupon = models.ForeignKey(Coupon, on_delete=models.PROTECT, null=True,
            blank=True, related_name='invoices', verbose_name=_('کوپن'))
    created_datetime = models.DateTimeField(_('تاریخ ایجاد فاکتور'), auto_now_add=True)
    last_payment_request = models.DateTimeField(_('آخرین درخواست پرداخت'), null=True, blank=True)

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
    def coupon_details(self):
        coupon = self.coupon
        if coupon:
            coupon(self.cart.user, self)
            coupon.is_valid()
            return {'result': coupon.final_price, 'errors': coupon.errors}
        return {}





