import json
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from nakhll_market.models import BankAccount, Product, Shop, State, BigCity, City
from logistic.managers import AddressManager
from logistic.interfaces import PostPriceSettingInterface


# Create your models here.

class Address(models.Model):
    ''' Addresses across all project '''
    class Meta:
        verbose_name = _('آدرس')
        verbose_name_plural = _('آدرس‌ها')
    old_id = models.UUIDField(null=True, blank=True)
    user = models.ForeignKey(User, verbose_name=_('کاربر'), related_name='addresses', on_delete=models.CASCADE)
    state = models.ForeignKey(State, verbose_name=_('استان'), related_name='addresses', on_delete=models.CASCADE)
    big_city = models.ForeignKey(BigCity, verbose_name=_('شهرستان'), related_name='addresses', on_delete=models.CASCADE)
    city = models.ForeignKey(City, verbose_name=_('شهر'), related_name='addresses', on_delete=models.CASCADE)
    address = models.TextField(verbose_name=_('آدرس'))
    zip_code = models.CharField(verbose_name=_('کد پستی'), max_length=10)
    phone_number = models.CharField(verbose_name=_('تلفن ثابت'), max_length=11, null=True, blank=True)
    receiver_full_name = models.CharField(verbose_name=_('نام و نام خانوادگی گیرنده'), max_length=200)
    receiver_mobile_number = models.CharField(verbose_name=_('تلفن همراه گیرنده'), max_length=11)

    objects = AddressManager()
    def __str__(self):
        return f'{self.user}: {self.address}'
    def to_json(self):
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


class PostPriceSetting(models.Model, PostPriceSettingInterface):
    ''' Post price settings '''
    class Meta:
        verbose_name = _('تنظیمات قیمت پستی')
        verbose_name_plural = _('تنظیمات قیمت پستی')
    user = models.ForeignKey(User, verbose_name=_('کاربر'), related_name='post_price_settings', on_delete=models.SET_NULL, null=True)
    inside_city_price = models.PositiveIntegerField(verbose_name=_('قیمت پست درون شهری (ریال)'), default=150000)
    outside_city_price = models.PositiveIntegerField(verbose_name=_('قیمت پست برون شهری (ریال)'), default=200000)
    extra_weight_fee = models.PositiveIntegerField(verbose_name=_('قیمت به ازای هر کیلو اضافه (ریال)'), default=20000)
    created_datetime = models.DateTimeField(verbose_name=_('تاریخ ایجاد'), auto_now_add=True)
    updated_datetime = models.DateTimeField(verbose_name=_('تاریخ بروزرسانی'), auto_now=True)
    def __str__(self):
        return f'{self.user}: {self.inside_city_price} تومان'
    

class LogisticUnitMetric(models.Model):
    class Meta:
        verbose_name = _('متریک ارسال')
        verbose_name_plural = _('متریک ارسال')

    price_per_kg = models.PositiveIntegerField(verbose_name=_('قیمت هر کیلوگرم'))
    price_per_extra_kg = models.PositiveIntegerField(verbose_name=_('قیمت هر کیلوگرم اضافه'))
    is_default = models.BooleanField(default=False, verbose_name=_('پیش فرض؟'))
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name=_('ایجاد کننده'))
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ بروزرسانی'), auto_now=True)


class LogisticUnitConstraintParameter(models.Model):
    class Meta:
        verbose_name = _('پارامتر محدودیت ارسال')
        verbose_name_plural = _('پارامتر محدودیت ارسال')
        
    cities = models.ManyToManyField(City, verbose_name=_('شهرها'))
    products = models.ManyToManyField(Product, verbose_name=_('محصولات'))
    min_price = models.DecimalField(verbose_name=_('حداقل قیمت'), max_digits=10, decimal_places=2)
    max_weight_g = models.PositiveIntegerField(verbose_name=_('حداکثر وزن (گرم)'))
    max_package_value = models.PositiveIntegerField(verbose_name=_('حداکثر ارزش بسته'))
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name=_('ایجاد کننده'))
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ بروزرسانی'), auto_now=True)

class LogisticUnit(models.Model):
    class Meta:
        verbose_name = _('واحد ارسال')
        verbose_name_plural = _('واحد ارسال')

    name = models.CharField(max_length=50, verbose_name=_('نام  '))
    description = models.TextField(null=True, blank=True, verbose_name=_('توضیحات'))
    is_publish = models.BooleanField(default=True, verbose_name=_('منتشر شده؟'))
    metric = models.ForeignKey(LogisticUnitMetric, on_delete=models.SET_NULL, null=True, verbose_name=_('متریک'))
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name=_('ایجاد کننده'))
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ بروزرسانی'), auto_now=True)


class LogisticUnitConstraint(models.Model):
    class Meta:
        verbose_name = _('محدودیت ارسال')
        verbose_name_plural = _('محدودیت ارسال')
        
    logistic_unit = models.ForeignKey(LogisticUnit, on_delete=models.SET_NULL, null=True, verbose_name=_('واحد ارسال'))
    constraint = models.ForeignKey(LogisticUnitConstraintParameter, on_delete=models.SET_NULL, null=True, verbose_name=_('محدودیت'))
    is_publish = models.BooleanField(default=True, verbose_name=_('منتشر شده؟'))
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name=_('ایجاد کننده'))
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ بروزرسانی'), auto_now=True)


class ShopLogisticUnit(models.Model):
    class Meta:
        verbose_name = _('واحد ارسال فروشگاه')
        verbose_name_plural = _('واحد ارسال فروشگاه')
        
    shop = models.ForeignKey(Shop, on_delete=models.SET_NULL, null=True, verbose_name=_('فروشگاه'))
    logistic_unit = models.ForeignKey(LogisticUnit, on_delete=models.SET_NULL, null=True, verbose_name=_('واحد ارسال'))
    is_active = models.BooleanField(default=True, verbose_name=_('فعال؟'))
    use_default_setting = models.BooleanField(default=True, verbose_name=_('استفاده از تنظیم پیش فرض؟'))
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ بروزرسانی'), auto_now=True)


class ShopLogisticUnitConstraint(models.Model):
    class Meta:
        verbose_name = _('محدودیت ارسال فروشگاه')
        verbose_name_plural = _('محدودیت ارسال فروشگاه')
        
    shop_logistic_unit = models.ForeignKey(ShopLogisticUnit, on_delete=models.SET_NULL, null=True, verbose_name=_('واحد ارسال فروشگاه'))
    constraint = models.ForeignKey(LogisticUnitConstraintParameter, on_delete=models.SET_NULL, null=True, verbose_name=_('محدودیت'))
    is_active = models.BooleanField(default=True, verbose_name=_('فعال؟'))
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ بروزرسانی'), auto_now=True)


class ShopLogisticUnitMetric(models.Model):
    class Meta:
        verbose_name = _('متریک فروشگاه')
        verbose_name_plural = _('متریک فروشگاه')
        
    shop_logistic_unit_constraint = models.ForeignKey(ShopLogisticUnit, on_delete=models.SET_NULL, null=True, verbose_name=_('واحد ارسال فروشگاه'))
    metric = models.ForeignKey(LogisticUnitMetric, on_delete=models.SET_NULL, null=True, verbose_name=_('متریک'))
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ بروزرسانی'), auto_now=True)
    