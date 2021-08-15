from datetime import datetime
from django.contrib.auth.models import User
from django.utils.timezone import make_aware
from django.utils.translation import ugettext_lazy as _
from django.db import models
from rest_framework.validators import ValidationError
from nakhll_market.models import Shop, Product
from coupon.managers import CouponManager, CouponUsageManager
from coupon.validators import (DateTimeValidator, CountValidator, PriceValidator,
                               ProductValidator, PublishValidator, UserValidator,
                               ShopValidator, )


class CouponValidation:
    ALL_VALIDATORS = '__all__'

    def __call__(self, user, factor, validators=ALL_VALIDATORS):
        self._user = user
        self._factor = factor
        self._validators = validators

    def get_validators(self):
        assert hasattr(self, '_validators'), 'You must call coupon object with user, factor and validators first'
            
        if self._validators == self.ALL_VALIDATORS:
            self._validators = [
                DateTimeValidator(),
                CountValidator(self._user),
                PriceValidator(self._factor),
                ProductValidator(self._factor),
                PublishValidator(),
                UserValidator(self._user),
                ShopValidator(self._factor)
            ]
        return self._validators



    def is_valid(self):
        # if hasattr(self, '_errors'):
            # return True if len(self._errors) == 0 else False

        self._errors = []
        for validator in self.get_validators():
            try:
                validator(self)
            except ValidationError as exc:
                self._errors.append(exc.args)
        self.__get_final_price()

        return not self._errors

    def __get_final_price(self):
        assert hasattr(self, '_errors'), 'You should call .is_valid() on coupon first'
        self._final_price = None
        if len(self._errors) == 0:
            # Some calculations
            self.final_price = self.price

    def apply(self, order):
       if hasattr(self, '_final_price') and self._final_price is not None:
           self.usages.create(
               user=self._user,
               used_date=make_aware(datetime.now()),
               price_applied=self._final_price,
               # order=order,
           )

    @property
    def final_price(self):
        assert hasattr(self, '_final_price'), 'You should call .is_valid() on coupon first'
        return self._final_price

    @final_price.setter
    def final_price(self, value):
        assert hasattr(self, '_final_price'), 'You should call .is_valid() on coupon first'
        self._final_price = value


    @property
    def errors(self):
        assert hasattr(self, '_errors'), 'You should call .is_valid() on coupon first'
        return self._errors



class Coupon(models.Model, CouponValidation):
    ''' Coupon model '''
    class Meta:
        verbose_name = _('کوپن تخفیف')
        verbose_name_plural = _('کوپن‌های تخفیف')
    code = models.CharField(_('کد تخفیف'), max_length=100, unique=True)
    valid_from = models.DateTimeField(_('تاریخ شروع'), default=datetime.now, null=True, blank=True)
    valid_to = models.DateTimeField(_('تاریخ پایان'), null=True, blank=True)
    max_count = models.IntegerField(default=1, verbose_name=_('دفعات استفاده'))
    is_publish = models.BooleanField(_('وضعیت انتشار'), default=True)
    price = models.IntegerField(_('مبلغ تخفیف'), default=0)
    min_price = models.IntegerField(_('حداقل خرید'), null=True, blank=True)
    max_price = models.IntegerField(_('حداکثر خرید'), null=True, blank=True)
    users = models.ManyToManyField(User, verbose_name=_('کاربران'), blank=True, related_name='coupons')
    shop = models.ForeignKey(Shop, null=True, blank=True, verbose_name=_('حجره'), on_delete=models.SET_NULL, related_name='coupons')
    product = models.ForeignKey(Product, null=True, blank=True, verbose_name=_('محصول'), on_delete=models.SET_NULL, related_name='coupons')
    description = models.TextField(_('توضیحات'), null=True, blank=True )
    objects = CouponManager

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





