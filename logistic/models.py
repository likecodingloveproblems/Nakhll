import json
from django.db import models
from django.core.files import File
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from nakhll_market.models import Category, Product, Shop, State, BigCity, City
from logistic.managers import AddressManager, ShopLogisticUnitManager


User = get_user_model()


class Address(models.Model):
    """User addresses model

    Each user can have multiple addresses to choose from, in purchase process

    Attributes:
        old_id (UUID): same as :attr:`cart.models.Cart.old_id`
        user (User): user who owns this address
        state (State): Province for the address
        big_city (BigCity): Big City for this address
        city (City): City for this address
        address (str): actual address to user's location
        zip_code (str): postal code for user's address
        phone_number (str): phone number related to user's address
        receiver_full_name: Full name for user who is going to receive product
            This can be different from user who registerd in Nakhll
        receiver_mobile_number: Mobile number for user who is going to receive
            product. This can be different from user who registerd in Nakhll

    """
    class Meta:
        verbose_name = _('آدرس')
        verbose_name_plural = _('آدرس‌ها')
    old_id = models.UUIDField(null=True, blank=True)
    user = models.ForeignKey(User, verbose_name=_(
        'کاربر'), related_name='addresses', on_delete=models.CASCADE)
    state = models.ForeignKey(State, verbose_name=_(
        'استان'), related_name='addresses', on_delete=models.CASCADE)
    big_city = models.ForeignKey(BigCity, verbose_name=_(
        'شهرستان'), related_name='addresses', on_delete=models.CASCADE)
    city = models.ForeignKey(City, verbose_name=_(
        'شهر'), related_name='addresses', on_delete=models.CASCADE)
    address = models.TextField(verbose_name=_('آدرس'))
    zip_code = models.CharField(verbose_name=_('کد پستی'), max_length=10)
    phone_number = models.CharField(verbose_name=_(
        'تلفن ثابت'), max_length=11, null=True, blank=True)
    receiver_full_name = models.CharField(verbose_name=_(
        'نام و نام خانوادگی گیرنده'), max_length=200)
    receiver_mobile_number = models.CharField(
        verbose_name=_('تلفن همراه گیرنده'), max_length=11)

    objects = AddressManager()

    def __str__(self):
        return f'{self.user}: {self.address}'

    def as_json(self):
        """Return user address as json with all address details"""
        address_data = {
            'state': self.state.name,
            'big_city': self.big_city.name,
            'city': self.city.name,
            'address': self.address,
            'zip_code': self.zip_code,
            'phone_number': self.phone_number,
            'receiver_full_name': self.receiver_full_name,
            'receiver_mobile_number': self.receiver_mobile_number
        }
        return json.dumps(address_data, ensure_ascii=False)


class ShopLogisticUnit(models.Model):
    """Logistic units for a shop

    Each shop has 5 logistic unit by default after creation. These units are:
        - Free
        - Delivery
        - PAD(Pay at delivery)
        - Express Mail Service
        - Mail Service
    Shop owner can change these units or create a new ones. There is no
    explicit option in this class that indicates type of logistic unit,
    instead there are parameters like
    :attr:`ShopLogisticUnitCalculationMetric.PayTimes` or
    :attr:`ShopLogisticUnitCalculationMetric.PayerTypes` which user can set to
    indicates what kind of unit is this.

    Attributes:
        shop (Shop): Shop object related to this logistic unit
        name (str): Acctual name for this unit defined by user. This name will
            be displayed in both shop portal and user invoice page.
        logo (Image): Small logo for this unit. Logo will be ignored if value
            of :attr:`logo_type` is not :attr:`LogoType.CUSTOM`
        logo_type (LogoType): Each default logistic unit has it's own logo,
            this logo is identified by :attr:`LogoType`. All logo types are
            related to one of default logistic units except custom type
            which is :attr:`LogoType.CUSTOM`. This logo type along with
            :attr:`logo` field, indicates user custom logo for this unit.
        is_active (bool): user can deactivate this unit.
        is_publish (bool): staff memebers can deactivate this unit.
        description (str): description which shop owner can set for this unit.
        created_at (datetime): created datetime.
        updated_at (datetime): updated datetime.
        constraint (ShopLogisticUnitConstraint): Each unit has constraints,
            which contains some parameters to indicates limitations for this
            unit. This parameters are defined by shop owner.
        calculation_metric (ShopLogisticUnitCalculationMetric): Each unit has
            calculation metrics which contains some parameters to calculate
            price for this unit. This parameters are defined by shop owner.
    """
    class Meta:
        verbose_name = _('واحد ارسال فروشگاه')
        verbose_name_plural = _('واحد ارسال فروشگاه')
        ordering = ['-id']

    class LogoType(models.IntegerChoices):
        """Each default logistic unit has it's own logo.

        All logo types are related to one of default logistic units except
        custom type which is :attr:`LogoType.CUSTOM`. This logo type along
        with :attr:`logo` field, indicates user custom logo for this unit.
        """
        CUSTOM = 0, _('لوگوی شخصی')
        PPOST = 1, _('پست پیشتاز')
        SPOST = 2, _('پست سفارشی')
        DELIVERY = 3, _('پیک')
        PAD = 4, _('پسکرایه')
        FREE = 5, _('رایگان')

    shop = models.ForeignKey(
        Shop,
        verbose_name=_('حجره'),
        related_name='logistic_units',
        on_delete=models.CASCADE)
    name = models.CharField(verbose_name=_('نام واحد'), max_length=200)
    logo = models.ImageField(
        verbose_name=_('لوگو'),
        upload_to='media/Pictures/logistic_unit/defaults',
        null=True,
        blank=True,
        default='static/Pictures/unkown_lu.png')
    logo_type = models.IntegerField(
        verbose_name=_('نوع لوگو'),
        choices=LogoType.choices,
        default=LogoType.CUSTOM)
    is_active = models.BooleanField(verbose_name=_('فعال؟'),
                                    default=True)
    is_publish = models.BooleanField(verbose_name=_('منتشر شود؟'),
                                     default=True)
    description = models.TextField(
        verbose_name=_('توضیحات'),
        null=True, blank=True)
    created_at = models.DateTimeField(
        verbose_name=_('تاریخ ایجاد'),
        auto_now_add=True)
    updated_at = models.DateTimeField(
        verbose_name=_('تاریخ بروزرسانی'), auto_now=True)
    objects = ShopLogisticUnitManager()

    def __str__(self):
        return f'{self.shop}: {self.name}'

    def save(self, *args, **kwargs):
        self.save_logo()
        return super().save(**kwargs)

    def save_logo(self):
        """Save logo if logo_type is CUSTOM, else just ignore"""
        if self.logo_type != self.LogoType.CUSTOM:
            self.logo = File(
                open(
                    f'static/Pictures/{self.logo_type}.png',
                    'rb'))


class ShopLogisticUnitConstraint(models.Model):
    """Constraints for a single :attr:`ShopLogisticUnit`

    Constraints of a unit indicates the limitations for that unit like cities,
    products, categories, etc. This limitations is defined by shop owner.

    Attributes:
        - shop_logistic_unit (ShopLogisticUnit): logistic unit related to this
            constraint object
        - cities (City): Cities that this unit can be sent to. None means all
            cities are allowed.
        - products (Product): Products that can be sent with this unit. None
            means all products are allowed.
        - categories (Category): Categories that can be sent with this unit.
            None means all categories.
        - max_weight: Maximum weight for invoice that can be sent using this
            unit. Zero means there is no limitation for that.
        - min_weight: Minimum weight for invoice that can be sent using this
            unit. Zero means there is no limitation for that.
        - max_cart_price: Maximum invoice price that can be sent using this
            unit. Zero means there is no limitation for that.
        - min_cart_price: Minimum invoice price that can be sent using this
            unit. Zero means there is no limitation for that.
        - max_cart_count: Maximum invoice items count that can be sent using
            this unit. Zero means there is no limitation for that.
        - min_cart_count: Minimum invoice items count that can be sent using
            this unit. Zero means there is no limitation for that.
        - created_at: created datetime
        - updated_at: updated datetime
    """
    class Meta:
        verbose_name = _('محدودیت واحد ارسال فروشگاه')
        verbose_name_plural = _('محدودیت واحد ارسال فروشگاه')
        ordering = ['-id']

    shop_logistic_unit = models.OneToOneField(
        ShopLogisticUnit, verbose_name=_('واحد ارسال'),
        related_name='constraint', on_delete=models.CASCADE)
    cities = models.ManyToManyField(
        City, verbose_name=_('شهرها'),
        related_name='logistic_unit_constraints', blank=True)
    products = models.ManyToManyField(
        Product, verbose_name=_('محصولات'),
        related_name='logistic_unit_constraints', blank=True)
    categories = models.ManyToManyField(
        Category, verbose_name=_('دسته بندی ها'),
        related_name='logistic_unit_constraints', blank=True)
    max_weight = models.PositiveIntegerField(
        verbose_name=_('حداکثر وزن (کیلوگرم)'),
        default=0, null=True, blank=True)
    min_weight = models.PositiveIntegerField(
        verbose_name=_('حداقل وزن (کیلوگرم)'),
        default=0, null=True, blank=True)
    max_cart_price = models.PositiveIntegerField(
        verbose_name=_('حداکثر قیمت سبد خرید (ریال)'),
        default=0, null=True, blank=True)
    min_cart_price = models.PositiveIntegerField(
        verbose_name=_('حداقل قیمت سبد خرید (ریال)'),
        default=0, null=True, blank=True)
    max_cart_count = models.PositiveIntegerField(
        verbose_name=_('حداکثر تعداد سبد خرید'),
        default=0, null=True, blank=True)
    min_cart_count = models.PositiveIntegerField(
        verbose_name=_('حداقل تعداد سبد خرید'),
        default=0, null=True, blank=True)
    created_at = models.DateTimeField(
        verbose_name=_('تاریخ ایجاد'),
        auto_now_add=True)
    updated_at = models.DateTimeField(
        verbose_name=_('تاریخ بروزرسانی'), auto_now=True)

    def __str__(self):
        unit = self.shop_logistic_unit
        cities = self.cities.count()
        products = self.products.count()
        return f'{unit} - {cities} - {products}'


class ShopLogisticUnitCalculationMetric(models.Model):
    """Logistic Unit parameters for calculate prices

    Each unit has calculation metrics which contains some parameters to
    calculate price for this unit like price per each kilogram of product. This
    parameters are defined by shop owner.
    Attributes:
        shop_logistic_unit: Logistic unit related to this parameters
        price_per_kilogram: Price for each Kilogram of product (Toman)
        price_per_extra_kilogram: Price for each extra Kilogram of product
            (Toman)
        pay_time (PayTimes): This parameter indicates time for user or shop
            owner to pay for shipping. This value can be:
                - WHEN_BUYING: At payment time in IPG
                - AT_DELIVERY: At delivery time
        payer (PayerTypes): This parameter indicates who is going to pay for
            shipping. This value can be:
                - SHOP: Shipping cost is payed by shop owner, means this is a
                    free unit and user should not pay for shipping
                - CUSTOMER: Shipping cost must pay by customer, either in IPG
                    or delivery time.
        created_at: created datetime
        updated_at: updated datetime
    """
    class Meta:
        verbose_name = _('پارامتر‌ محاسبه واحد ارسال فروشگاه')
        verbose_name_plural = _('پارامتر‌ محاسبه واحد ارسال فروشگاه')
        ordering = ['-id']

    class PayTimes(models.TextChoices):
        """Payment time for shipping"""
        WHEN_BUYING = 'when_buying', _('هنگام خرید')
        AT_DELIVERY = 'at_delivery', _('هنگام تحویل')

    class PayerTypes(models.TextChoices):
        """Payer, which can be user or shop owner"""
        SHOP = 'shop', _('فروشگاه')
        CUSTOMER = 'cust', _('مشتری')

    shop_logistic_unit = models.OneToOneField(
        ShopLogisticUnit, verbose_name=_('واحد ارسال'),
        related_name='calculation_metric', on_delete=models.CASCADE)
    price_per_kilogram = models.FloatField(
        verbose_name=_('قیمت به ازای هر کیلو (ریال)'), default=0)
    price_per_extra_kilogram = models.FloatField(
        verbose_name=_('قیمت به ازای هر کیلو اضافه (ریال)'), default=0)
    pay_time = models.CharField(
        verbose_name=_('زمان پرداخت'),
        max_length=11,
        choices=PayTimes.choices,
        default=PayTimes.WHEN_BUYING)
    payer = models.CharField(
        verbose_name=_('پرداخت کننده'),
        max_length=4,
        choices=PayerTypes.choices,
        default=PayerTypes.CUSTOMER)
    created_at = models.DateTimeField(
        verbose_name=_('تاریخ ایجاد'),
        auto_now_add=True)
    updated_at = models.DateTimeField(
        verbose_name=_('تاریخ بروزرسانی'), auto_now=True)

    def __str__(self):
        unit = self.shop_logistic_unit
        ppkg = self.price_per_kilogram
        ppekg = self.price_per_extra_kilogram
        return f'{unit} - {ppkg} - {ppekg}'


class LogisticUnitGeneralSetting(models.Model):
    """General settings for default logistic units that will create for shops
        for first time

    Attributes:
         - default_price_per_kilogram
         - default_price_per_extra_kilogram
         - maximum_price_per_kilogram
         - maximum_price_per_extra_kilogram
         - created_at
         - updated_at
         - updated_by
    """
    class Meta:
        verbose_name = _('تنظیمات واحد ارسال')
        verbose_name_plural = _('تنظیمات واحد ارسال')

    default_price_per_kilogram = models.PositiveIntegerField(
        verbose_name=_('قیمت به ازای هر کیلو (ریال)'), default=0)
    default_price_per_extra_kilogram = models.PositiveIntegerField(
        verbose_name=_('قیمت به ازای هر کیلو اضافه (ریال)'), default=0)
    maximum_price_per_kilogram = models.PositiveIntegerField(
        verbose_name=_('حداکثر قیمت به ازای هر کیلو (ریال)'), default=0)
    maximum_price_per_extra_kilogram = models.PositiveIntegerField(
        verbose_name=_('حداکثر قیمت به ازای هر کیلو اضافه (ریال)'), default=0)
    created_at = models.DateTimeField(
        verbose_name=_('تاریخ ایجاد'),
        auto_now_add=True)
    updated_at = models.DateTimeField(
        verbose_name=_('تاریخ بروزرسانی'), auto_now=True)
    updated_by = models.ForeignKey(
        User, verbose_name=_('بروزرسانی توسط'),
        on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        dppkg = self.default_price_per_kilogram
        dppekg = self.default_price_per_extra_kilogram
        return f'{dppkg} - {dppekg}'

    def clean(self):
        super().clean()
        if not self.pk and LogisticUnitGeneralSetting.objects.exists():
            raise Exception(_('تنظیمات اصلی فقط می‌تواند به یک بار تنظیم شود'))
