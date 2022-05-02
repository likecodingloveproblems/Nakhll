from datetime import datetime, timedelta
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from nakhll_market.models import Shop
from payoff.interfaces import PaymentInterface
from payoff.models import Transaction
from .managers import ShopFeatureManager, ShopLandingManager

# Create your models here.

class ShopFeature(models.Model):
    class Meta:
        verbose_name = _('ویژگی فروشگاه')
        verbose_name_plural = _('ویژگی فروشگاه')
    class Units(models.TextChoices):
        ONE_TIME = '1time', _('یک بار') 
        PER_WEEK = 'week', _('هفته')
        PER_MONTH = 'month', _('ماه')
        PER_YEAR = 'year', _('سال')
    class PermissionCodeNames(models.TextChoices):
        LANDING = 'landing', _('صفحه اصلی')
        BULK_OPERATION = 'bulk_operation', _('عملیات دسته جمعی')


    name = models.CharField(max_length=100)
    feature_permission_code_name = models.CharField(
        max_length=15,
        choices=PermissionCodeNames.choices,
        verbose_name=_('نام کد دسترسی')
    )
    description = models.TextField()
    unit = models.CharField(
        max_length=5,
        choices=Units.choices,
        default=Units.ONE_TIME,
    )
    price_per_unit_without_discount = models.DecimalField(max_digits=12, decimal_places=0)
    price_per_unit_with_discount = models.DecimalField(max_digits=12, decimal_places=0)
    demo_days = models.IntegerField(default=0)
    is_publish = models.BooleanField(_('منتشر شده؟'), default=True)
    objects = ShopFeatureManager()

    def __str__(self):
        return self.name

    def is_enabled_before(self, shop):
        prev_demo = self.shop_feature_invoices.filter(
            is_demo=True, shop=shop).first()
        return bool(prev_demo)
    
    @staticmethod
    def has_shop_landing_access(shop):
        permission = ShopFeature.PermissionCodeNames.LANDING
        now = timezone.now()
        return bool(shop.invoice_shop_feature_items.filter(
            feature__feature_permission_code_name=permission,
            start_datetime__lte=now,
            expire_datetime__gte=now,
            status=ShopFeatureInvoice.ShopFeatureInvoiceStatuses.COMPLETED
        ).first())

    @staticmethod
    def has_active_landing_page(shop):
        return bool(shop.landings.filter(status=ShopLanding.Statuses.ACTIVE).first())
        
        


class ShopFeatureInvoice(models.Model):
    class Meta:
        verbose_name = _('فاکتور ویژگی فروشگاه')
        verbose_name_plural = _('فاکتورهای ویژگی فروشگاه')
    class ShopFeatureInvoiceStatuses(models.TextChoices):
        AWAIT_PAYMENT = 'awaiting_paying', _('در انتظار پرداخت')
        COMPLETED = 'completed', _('تکمیل شده')
        CANCELED = 'canceled', _('لغو شده')
    
    feature = models.ForeignKey(ShopFeature, on_delete=models.CASCADE, related_name='shop_feature_invoices',
                        verbose_name=_('ویژگی فروشگاه'))
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='invoice_shop_feature_items',
                        verbose_name=_('فروشگاه'))
    status = models.CharField(_('وضعیت'), max_length=15, choices=ShopFeatureInvoiceStatuses.choices,
                        default=ShopFeatureInvoiceStatuses.AWAIT_PAYMENT)
    bought_price_per_unit = models.DecimalField(_('قیمت خرید'), max_digits=12, decimal_places=0)
    bought_unit = models.CharField(_('واحد خرید'), max_length=20)
    unit_count = models.IntegerField(_('تعداد'), default=1)
    start_datetime = models.DateTimeField(_('تاریخ شروع'), null=True, blank=True)
    expire_datetime = models.DateTimeField(_('تاریخ انقضا'), null=True, blank=True)
    payment_datetime = models.DateTimeField(_('تاریخ خرید'), auto_now_add=True, null=True, blank=True)
    payment_unique_id = models.BigIntegerField(_('شماره درخواست پرداخت'), null=True, blank=True)
    is_demo = models.BooleanField(_('دمو'), default=False)

    @property
    def final_price(self):
        if self.is_demo:
            return 0
        else:
            return self.bought_price_per_unit * self.unit_count

    def send_to_payment(self, bank_port=Transaction.IPGTypes.PEC):
        self.payment_unique_id = int(timezone.now().timestamp() * 1000000)
        self.save()
        return PaymentInterface.from_shop_feature(self, bank_port)

    def complete_payment(self):
        ''' Payment is succeeded '''
        self.status = self.ShopFeatureInvoiceStatuses.COMPLETED
        self.payment_datetime = timezone.now()
        self.save_start_datetime()
        self.save_expire_datetime()
        self.save()

    def revert_payment(self):
        ''' Payment is failed'''
        pass

    def save_start_datetime(self):
        ''' Get last active feature invoice, set new invoice start_datetime right after
            previous expire_datetime
        '''
        start_datetime = None
        last_invoice = ShopFeatureInvoice.objects.filter(
            shop=self.shop,
            feature=self.feature,
            status=self.ShopFeatureInvoiceStatuses.COMPLETED
        ).order_by('-expire_datetime').first()
        if last_invoice:
            start_datetime = last_invoice.expire_datetime
        else:
            start_datetime = timezone.now()
        self.start_datetime = start_datetime

    def save_expire_datetime(self):
        start_datetime = self.start_datetime
        if self.feature.unit == ShopFeature.Units.PER_WEEK:
            expire_datetime = start_datetime + timedelta(7 * self.unit_count)
        elif self.feature.unit == ShopFeature.Units.PER_MONTH:
            expire_datetime = start_datetime + timedelta(31 * self.unit_count)
        elif self.feature.unit == ShopFeature.Units.PER_YEAR:
            expire_datetime = start_datetime + timedelta(365 * self.unit_count)
        else:
            expire_datetime = None
        self.expire_datetime = expire_datetime
        self.save()
        
        
        
class ShopLanding(models.Model):
    class Meta:
        verbose_name = _('صفحه فرود فروشگاه')
        verbose_name_plural = _('صفحات فرود فروشگاه')
    class Statuses(models.TextChoices):
        ACTIVE = 'active', _('فعال')
        INACTIVE = 'inactive', _('غیرفعال')
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='landings', verbose_name=_('حجره'))
    name = models.CharField(max_length=100, verbose_name=_('نام'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاریخ ایجاد'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاریخ بروزرسانی'))
    status = models.CharField(max_length=10, choices=Statuses.choices, default=Statuses.INACTIVE, verbose_name=_('وضعیت'))
    page_data = models.TextField(verbose_name=_('داده‌های صفحه'), null=True, blank=True)
    objects = ShopLandingManager()

    def __str__(self):
        return f'{self.shop} - {self.name}'

class PinnedURL(models.Model):
    class Meta:
        verbose_name = _('لینک پین شده')
        verbose_name_plural = _('لینک پین شده')

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pinned_urls', verbose_name=_('کاربر'))
    name = models.CharField(max_length=100, verbose_name=_('نام'))
    link = models.URLField(verbose_name=_('لینک'), max_length=500)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاریخ ایجاد'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاریخ بروزرسانی'))

    
    
class ShopAdvertisement(models.Model):
    class Meta:
        verbose_name = _('تبلیغات')
        verbose_name_plural = _('تبلیغات')
        ordering = ('-id', )

    class YektanetStatuses(models.IntegerChoices):
        ACTIVE = 1, _('فعال')
        INACTIVE = 0, _('غیرفعال')

    shop = models.OneToOneField(Shop, on_delete=models.CASCADE, related_name='advertisement', verbose_name=_('حجره'))
    yektanet_id = models.CharField(verbose_name=_('شناسه تبلیغاتی یکتانت'), max_length=20, null=True, blank=True)
    yektanet_status = models.IntegerField(verbose_name=_('وضعیت تبلیغاتی یکتانت'),
                                          choices=YektanetStatuses.choices,
                                          default=YektanetStatuses.INACTIVE)