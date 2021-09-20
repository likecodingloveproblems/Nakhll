from datetime import datetime
from django.contrib.auth.models import User
from django.utils.timezone import make_aware
from django.utils.translation import ugettext_lazy as _
from django.db import models
from rest_framework.validators import ValidationError
from nakhll_market.models import Category, Shop, Product
from accounting_new.models import Invoice
from coupon.managers import CouponManager, CouponUsageManager
from coupon.interfaces import CouponValidation



class Coupon(models.Model, CouponValidation):
    ''' Coupon model '''
    class Meta:
        verbose_name = _('کوپن تخفیف')
        verbose_name_plural = _('کوپن‌های تخفیف')
    class AvailableStatuses(models.TextChoices):
        AVAILABLE = True, _('فعال')
        UNAVAILABLE = False, _('غیر فعال')
    code = models.CharField(_('کد تخفیف'), max_length=100, unique=True)
    title = models.CharField(_('عنوان'), max_length=100, null=True, blank=True)
    description = models.TextField(_('توضیحات'), null=True, blank=True )
    amount = models.IntegerField(_('مبلغ تخفیف'), default=0)
    max_amount = models.IntegerField(_('حداکثر تخفیف قابل اعمال'), default=0)
    presentage = models.IntegerField(_('درصد تخفیف'), default=0)
    creator = models.ForeignKey(User, verbose_name=_('سازنده کوپن'), on_delete=models.SET_NULL, null=True, blank=True, related_name='coupon_creator')
    available=models.BooleanField(verbose_name='وضعیت ثبت کوپن', choices=AvailableStatuses.choices, default=True)
    log = models.TextField(_('گزارش'), null=True, blank=True)
    created_at = models.DateTimeField(_('تاریخ ثبت'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ بروزرسانی'), auto_now=True)
    objects = CouponManager()
    def __str__(self):
        return self.code

class CouponConstraint(models.Model):
    class Meta:
        verbose_name = _('محدودیت تخفیف')
        verbose_name_plural = _('محدودیت‌های تخفیف')
    coupon = models.OneToOneField(Coupon, on_delete=models.CASCADE, related_name='constraint', verbose_name=_('کوپن'))
    users = models.ManyToManyField(User, verbose_name=_('کاربران'), related_name='coupons')
    shops = models.ManyToManyField(Shop, verbose_name=_('حجره'), related_name='coupons')
    products = models.ManyToManyField(Product, verbose_name=_('محصول'), related_name='coupons')
    # categories = models.ManyToManyField(Category, verbose_name=_('دسته بندی'), related_name='coupons')
    valid_from = models.DateField(_('تاریخ شروع'), default=datetime.now, null=True, blank=True)
    valid_to = models.DateField(_('تاریخ پایان'), null=True, blank=True)
    budget = models.IntegerField(_('بودجه کل کوپن'), default=0)
    max_usage_per_user = models.IntegerField(default=1, verbose_name=_('حداکثر دفعات استفاده کاربر'))
    max_usage = models.IntegerField(default=5, verbose_name=_('حداکثر دفعات استفاده'))
    min_purchase_amount = models.IntegerField(_('حداقل مقدار خرید'), null=True, blank=True)
    min_purchase_count = models.IntegerField(_('حداقل تعداد خرید'), null=True, blank=True)
    max_purchase_amount = models.IntegerField(_('حداکثر مقدار خرید'), null=True, blank=True)
    max_purchase_count = models.IntegerField(_('حداکثر تعداد خرید'), null=True, blank=True)


   
class CouponUsage(models.Model):
    ''' Coupon Usage model '''
    class Meta:
        verbose_name = _('استفاده از کوپن تخفیف')
        verbose_name_plural = _('استفاده از کوپن های تخفیف')
    invoice = models.ForeignKey(Invoice, verbose_name=_('سفارش'), related_name='coupon_usages', on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon, verbose_name=_('کوپن تخفیف'), on_delete=models.CASCADE, related_name='usages')
    used_datetime = models.DateTimeField(_('تاریخ استفاده'), default=datetime.now)
    price_applied = models.IntegerField(_('تخفیف اعمال شده'), default=0)
    objects = CouponUsageManager
    def __str__(self):
        return f'{self.coupon} - {self.amount} - {self.used_datetime}'





