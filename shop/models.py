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
    """Features that a shop can get (free or paid) for his/her shops

    'Custom Landing Page' and 'Adding or Editing Product features in Bulk Operation' are two example of shop features
    which shop owners doesn't have by default. These features are usually time-limited and shop owners should
    extend featuers their time are finished.

    Each record in this table should have it's own implementation to handle the feature. This means adding a new
    record to this table without a module or class or function to handle the feature will not work. So the reason
    that this table exists is because we want to allow admin and staffs to change its details like name, price and
    description.

    Attributes:
        name: Name of the feature
        feature_permission_code_name: we use this code to check if a user has permission to use this feature or not.
        description = HTML description of the feature that can use as a marketing landing page, help page, etc.
        unit = time unit of this feature.
        price_per_unit_without_discount = price of this feature per unit without discount.
        price_per_unit_with_discount = price of this feature per unit with discount.
        demo_days = indicates how many days this feature is available for demo.
        is_publish = indicates if this feature is published or not.

    """
    class Meta:
        verbose_name = _('ویژگی فروشگاه')
        verbose_name_plural = _('ویژگی فروشگاه')

    class Units(models.TextChoices):
        """Available units for now are:
            * week: for one week
            * month: for one month
            * year: for one year
            * one_time: for one time
        """
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
        """This function check if this feature is previously enabled for this shop or not."""
        prev_demo = self.shop_feature_invoices.filter(
            is_demo=True, shop=shop).first()
        return bool(prev_demo)

    @staticmethod
    def has_shop_landing_access(shop):
        """Check if this shop has access to shop landing page or not.

        For a shop to have access to shop landing page, it should has a record in 
        :attr:`shop.models.ShopFeatureInvoice` table with these conditions:
            * :attr:`status` must be completed
            * :attr:`start_datetime` must be less than or equal to current time
            * :attr:`expite_datetime` must be greater than or equal to current time
        """
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
        """Check if this shop has active landing page or not."""
        return bool(shop.landings.filter(status=ShopLanding.Statuses.ACTIVE).first())


class ShopFeatureInvoice(models.Model):
    """Invoices for shop which want to use a feature

    After a shop owner request for a feature, an invoice will assign to her/his shop which shop owner must change its 
    :attr:`status` to completed. This operation does not necessarily happen with payment, but it can be a demo request.
    After changing the status to completed, the shop owner can use the feature until the expire date.

    Attributes:
        feature = :class:`ShopFeature` that this invoice is for.
        shop = :class:`nakhll_market.models.Shop` that this invoice is for.
        status = :class:`ShopFeatureInvoiceStatuses` that this invoice is in.
        bought_price_per_unit = price of this invoice per unit.
        bought_unit = unit of this invoice.
        unit_count = number of units of this invoice.
        start_datetime = start date of this invoice.
        expire_datetime = expire date of this invoice.
        payment_datetime = date of payment of this invoice.
        payment_unique_id = unique id of payment of this invoice which will use in payment system.
        is_demo = indicates if this invoice is a demo or not.
    """
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
        """Operations that should be done after payment is completed.

        These operations include:
            * change status to completed
            * set payment datetime
            * set start and expire datetime
        """
        self.status = self.ShopFeatureInvoiceStatuses.COMPLETED
        self.payment_datetime = timezone.now()
        self.save_start_datetime()
        self.save_expire_datetime()
        self.save()

    def revert_payment(self):
        """Operations which should be done when payment is failed."""

    def save_start_datetime(self):
        """Set start datetime of invoice.

        Start datetime is not necessarily equal to now. It will start after the expire date of previous invoice.
        This function find the last invoice of this shop and set start datetime to expire date of that invoice.
        """
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
        """Set expire datetime of invoice.

        Expire datetime of invoice is calculated by start datetime and unit count.
        """
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
    """Landing pages of shops.

    Each shop can have landing pages which are used to show on shop's first page. Only one landing page can be used
    at a time. Each landing page has HTML data to parse in its landing page.
    This is a shop feature object. for more information about a shop feature, read :class:`ShopFeature`.

    Attributes:
        * shop: shop of this landing page.
        * name: name of this landing page.
        * status: status of this landing page which can be active or inactive. Active landing page will be shown
            on shop's first page.
        * page_data: HTML data of this landing page.
        * created_at: date of creation of this landing page.
        * updated_at: date of last update of this landing page.

    """
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
    status = models.CharField(max_length=10, choices=Statuses.choices,
                              default=Statuses.INACTIVE, verbose_name=_('وضعیت'))
    page_data = models.TextField(verbose_name=_('داده‌های صفحه'), null=True, blank=True)
    objects = ShopLandingManager()

    def __str__(self):
        return f'{self.shop} - {self.name}'


class PinnedURL(models.Model):
    """URLs that a user (not shop owner) marked as pinned urls.

    These urls will be shown to user to choose from in different pages.

    Attributes:
        * user: user of this pinned url.
        * name: name of this pinned url.
        * link: url of this pinned url.
        * created_at: date of creation of this landing page.
        * updated_at: date of last update of this landing page.
    """
    class Meta:
        verbose_name = _('لینک پین شده')
        verbose_name_plural = _('لینک پین شده')

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pinned_urls', verbose_name=_('کاربر'))
    name = models.CharField(max_length=100, verbose_name=_('نام'))
    link = models.URLField(verbose_name=_('لینک'), max_length=500)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاریخ ایجاد'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاریخ بروزرسانی'))


class ShopAdvertisement(models.Model):
    """Advertisement details of each shop.

    Different advertisement systems gives some data to shop owners to add to their website. We can use this data to
    add to shop owner's landing page.

    Attributes:
        * shop: shop of this advertisement.
        * yektanet_id: id of this advertisement in yektanet.
        * yektanet_status: this advertisement on yektanet can set as active or inactive in any time.
    """
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
