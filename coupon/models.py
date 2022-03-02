from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import make_aware, now
from django.utils.translation import ugettext_lazy as _
from django.core.serializers.json import DjangoJSONEncoder
from rest_framework.validators import ValidationError
from nakhll_market.models import Shop, Product
from invoice.models import Invoice
from coupon.managers import CouponManager, CouponUsageManager
from coupon.interfaces import CouponValidation



class Coupon(models.Model, CouponValidation):
    ''' Coupon model '''
    class Meta:
        verbose_name = _('کوپن تخفیف')
        verbose_name_plural = _('کوپن‌های تخفیف')
    # class AvailableStatuses(models.TextChoices):
        # AVAILABLE = True, _('فعال')
        # UNAVAILABLE = False, _('غیر فعال')
    code = models.CharField(_('کد تخفیف'), max_length=100, unique=True)
    title = models.CharField(_('عنوان'), max_length=100, null=True, blank=True)
    description = models.TextField(_('توضیحات'), null=True, blank=True )
    amount = models.IntegerField(_('مبلغ تخفیف'), default=0)
    max_amount = models.IntegerField(_('حداکثر تخفیف قابل اعمال'), default=0)
    presentage = models.IntegerField(_('درصد تخفیف'), default=0)
    creator = models.ForeignKey(User, verbose_name=_('سازنده کوپن'), on_delete=models.SET_NULL, null=True, blank=True, related_name='coupon_creator')
    available=models.BooleanField(verbose_name='وضعیت ثبت کوپن', default=True)
    log = models.TextField(_('گزارش'), null=True, blank=True)
    created_at = models.DateTimeField(_('تاریخ ثبت'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ بروزرسانی'), auto_now=True)
    objects = CouponManager()
    # extra_data = models.TextField(_('اطلاعات اضافی'), null=True, blank=True)
    def __str__(self):
        return self.code

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not hasattr(self, 'constraint'):
            CouponConstraint.objects.create(coupon=self)


class CouponConstraint(models.Model):
    class Meta:
        verbose_name = _('محدودیت تخفیف')
        verbose_name_plural = _('محدودیت‌های تخفیف')
    coupon = models.OneToOneField(Coupon, on_delete=models.CASCADE, related_name='constraint', verbose_name=_('کوپن'))
    users = models.ManyToManyField(User, verbose_name=_('کاربران'), related_name='coupons', blank=True)
    shops = models.ManyToManyField(Shop, verbose_name=_('حجره'), related_name='coupons', blank=True)
    products = models.ManyToManyField(Product, verbose_name=_('محصول'), related_name='coupons', blank=True)
    # categories = models.ManyToManyField(Category, verbose_name=_('دسته بندی'), related_name='coupons') TODO
    valid_from = models.DateField(_('تاریخ شروع'), default=now, null=True, blank=True)
    valid_to = models.DateField(_('تاریخ پایان'), null=True, blank=True)
    budget = models.IntegerField(_('بودجه کل کوپن'), default=0)
    max_usage_per_user = models.IntegerField(default=1, verbose_name=_('حداکثر دفعات استفاده کاربر'))
    max_usage = models.IntegerField(default=5, verbose_name=_('حداکثر دفعات استفاده'))
    min_purchase_amount = models.BigIntegerField(_('حداقل مقدار خرید'), null=True, blank=True)
    min_purchase_count = models.IntegerField(_('حداقل تعداد خرید'), null=True, blank=True)
    max_purchase_amount = models.BigIntegerField(_('حداکثر مقدار خرید'), null=True, blank=True)
    max_purchase_count = models.IntegerField(_('حداکثر تعداد خرید'), null=True, blank=True)
    cities = models.ManyToManyField('nakhll_market.City', verbose_name=_('شهرها'), related_name='coupons', blank=True)
    
    extra_data = models.JSONField(_('اطلاعات اضافه'), null=True, blank=True, encoder=DjangoJSONEncoder)


   
class CouponUsage(models.Model):
    ''' Coupon Usage model '''
    class Meta:
        verbose_name = _('استفاده از کوپن تخفیف')
        verbose_name_plural = _('استفاده از کوپن های تخفیف')
    invoice = models.ForeignKey(Invoice, verbose_name=_('سفارش'), related_name='coupon_usages', on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon, verbose_name=_('کوپن تخفیف'), on_delete=models.CASCADE, related_name='usages')
    used_datetime = models.DateTimeField(_('تاریخ استفاده'), default=now)
    price_applied = models.IntegerField(_('تخفیف اعمال شده'), default=0)
    objects = CouponUsageManager
    def __str__(self):
        return f'{self.coupon} - {self.price_applied} - {self.used_datetime}'





