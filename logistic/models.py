import json
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from nakhll_market.models import BankAccount, State, BigCity, City
from logistic.managers import AddressManager
from logistic.interfaces import PostPriceSettingInterface


# Create your models here.

class Address(models.Model):
    ''' Addresses across all project '''
    class Meta:
        verbose_name = _('آدرس')
        verbose_name_plural = _('آدرس‌ها')
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
        return json.dumps(address_data)


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
    
