from datetime import datetime
from django.contrib.auth.models import User
from django.utils.timezone import make_aware
from django.utils.translation import ugettext_lazy as _
from django.db import models
from rest_framework.validators import ValidationError
from nakhll_market.models import Category, Shop, Product
from coupon.managers import CouponManager, CouponUsageManager
from coupon.interfaces import CouponValidation



class Coupon(models.Model, CouponValidation):
    ''' Coupon model '''
    class Meta:
        verbose_name = _('کوپن تخفیف')
        verbose_name_plural = _('کوپن‌های تخفیف')
    AVAILABLE_STATUS =(
        (True,'فعال'),
        (False,'غیر فعال'),
    )
    code = models.CharField(_('کد تخفیف'), max_length=100, unique=True)
    valid_from = models.DateField(_('تاریخ شروع'), default=datetime.now, null=True, blank=True)
    valid_to = models.DateField(_('تاریخ پایان'), null=True, blank=True)
    user_max_count = models.IntegerField(default=1, verbose_name=_('دفعات استفاده کاربر'))
    total_max_count = models.IntegerField(default=5, verbose_name=_('دفعات استفاده'))
    price = models.IntegerField(_('مبلغ تخفیف'), default=0)
    discount_percent = models.IntegerField(_('درصد تخفیف'), default=0)
    min_price = models.IntegerField(_('حداقل خرید'), null=True, blank=True)
    max_price = models.IntegerField(_('حداکثر خرید'), null=True, blank=True)
    users = models.ManyToManyField(User, verbose_name=_('کاربران'), related_name='coupons')
    shops = models.ManyToManyField(Shop, verbose_name=_('حجره'), related_name='coupons')
    products = models.ManyToManyField(Product, verbose_name=_('محصول'), related_name='coupons')
    categories = models.ManyToManyField(Category, verbose_name=_('دسته بندی'), related_name='coupons')
    description = models.TextField(_('توضیحات'), null=True, blank=True )
    title = models.CharField(_('عنوان'), max_length=100, null=True, blank=True)
    creator = models.ForeignKey(User, verbose_name=_('سازنده کوپن'), on_delete=models.SET_NULL, null=True, blank=True, related_name='coupon_creator')
    available=models.BooleanField(verbose_name='وضعیت ثبت کوپن', choices=AVAILABLE_STATUS, default=True)
    log = models.TextField(_('گزارش'), null=True, blank=True)
    objects = CouponManager()

    def __str__(self):
        return self.code
   
class CouponUsage(models.Model):
    ''' Coupon Usage model '''
    class Meta:
        verbose_name = _('استفاده از کوپن تخفیف')
        verbose_name_plural = _('استفاده از کوپن های تخفیف')
    coupon = models.ForeignKey(Coupon, verbose_name=_('کوپن تخفیف'), on_delete=models.CASCADE, related_name='usages')
    user = models.ForeignKey(User, verbose_name=_('کاربر'), related_name='coupon_usages', on_delete=models.CASCADE)
    used_date = models.DateTimeField(_('تاریخ استفاده'), default=datetime.now)
    price_applied = models.IntegerField(_('تخفیف اعمال شده'), default=0)
    # order = models.ForeignKey('accounting.Order', verbose_name=_('سفارش'), 
                            #    related_name='coupon_usages', on_delete=models.CASCADE)
    objects = CouponUsageManager
    def __str__(self):
        return f'{self.user} - {self.coupon}'





