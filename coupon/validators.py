from datetime import datetime
from django.utils.translation import ugettext as _
from django.utils.timezone import make_aware
from rest_framework.validators import ValidationError

class CountValidator:
    def __init__(self, user):
        self.user = user
    def __call__(self, coupon):
        max_usage = coupon.max_count
        user_usage = coupon.usages.filter(user=self.user).count()
        if user_usage >= max_usage:
            message = _(f'شما تابحال {user_usage} بار از این کوپن استفاده کرده اید و دیگر اجازه استفاده آن را ندارید.')
            raise ValidationError(message)

class DateTimeValidator:
    def __call__(self, coupon):
        now = make_aware(datetime.now())
        valid_from = coupon.valid_from
        valid_to = coupon.valid_to
        if valid_from > now:
            raise ValidationError(_('زمان استفاده از این کوپن تخفیف نرسیده است'))
        if valid_to < now:
            raise ValidationError(_('زمان استفاده از این کوپن تخفیف به پایان رسیده است'))

class PublishValidator:
    def __call__(self, coupon):
        if not coupon.is_publish:
            raise ValidationError(_('این کوپن فعال  نیست'))

class PriceValidator:
    def __init__(self, factor):
        self.total_factor_price = factor.total_price
    def __call__(self, coupon):
        if coupon.max_price and self.total_factor_price > coupon.max_price:
            raise ValidationError(_(f'حداکثر قیمت فاکتور برای استفاده از این کوپن باید {coupon.max_price} باشد.'))
        if coupon.min_price and self.total_factor_price < coupon.min_price:
            raise ValidationError(_(f'حداقل قیمت فاکتور برای استفاده از این کوپن باید {coupon.min_price} باشد.'))

class UserValidator:
    def __init__(self, user):
        self.user = user
    def __call__(self, coupon):
        if coupon.users and self.user not in coupon.users.all():
            raise ValidationError(_('این کوپن برای شما فعال نمی باشد.'))

class ShopValidator:
    def __init__(self, factor):
        self.shops = factor.shops
    def __call__(self, coupon):
        if coupon.shop and coupon.shop not in self.shops:
            raise ValidationError(_('این کوپن تنها در حجره‌ {coupon.shop} فعال می‌باشد.'))

class ProductValidator:
    def __init__(self, factor):
        self.products = factor.products
    def __call__(self, coupon):
        if coupon.product and coupon.product not in self.products:
            raise ValidationError(_('این کوپن تنها برای محصول {coupon.product} فعال می‌باشد.'))

