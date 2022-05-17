from datetime import date, datetime
from django.db.models.aggregates import Sum
from django.utils.translation import ugettext as _
from django.utils.timezone import make_aware
from rest_framework.validators import ValidationError
from coupon.exceptions import (AvailableException, BudgetException, CountException, UserException,
                               ShopException, DateTimeException, MaxCountException, CityException,
                               MaxUserCountException, PriceException, ProductException)

class AvailableValidator:
    def __call__(self, coupon):
        if not coupon.available:
            raise AvailableException(coupon, _('کوپن مورد نظر شما فعال نیست'))

class UserUsagePerCartValidator:
    """Insure that user doesn't use coupon more than once in same cart"""
    def __init__(self, cart):
        self.cart = cart

    def __call__(self, coupon):
        usages = self.cart.coupons.filter(id=coupon.id).count()
        # invoice_usages = coupon.usages.filter(invoice=self.invoice).count()
        if usages > 0:
            raise UserException(coupon, _('کوپن تکراری است'), self.cart.user)
        

class MaxUserCountValidator:
    """Insure that user doesn't use coupon more than the value he/she allowed to use"""
    def __init__(self, user):
        self.user = user
    def __call__(self, coupon):
        max_usage = coupon.constraint.max_usage_per_user 
        user_usage = coupon.usages.filter(invoice__user=self.user).count()
        if max_usage and user_usage >= max_usage:
            raise MaxUserCountException(coupon, _('شما بیشتر از این نمی‌توانید از این کوپن استفاده کنید'), self.user)

class MaxCountValidator:
    """Insure that coupon is not used more that it's max usage"""
    def __call__(self, coupon):
        max_usage = coupon.constraint.max_usage
        usage = coupon.usages.count()
        if max_usage and usage >= max_usage:
            raise MaxCountException(coupon, _('شما بیش از این نمی‌توانید از این کوپن استفاده کنید'))


class DateTimeValidator:
    """Insure that coupon is used within valid time range"""
    def __call__(self, coupon):
        now = datetime.now().date()
        valid_from = coupon.constraint.valid_from
        valid_to = coupon.constraint.valid_to
        if valid_from and valid_from > now or valid_to and valid_to < now:
            raise DateTimeException(coupon, _('بازه زمانی استفاده از این کوپن به پایان رسیده است'), valid_from, valid_to)

class PriceValidator:
    """Insure that coupon's price is not greater than cart's total price"""
    def __init__(self, cart):
        self.cart = cart
    def __call__(self, coupon):
        if coupon.amount > self.cart._coupon_shops_total_price:
            raise PriceException(coupon, _('مبلغ کوپن بیشتر از مبلغ سبد خرید است'), self.cart._coupon_shops_total_price)

class MinPriceValidator:
    """Insure that cart's total price is greater than coupon's min purchase amount"""
    def __init__(self, cart):
        self.cart = cart
    def __call__(self, coupon):
        total_price = self.cart._coupon_shops_total_price
        if coupon.constraint.min_purchase_amount and total_price < coupon.constraint.min_purchase_amount:
            message = 'حداقل مبلغ سبد خرید برای اعمال این کوپن '
            message += 'از فروشگاه‌های {shops}'.format(
                shops=' و '.join(coupon.constraint.shops.values_list('Title', flat=True))
            ) if coupon.constraint.shops.count() else ''
            message += f' باید بیشتر از {coupon.constraint.min_purchase_amount:,} ریال باشد'
            raise PriceException(coupon, _(message), self.cart._coupon_shops_total_price)

class MaxPriceValidator:
    """Insure that cart's total price is lower than coupon's max purchase amount"""
    def __init__(self, cart):
        self.cart = cart
    def __call__(self, coupon):
        total_price = self.cart._coupon_shops_total_price
        if coupon.constraint.max_purchase_amount and total_price > coupon.constraint.max_purchase_amount:
            message = 'حداکثر مبلغ سبد خرید برای اعمال این کوپن '
            message += 'از فروشگاه‌های {shops}'.format(
                shops=' و '.join(coupon.constraint.shops.values_list('Title', flat=True))
            ) if coupon.constraint.shops.count() else ''
            message += ' باید کمتر از {} ریال باشد'.format(coupon.constraint.min_purchase_amount)
            raise PriceException(coupon, _(message), self.cart._coupon_shops_total_price)
        
class CountValidator:
    """Insure that cart's total items is between coupon's min and max items count"""
    def __init__(self, cart):
        self.total_cart_items = cart.items.count()
    def __call__(self, coupon):
        if coupon.constraint.max_purchase_count and self.total_cart_items > coupon.constraint.max_purchase_count\
            or coupon.constraint.min_purchase_count and self.total_cart_items < coupon.constraint.min_purchase_count:
            raise CountException(coupon, _('بیش از این نمی‌توانید از این کوپن استفاده کنید'), self.total_cart_items )

class UserValidator:
    """Insure that this coupon is valid for this user"""
    def __init__(self, user):
        self.user = user
    def __call__(self, coupon):
        if coupon.constraint.users.all() and self.user not in coupon.constraint.users.all():
            raise UserException(coupon, _('این کوپن برای استفاده شما تعریف نشده است'), self.user)

class ShopValidator:
    """Insure that this coupon is valid for shops in cart"""
    def __init__(self, cart):
        self.shops = cart.shops.all()
    def __call__(self, coupon):
        if coupon.constraint.shops.all():
            flag = False
            for shop in self.shops:
                if shop in coupon.constraint.shops.all():
                    flag = True
                    break
            if not flag:
                raise ShopException(coupon, _('این کوپن برای استفاده از این فروشگاه تعریف نشده است'), self.shops)

class ProductValidator:
    """Insure that this coupon is valid for products in cart"""
    def __init__(self, cart):
        self.products = cart.items.all().values_list('product', flat=True)
    def __call__(self, coupon):
        if coupon.constraint.products.all() and self.products not in coupon.constraint.products.all().values_list('ID', flat=True):
            raise ProductException(coupon, _('این کوپن برای استفاده روی این محصول تعریف نشده است'), self.products)

class BudgetValidator:
    """Insure that the budget is not exceeded"""
    def __call__(self, coupon):
        coupon_total_usage = coupon.usages.aggregate(Sum('price_applied'))['price_applied__sum']
        if coupon_total_usage and coupon.constraint.budget and coupon.constraint.budget < coupon_total_usage:
            raise BudgetException(coupon, _('بودجه این کوپن تمام شده است'), self.budget)


class CityValidator:
    """Insure that this coupon is valid for cart's city"""
    def __init__(self, cart):
        self.city = cart.address.city if cart.address else None
    def __call__(self, coupon):
        if coupon.constraint.cities.all() and self.city not in coupon.constraint.cities.all():
            raise CityException(coupon, _('این کوپن برای استفاده در این شهر تعریف نشده است'), self.city)