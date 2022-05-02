from django.db import models
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from django.core.serializers.json import DjangoJSONEncoder
from nakhll_market.models import Shop, Product
from invoice.models import Invoice
from coupon.managers import CouponManager, CouponUsageManager
from coupon.interfaces import CouponValidation


User = get_user_model()


class Coupon(models.Model, CouponValidation):
    """Coupon model

    This model derived from :attr:`coupon.interfaces.CouponValidation`, which
    contains all coupon validation logic and methods. for example:
    .. :code:

        coupon = Coupon.objects.last()
        coupon.is_valid()

    Attributes:
        code: Coupon code which is unique.
        title: Coupon title which is shown in admin panel and in frontend.
        description: Coupon description which is shown to staff members
        amount: Coupon amount to deduct from invoice. This attribute can be
            zero, which means that coupon is a percentage.
        max_amount: Maximum amount to deduct from invoice. This attribute only
            works with coupon percentage. When calculating coupon amount with
            percentage, final amount will be less than or equal to this value.
        presentage: Coupon percentage to deduct from invoice. This attribute
            only applied if :attr:`amount` is zero. otherwise it will be
            ignored. This value must be between 0 and 100.
        creator (User): User who created this coupon.
        available: Coupon availability. If this attribute is set to False,
            coupon will not be available for usage.
        created_at: DateTime when coupon was created.
        updated_at: DateTime when coupon was updated.
        constraint: Coupon constraint object which contains all validation
            constraint for this coupon.
    """
    class Meta:
        verbose_name = _('کوپن تخفیف')
        verbose_name_plural = _('کوپن‌های تخفیف')
    code = models.CharField(_('کد تخفیف'), max_length=100, unique=True)
    title = models.CharField(_('عنوان'), max_length=100, null=True, blank=True)
    description = models.TextField(_('توضیحات'), null=True, blank=True)
    amount = models.IntegerField(_('مبلغ تخفیف'), default=0)
    max_amount = models.IntegerField(_('حداکثر تخفیف قابل اعمال'), default=0)
    presentage = models.IntegerField(_('درصد تخفیف'), default=0)
    creator = models.ForeignKey(
        User, verbose_name=_('سازنده کوپن'),
        on_delete=models.SET_NULL, null=True, blank=True,
        related_name='coupon_creator')
    available = models.BooleanField(verbose_name='وضعیت ثبت کوپن',
                                    default=True)
    log = models.TextField(_('گزارش'), null=True, blank=True)
    created_at = models.DateTimeField(_('تاریخ ثبت'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ بروزرسانی'), auto_now=True)
    objects = CouponManager()

    def __str__(self):
        return self.code

    def save(self, *args, **kwargs):
        """Make sure that each coupon has it's own constraint object.

        Coupons without constraint object will cause AttributeError in coupon
        validation process, as we need to access coupon constraint frequently.
        """
        super().save(*args, **kwargs)
        if not hasattr(self, 'constraint'):
            CouponConstraint.objects.create(coupon=self)


class CouponConstraint(models.Model):
    """Coupon constraint model, which has one to one relationship with
        :attr:`coupon.models.Coupon` model. Means that each coupon has only
        one constraint object.

    Attributes:
        coupon (Coupon): Coupon object which this constraint belongs to.
        shops (Shop): List of shops which this coupon is available for.
            None means all shops are available.
        users (User): List of users which this coupon is available for.
            None means all users are available.
        products (Product): List of products which this coupon is available
            for. None means all products are available.
        cities (nakhll_market.models.City): List of citys which this coupon is
            available for. None means all cities are available.
        valid_from: DateTime when this coupon is available for usage.
            None means this coupon is available from now.
        valid_to: DateTime when this coupon is not available for usage.
            None means this coupon has no expiration date.
        min_purchase_price: Minimum cart total price to use this coupon.
            None means this coupon can be used for any price of cart.
        max_purchase_price: Maximum cart total price to use this coupon.
            None means this coupon can be used for any price of cart.
        min_purchase_count: Minimum number of products in cart to use this
            coupon. None means this coupon can be used for any number of
            products.
        max_purchase_count: Maximum number of products in cart to use this
            coupon. None means this coupon can be used for any number of
            products.
        budget: Maximum amount that can be spent with this coupon in total.
            For example, if budget is 2000, and the amount is 500, users can
            apply this coupon only 4 times.
            None means this coupon has no budget limitation.
        max_usage_per_user: Maximum number of usage per user.
            None means each user can use this coupon unlimited number of
            times, but not in a single order.
        extra_data: same as :attr:`cart.models.Cart.extra_data`.


    """
    class Meta:
        verbose_name = _('محدودیت تخفیف')
        verbose_name_plural = _('محدودیت‌های تخفیف')
    coupon = models.OneToOneField(
        Coupon,
        on_delete=models.CASCADE,
        related_name='constraint',
        verbose_name=_('کوپن'))
    users = models.ManyToManyField(
        User, verbose_name=_('کاربران'),
        related_name='coupons', blank=True)
    shops = models.ManyToManyField(
        Shop, verbose_name=_('حجره'),
        related_name='coupons', blank=True)
    products = models.ManyToManyField(
        Product, verbose_name=_('محصول'),
        related_name='coupons', blank=True)
    # categories = models.ManyToManyField(Category, verbose_name=_('دسته
    # بندی'), related_name='coupons') TODO
    valid_from = models.DateField(
        _('تاریخ شروع'),
        default=now, null=True, blank=True)
    valid_to = models.DateField(_('تاریخ پایان'), null=True, blank=True)
    budget = models.IntegerField(_('بودجه کل کوپن'), default=0)
    max_usage_per_user = models.IntegerField(
        default=1, verbose_name=_('حداکثر دفعات استفاده کاربر'))
    max_usage = models.IntegerField(
        default=5, verbose_name=_('حداکثر دفعات استفاده'))
    min_purchase_amount = models.BigIntegerField(
        _('حداقل مقدار خرید'), null=True, blank=True)
    min_purchase_count = models.IntegerField(
        _('حداقل تعداد خرید'), null=True, blank=True)
    max_purchase_amount = models.BigIntegerField(
        _('حداکثر مقدار خرید'), null=True, blank=True)
    max_purchase_count = models.IntegerField(
        _('حداکثر تعداد خرید'), null=True, blank=True)
    cities = models.ManyToManyField(
        'nakhll_market.City',
        verbose_name=_('شهرها'),
        related_name='coupons',
        blank=True)

    extra_data = models.JSONField(
        _('اطلاعات اضافه'),
        null=True,
        blank=True,
        encoder=DjangoJSONEncoder)


class CouponUsage(models.Model):
    """ Coupon Usage model """
    class Meta:
        verbose_name = _('استفاده از کوپن تخفیف')
        verbose_name_plural = _('استفاده از کوپن های تخفیف')
    invoice = models.ForeignKey(
        Invoice,
        verbose_name=_('سفارش'),
        related_name='coupon_usages',
        on_delete=models.CASCADE)
    coupon = models.ForeignKey(
        Coupon,
        verbose_name=_('کوپن تخفیف'),
        on_delete=models.CASCADE,
        related_name='usages')
    used_datetime = models.DateTimeField(_('تاریخ استفاده'), default=now)
    price_applied = models.IntegerField(_('تخفیف اعمال شده'), default=0)
    objects = CouponUsageManager

    def __str__(self):
        return f'{self.coupon} - {self.price_applied} - {self.used_datetime}'
