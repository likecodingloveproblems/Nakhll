import logging
from uuid import uuid4
from datetime import datetime, timedelta
from django.db import models
from django.conf import settings
from django.db.models.query_utils import Q
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth.models import User
from django_jalali.db import models as jmodels
from bank.constants import RequestTypes
from bank.views import deposit_user
from cart.managers import CartManager
from invoice.constants import PURCHASE_REWARD, PURCHASE_VOLUME_LIMIT, PURCHASE_VOLUME_REWARD
from nakhll.utils import datetime2jalali
from nakhll_market.interface import AlertInterface
from nakhll_market.models import Category, Product, Shop
from payoff.models import Transaction
from payoff.interfaces import PaymentInterface
from payoff.exceptions import (
    NoAddressException, InvoiceExpiredException,
    InvalidInvoiceStatusException, NoItemException,
)
from invoice.managers import AccountingManager, InvoiceItemManager
from logistic.models import ShopLogisticUnit
from refer.models import ReferrerPurchaseEvent
from sms.services import Kavenegar

logger = logging.getLogger(__name__)


class Invoice(models.Model):
    """Invoice model for each user purchase from shop

    Just before reaching IPG, invoice will create from user's cart. user have
    6 hours (configured from settings.INVOICE_EXPIRING_HOURS) to pay invoice,
    after that, invoice will expire and cannot payed anymore.

    Attributes:
        user (User): global user model
        old_id: the UUID field in previous design system. This field is not
            using anymore, it is just for reference to old database
        FactorNumber: this is also just for reference to old database and
            not used anymore
        status: indicate invoice status, options can be found at
            :class:`Statuses`
        address_json: while creating invoice from cart, value of
            :attr:`cart.models.Cart.address` is converted to json using
            :func:`logistic.models.Address.as_json`
            and then saved in this field
        invoice_price_with_discount: this is the price of invoice with
            shop's own discount
        invoice_price_without_discount: this is the price of invoice without
            shop's own discount
        logistic_price: this is the price of logistic unit
        created_datetime: this is the datetime of invoice creation
        payment_request_datetime: this is the last datetime when invoice is
            sent to payment gateway by user.
        payment_datetime: datetime of payment success
        payment_unique_id: unique id that will generated when user
            send invoice to payment gateway. This id will be sent to payment
            gateway as it's unique id. Also we can use this field to connect
            :attr:`payoff.models.Transaction` to invoice after successful
            payment.
        extra_data: same as :attr:`cart.models.Cart.extra_data`
        total_weight_gram: total weight of all items in invoice
        logistic_unit_details: JSON representation of logistic unit details,
            including all types of logistic unit that are going to be used to
            send invoice items to user, which their price.
    """

    class Statuses(models.TextChoices):
        """Status values for field status of invoice

        Statuses are designed to change in process of purchase
        in this order:

            1. awaiting_paying
            2. wait_store_approv
            3. preparing_product
            4. wait_customer_approv
            5. wait_store_checkout
            6. completed

        There are 2 drawback with this statuses

        1. In order to check if invoice is accepted by store, it should be one
        of this statuses:

            a. preparing_product
            b. wait_customer_approv
            c. wait_store_checkout
            d. completed

        or it should NOT be one of these statuses:

            a. awaiting_paying
            b. wait_store_approv

        this means you should check multiple statuses to find out what is the
        current status of invoice maybe it's better to change statuses from
        text to integer

        2. Invoice can be canceled at any time, in any status, so we cannot
        findout in which status invoice canceled. Maybe it's better to separate
        canceled status in another column with it's datetime and reason
        """

        AWAIT_PAYMENT = 'awaiting_paying', _('در انتظار پرداخت')
        AWAIT_SHOP_APPROVAL = 'wait_store_approv', _('در انتظار تأیید فروشگاه')
        PREPATING_PRODUCT = 'preparing_product', _('در حال آماده سازی')
        AWAIT_CUSTOMER_APPROVAL = 'wait_customer_approv', _(
            'در انتظار تأیید مشتری')
        AWAIT_SHOP_CHECKOUT = 'wait_store_checkout', _(
            'در انتظار تسویه با فروشگاه')
        COMPLETED = 'completed', _('تکمیل شده')
        CANCELED = 'canceled', _('لغو شده')

    class Meta:
        verbose_name = _('فاکتور')
        verbose_name_plural = _('فاکتورها')
        ordering = ('-id',)
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name=_('کاربر'))
    old_id = models.UUIDField(null=True, blank=True)
    FactorNumber = models.CharField(
        _('شماره فاکتور'),
        max_length=50,
        null=True,
        blank=True,
        unique=True)
    status = models.CharField(
        _('وضعیت فاکتور'),
        max_length=20,
        default=Statuses.AWAIT_PAYMENT,
        choices=Statuses.choices)
    address_json = models.JSONField(
        _('آدرس ثبت شده نهایی'),
        null=True,
        blank=True,
        encoder=DjangoJSONEncoder)
    invoice_price_with_discount = models.DecimalField(
        _('مبلغ فاکتور با تخفیف'),
        max_digits=12, decimal_places=0, default=0)
    invoice_price_without_discount = models.DecimalField(
        _('مبلغ فاکتور بدون تخفیف'),
        max_digits=12, decimal_places=0, default=0)
    logistic_price = models.DecimalField(
        _('هزینه حمل و نقل'),
        max_digits=12, decimal_places=0, default=0)
    coin_price = models.DecimalField(
        _('مبلغ سکه های پرداخت شده'),
        max_digits=12, decimal_places=0, default=0)
    coin_amount = models.IntegerField(
        _('coins amount'), default=0
    )
    created_datetime = models.DateTimeField(
        _('تاریخ ایجاد فاکتور'), auto_now_add=True)
    payment_request_datetime = models.DateTimeField(
        _('تاریخ درخواست پرداخت'), null=True, blank=True)
    payment_datetime = models.DateTimeField(
        _('تاریخ پرداخت'), null=True, blank=True)
    payment_unique_id = models.BigIntegerField(
        _('شماره درخواست پرداخت'), null=True, blank=True)
    extra_data = models.JSONField(
        null=True, blank=True, encoder=DjangoJSONEncoder)
    total_weight_gram = models.PositiveIntegerField(
        _('وزن نهایی (گرم)'), null=True, blank=True)
    logistic_unit_details = models.JSONField(
        null=True, blank=True, encoder=DjangoJSONEncoder,
        verbose_name=_('جزئیات واحد حمل و نقل'))
    description = models.TextField(
        verbose_name='توضیحات', null=True, blank=True)
    date_checkout = jmodels.jDateTimeField(
        verbose_name='تاریخ تسویه', null=True, blank=True)
    date_canceled = jmodels.jDateTimeField(
        verbose_name='تاریخ لغو', null=True, blank=True)
    objects = AccountingManager()

    def __str__(self):
        return f'{self.id} ({self.FactorNumber})'

    @property
    def shops(self):
        """All shops in this invoice"""
        shop_ids = self.items.values_list(
            'product__FK_Shop__ID', flat=True).distinct()
        return Shop.objects.filter(ID__in=shop_ids)

    @property
    def products(self):
        """All products in this invoice"""
        product_ids = self.items.values_list(
            'product__ID', flat=True).distinct()
        return Product.objects.filter(ID__in=product_ids)

    @property
    def categories(self):
        """All categories in this invoice"""
        category_ids = self.items.values_list(
            'product__category__id', flat=True).distinct()
        return Category.objects.filter(id__in=category_ids)

    @property
    def barcodes(self):
        """All barcodes in this invoice"""
        return self.items.exclude(
            barcode=None).values_list('barcode', flat=True)

    @property
    def logistic_errors(self):
        return ""
        # post_setting, is_created = PostPriceSetting.objects.get_or_create()
        # out_of_range = post_setting.get_out_of_range_products(self)
        # return out_of_range

    @property
    def coupons_total_price(self):
        """Coupons total price that is applied in this invoice"""
        final_price = 0
        usages = self.coupon_usages.all()
        for usage in usages:
            final_price += usage.price_applied
        return final_price

    @property
    def final_price(self):
        """ Total amount of cart_price + logistic - coupon - coin"""
        total_price = self.invoice_price_with_discount
        logistic_price = self.logistic_price
        coupon_price = self.coupons_total_price
        return total_price + logistic_price - coupon_price - self.coin_price

    @property
    def jpayment_datetime(self):
        return datetime2jalali(self.payment_datetime)

    def send_to_payment(self, bank_port=Transaction.IPGTypes.PEC):
        """Send this invoice to payment

        Args:
            bank_port (Transaction.IPGTypes, optional): Internet Payment
            Gateway which should handle the payment. Defaults to
            :attr:`payoff.models.Transaction.IPGTypes.PEC`.

        Returns:
            A link to payment page that user should be redirected to, in order
            to pay for this invoice.
        """

        self.__validate_items()
        self.__validate_address()
        self.__validate_invoice_status()
        self.__validate_invoice_expiring_date()
        self.payment_unique_id = int(datetime.now().timestamp() * 1000000)
        self.payment_request_datetime = timezone.now()
        self.save()
        return PaymentInterface.from_invoice(self, bank_port)

    def __validate_items(self):
        """Check if there are any items in this invoice"""
        if not self.items.count():
            raise NoItemException()

    def __validate_address(self):
        """Check if there is an address in this invoice"""
        if not self.address_json:
            raise NoAddressException()

    def __validate_invoice_expiring_date(self):
        """Check if invoice is not expired

        Invoices will expire after a certain time, which is defined in
        :attr:`nakhll.settings.INVOICE_EXPIRING_HOURS`.
        """
        expire_datetime = self.created_datetime + \
            timedelta(hours=settings.INVOICE_EXPIRING_HOURS)
        if expire_datetime < timezone.now():
            raise InvoiceExpiredException()

    def __validate_invoice_status(self):
        """Check if invoice status in :attr:`Statuses.AWAIT_PAYMENT`"""
        if self.status != self.Statuses.AWAIT_PAYMENT:
            raise InvalidInvoiceStatusException()

    def complete_payment(self):
        """Operations that should be done after payment is completed

        This function is called by
        :func:`payoff.payment.PaymentMethod.callback()`, after successful
        payment by user. So here is the best place to do any operations that
        should be done after payment is completed.

        Currently, this function does the following:
          - Reduce stock of products in this invoice
          - Send SMS notifications to user and shops
          - Send Discord Alert to Staff members
          - Set invoice status to :attr:`Statuses.AWAIT_SHOP_APPROVAL`
          - Set :attr:`payment_datetime` to current time
        """

        self._reduce_inventory()
        self._send_notifications()
        self.status = self.Statuses.AWAIT_SHOP_APPROVAL
        self.payment_datetime = timezone.now()
        self.save()
        self.give_rewarded_coins()

    def _reduce_inventory(self):
        """Reduce bought items from shops stock"""
        items = self.items.all()
        for item in items:
            item.product.reduce_stock(item.count)

    def _send_notifications(self):
        """Send SMS to user and shop_owner and create alert for staff"""
        shop_owner_mobiles = self.items.all().values_list(
            'product__FK_Shop__FK_ShopManager__User_Profile__MobileNumber',
            flat=True).distinct()
        logger.debug(f'Shop owner mobiles: {shop_owner_mobiles}')
        for mobile_number in shop_owner_mobiles:
            Kavenegar.shop_new_order(mobile_number, self.id)
        AlertInterface.new_order(self)

    def revert_payment(self):
        """Operations that should be done after payment is failed

        This function is called by
        :func:`payoff.payment.PaymentMethod.callback()`, after failed payment
        by user. So here is the best place to do any operations that should
        be done after payment is failed.

        Currently, this function does the following:
            - Unset all coupons that are applied in this invoice
            - Fill user's cart with items that are in this invoice
            - Set invoice status to :attr:`Statuses.AWAIT_PAYMENT`
        """

        self.unset_coupons()
        self.fill_cart()
        self.status = self.Statuses.AWAIT_PAYMENT
        self.save()

    def unset_coupons(self):
        """Delete all coupon usages from invoice"""
        coupon_usages = self.coupon_usages.all()
        for coupon_usage in coupon_usages:
            coupon_usage.delete()

    def available_logistic_units(self):
        """Return available logistic units for this invoice"""
        ShopLogisticUnit.objects.filter(
            # Q(shop__ShopProduct=p),
            ~Q(logistic_unit__logistic_unit_constraints__constraint__products__in=self.products),
            ~Q(logistic_unit__logistic_unit_constraints__constraint__categories__in=self.categories),
            ~Q(logistic_unit__logistic_unit_constraints__constraint__cities=self.address.city),
        ).distinct()

    def fill_cart(self):
        """Fill user's cart with items that are in this invoice"""
        cart = CartManager.user_active_cart(self.user)
        for item in self.items.all():
            cart.add_product(item.product)
        cart.reset_coupons()
        cart.reset_address()

    def give_rewarded_coins(self):
        """Give rewarded coins to user for this purchase"""
        if self._is_user_rewarded():
            self._give_referrer_coins()
            self._give_buyer_coins()

    def _is_user_rewarded(self):
        """this will check that this invoice will give coin reward to users or not
        Only referrer and referred users will get coins for purchase"""
        return self.user.User_Profile.is_referred

    def _give_referrer_coins(self):
        """Give referrer purchase coins"""
        ReferrerPurchaseEvent.objects.create(
            referrer=self.user.User_Profile.referrer,
            invoice=self
        )

    def _give_buyer_coins(self):
        """give purchase coins"""
        deposit_user(
            user=self.user,
            request_type=RequestTypes.PURCHASE_REWARD,
            amount=self.reward_coins_amount,
            description=self.reward_description
        )

    @property
    def reward_coins_amount(self):
        """Calculate rewarded coins for this invoice based on the final price"""
        return self.final_price // PURCHASE_VOLUME_LIMIT * PURCHASE_VOLUME_REWARD + PURCHASE_REWARD

    @property
    def reward_description(self):
        return f'id:{self.id} - payment datetime:{self.payment_datetime} -\
                user:{self.user.username} - final price:{self.final_price} -\
                coins:{self.reward_coins_amount}'


class InvoiceItem(models.Model):
    """Invoice items model

    This model is used to store items that are in an invoice. Each invoice can
    have multiple items.

    This model has a relationship to :class:`nakhll_market.models.Product`,
    which means it has access to all the fields of that class, but we still
    need to store some of its fields in this model too. The reason is,
    attributes in this model must be immutable, and should not be changed if
    chagnes happen in the related :class:`nakhll_market.models.Product`.

    Note that, user confirmation which has 3 fields in this model, is not yet
    implemented in front-end.

    Attributes:
        invoice (Invoice): Invoice that this item is in
        product (Product): Product that is in this item
        count (int): Count of this item
        status (InvoiceItem.Statuses): Status of this item
        created_datetime (datetime): Datetime when this item was created
        slug: Product slug which is hardcoded in this model
        name: Product name which is hardcoded in this model
        barcode: Product barcode which is hardcoded in this model
        price_with_discount: Product price_with_discount which is hardcoded in
            this model
        price_without_discount: Product price_without_discount which is
            hardcoded in this model
        weight: single Product weight which is hardcoded in this model
        image: Product image which is hardcoded in this model
        image_thumbnail: Product image_thumbnail which is hardcoded in this
            model
        shop_name: Shop name which is hardcoded in this model
        added_datetime: Datetime when this item was added to this invoice
        shop_confirmed_datetime: Datetime when this item was confirmed by shop
            owner
        post_type: This field is deprecated and should be removed in future
        post_tracking_code: Tracking code for this item which shop owner will
            fill in, after sending this item to user
        user_confirmed_datetime: Datetime when this item was recieved to user
            and confirmed by user
        user_confirm_status: Status of this item after user confirmed it
        user_confirm_comment: Comment that user gave to this item for
            confirmation.
    """

    class Meta:
        verbose_name = _('آیتم فاکتور')
        verbose_name_plural = _('آیتم های فاکتور')

    class ItemStatuses(models.TextChoices):
        """statuses for each item are the same as in :class:`Invoice`"""

        AWAIT_PAYMENT = 'awaiting_paying', _('در انتظار پرداخت')
        AWAIT_SHOP_APPROVAL = 'wait_store_approv', _('در انتظار تأیید فروشگاه')
        PREPATING_PRODUCT = 'preparing_product', _('در حال آماده سازی')
        AWAIT_CUSTOMER_APPROVAL = 'wait_customer_approv', _(
            'در انتظار تأیید مشتری')
        AWAIT_SHOP_CHECKOUT = 'wait_store_checkout', _(
            'در انتظار تسویه با فروشگاه')
        COMPLETED = 'completed', _('تکمیل شده')
        CANCELED = 'canceled', _('لغو شده')

    class UserConfirmStatuses(models.TextChoices):
        """Status of this item after user confirmed it

            Attributes:
                AWAIT_CONFIRM: waiting for user to confirm it
                CONFIRMED: user confirmed
                REJECTED: user rejected
        """

        AWAIT_CONFIRM = 'awaiting_confirm', _('در انتظار تایید')
        CONFIRMED = 'confirmed', _('تایید شده')
        REJECTED = 'rejected', _('رد شده')

    class PostType(models.TextChoices):
        """Previously used to indicates that this item is going to be sent
            using national post, or it'll send by in-city delivery services
            This field is deprecated and should be removed in future
        """

        IRPOST = 'irpost', _('شرکت پست')
        INCITY = 'incity', _('درون شهری')

    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.PROTECT,
        related_name='items',
        verbose_name=_('فاکتور'))
    product = models.ForeignKey(Product, on_delete=models.PROTECT,
                                related_name='invoice_items')
    count = models.IntegerField(_('تعداد'), default=1)
    status = models.CharField(
        _('وضعیت'),
        max_length=20,
        choices=ItemStatuses.choices,
        default=ItemStatuses.AWAIT_PAYMENT)

    slug = models.CharField(max_length=500, null=True, blank=True)
    name = models.CharField(_('نام محصول'), max_length=500)
    price_with_discount = models.DecimalField(
        _('قیمت با تخفیف'), max_digits=12, decimal_places=0)
    price_without_discount = models.DecimalField(
        _('قیمت بدون تخفیف'), max_digits=12, decimal_places=0)
    weight = models.DecimalField(_('وزن'), max_digits=10, decimal_places=0)
    image = models.ImageField(
        _('تصویر'),
        upload_to='invoice_items',
        null=True,
        blank=True,
        max_length=500)
    image_thumbnail = models.ImageField(
        _('تصویر کوچک'),
        upload_to='invoice_items',
        null=True,
        blank=True,
        max_length=500)
    shop_name = models.CharField(_('نام فروشگاه'), max_length=500)
    added_datetime = models.DateTimeField(_('تاریخ افزودن'), auto_now_add=True)
    shop_confirmed_datetime = models.DateTimeField(
        _('تاریخ تایید فروشگاه'), null=True, blank=True)
    post_type = models.CharField(
        _('نوع پست'),
        max_length=20,
        choices=PostType.choices,
        null=True,
        blank=True)
    post_tracking_code = models.CharField(
        _('کد رهگیری پستی'),
        max_length=100, null=True, blank=True)
    user_confirm_datetime = models.DateTimeField(
        _('تاریخ تایید کاربر'), null=True, blank=True)
    user_confirm_status = models.CharField(
        _('وضعیت تایید کاربر'),
        max_length=20,
        choices=UserConfirmStatuses.choices,
        null=True,
        blank=True)
    user_confirm_comment = models.TextField(
        _('توضیحات تایید کاربر'), null=True, blank=True)
    barcode = models.CharField(
        _('کد بارکد'),
        max_length=100,
        null=True,
        blank=True)

    objects = InvoiceItemManager()
