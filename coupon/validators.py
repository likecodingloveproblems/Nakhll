"""Validator classes for coupons

    Each validator class Must implement __call__ method, which takes coupon as
    first argument and returns None if coupon is valid or raises an exception
    which is a subclass of :class:`coupon.exceptions.CouponException`.
    Any extra data can be passed to the validator class in __init__ method.

    Must of this validators are ignored if they coresponding value in coupon
    constraint is None (or zero for integer values). For example, if coupon
    constraint has max_usage_per_user value of None, then max_usage_per_user
    validator is ignored.
"""
from datetime import datetime
from django.db.models.aggregates import Sum
from django.utils.translation import ugettext as _
from coupon.exceptions import (AvailableException, BudgetException,
                               CountException, UserException, ShopException,
                               DateTimeException, MaxCountException,
                               CityException, MaxUserCountException,
                               PriceException, ProductException)


class AvailableValidator:
    """Check if coupon is available or not

    Coupon is available when :attr:`coupon.models.Coupon.available` is True.
    Availability of a coupon cannot be None, it's always either True or False.
    """

    def __call__(self, coupon):
        if not coupon.available:
            raise AvailableException(coupon, _('کوپن مورد نظر شما فعال نیست'))


class UserUsagePerCartValidator:
    """Insure that user doesn't use coupon more than once in same cart

    This validator should only be used when user is using coupon in cart. It
    doesn't allow user to add a single coupon more than once in cart.
    """

    def __init__(self, cart):
        self.cart = cart

    def __call__(self, coupon):
        usages = self.cart.coupons.filter(id=coupon.id).count()
        # invoice_usages = coupon.usages.filter(invoice=self.invoice).count()
        if usages > 0:
            raise UserException(coupon, _('کوپن تکراری است'), self.cart.user)


class MaxUserCountValidator:
    """Insure that user doesn't use coupon more than the allowed value

    Allowed value for a user is defined in
    :attr:`coupon.models.CouponConstraint.max_usage_per_user`. If this value
    is None, then this validator is ignored.
    """

    def __init__(self, user):
        self.user = user

    def __call__(self, coupon):
        max_usage = coupon.constraint.max_usage_per_user
        user_usage = coupon.usages.filter(invoice__user=self.user).count()
        if max_usage and user_usage >= max_usage:
            raise MaxUserCountException(
                coupon,
                _('شما بیشتر از این نمی‌توانید از این کوپن استفاده کنید'),
                self.user)


class MaxCountValidator:
    """Insure that coupon is not used more that it's max usage

    Coupon's max usage is defined in
    :attr:`coupon.models.CouponConstraint.max_usage`. If this value is None,
    then this validator is ignored.
    """

    def __call__(self, coupon):
        max_usage = coupon.constraint.max_usage
        usage = coupon.usages.count()
        if max_usage and usage >= max_usage:
            raise MaxCountException(coupon, _(
                'شما بیش از این نمی‌توانید از این کوپن استفاده کنید'))


class DateTimeValidator:
    """Insure that coupon is used within valid time range

    Coupon's valid time range is defined in coupon constraint as
    :attr:`coupon.models.CouponConstraint.valid_from` and
    :attr:`coupon.models.CouponConstraint.valid_to`. If these values are None,
    then this validator is ignored.
    """

    def __call__(self, coupon):
        now = datetime.now().date()
        valid_from = coupon.constraint.valid_from
        valid_to = coupon.constraint.valid_to
        if valid_from and valid_from > now or valid_to and valid_to < now:
            raise DateTimeException(
                coupon,
                _('بازه زمانی استفاده از این کوپن به پایان رسیده است'),
                valid_from,
                valid_to)


class PriceValidator:
    """Insure that coupon's price is not greater than cart's total price

    Coupon's price is defined in :attr:`coupon.models.Coupon.amount`. This
    validator cannot be ignored.
    """

    def __init__(self, cart):
        self.cart = cart

    def __call__(self, coupon):
        if coupon.amount > self.cart._coupon_shops_total_price:
            raise PriceException(coupon,
                                 _('مبلغ کوپن بیشتر از مبلغ سبد خرید است'),
                                 self.cart._coupon_shops_total_price)


class MinPriceValidator:
    """Cart's total price must be greater than coupon's min purchase amount

    Coupon's min purchase amount is defined in
    :attr:`coupon.models.Coupon.min_purchase_amount`. If this value is None,
    then this validator is ignored.
    """

    def __init__(self, cart):
        self.cart = cart

    def __call__(self, coupon):
        total_price = self.cart._coupon_shops_total_price
        if (
            coupon.constraint.min_purchase_amount and
            total_price < coupon.constraint.min_purchase_amount
        ):
            shops = ' و '.join(
                coupon.constraint.shops.values_list(
                    'Title', flat=True))
            message = 'حداقل مبلغ سبد خرید برای اعمال این کوپن '
            message += (
                f'از فروشگاه‌های {shops}'
                if coupon.constraint.shops.count()
                else ''
            )
            min_amount = coupon.constraint.min_purchase_amount
            message += f' باید بیشتر از {min_amount:,} ریال باشد'
            raise PriceException(
                coupon, _(message),
                self.cart._coupon_shops_total_price)


class MaxPriceValidator:
    """Cart's total price must be lower than coupon's max purchase amount

    Coupon's max purchase amount is defined in
    :attr:`coupon.models.Coupon.max_purchase_amount`. If this value is None,
    then this validator is ignored.
    """

    def __init__(self, cart):
        self.cart = cart

    def __call__(self, coupon):
        total_price = self.cart._coupon_shops_total_price
        if (
            coupon.constraint.max_purchase_amount and
            total_price > coupon.constraint.max_purchase_amount
        ):
            shops = ' و '.join(
                coupon.constraint.shops.values_list(
                    'Title', flat=True))
            message = 'حداکثر مبلغ سبد خرید برای اعمال این کوپن '
            message += (
                f'از فروشگاه‌های {shops}'
                if coupon.constraint.shops.count()
                else ''
            )
            max_amount = coupon.constraint.max_purchase_amount
            message += f' باید کمتر از {max_amount} ریال باشد'
            raise PriceException(
                coupon, _(message),
                self.cart._coupon_shops_total_price)


class CountValidator:
    """Cart's total items must be between coupon's min and max items count

    Coupon's min and max items count are defined in
    :attr:`coupon.models.CouponConstraint.min_purchase_count` and
    :attr:`coupon.models.CouponConstraint.max_purchase_count`. If these values
    are None, then this validator is ignored.
    """

    def __init__(self, cart):
        self.total_cart_items = cart.items.count()

    def __call__(self, coupon):
        if (
            coupon.constraint.max_purchase_count and
            self.total_cart_items > coupon.constraint.max_purchase_count or
            coupon.constraint.min_purchase_count and
            self.total_cart_items < coupon.constraint.min_purchase_count
        ):
            raise CountException(
                coupon,
                _('بیش از این نمی‌توانید از این کوپن استفاده کنید'),
                self.total_cart_items)


class UserValidator:
    """Insure that this coupon is valid for this user

    Coupon's valid users are defined in :attr:`coupon.models.Coupon.users`.
    If this value is empty, then this validator is ignored.
    """

    def __init__(self, user):
        self.user = user

    def __call__(self, coupon):
        if (
            coupon.constraint.users.all() and
            self.user not in coupon.constraint.users.all()
        ):
            raise UserException(
                coupon,
                _('این کوپن برای استفاده شما تعریف نشده است'),
                self.user)


class ShopValidator:
    """Insure that this coupon is valid for shops in cart

    Coupon's valid shops are defined in :attr:`coupon.models.Coupon.shops`.
    If only one of the shops in the cart is available in this coupon
    counstraint, then this validator is valid. This is a business rule, and
    can change in the future.
    If this value is empty, then this validator is ignored.
    """

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
                raise ShopException(
                    coupon,
                    _('این کوپن برای استفاده از این فروشگاه تعریف نشده است'),
                    self.shops)


class ProductValidator:
    """Insure that this coupon is valid for products in cart

    Coupon's valid products are defined in
    :attr:`coupon.models.CouponConstraint.products`.
    If this value is empty, then this validator is ignored.
    """

    def __init__(self, cart):
        self.products = cart.items.all().values_list('product', flat=True)

    def __call__(self, coupon):
        coupon_product_ids = coupon.constraint.products.values_list(
            'ID', flat=True)
        if (
            coupon.constraint.products.all() and
            self.products not in coupon_product_ids
        ):
            raise ProductException(
                coupon,
                _('این کوپن برای استفاده روی این محصول تعریف نشده است'),
                self.products)


class BudgetValidator:
    """Insure that the budget is not exceeded

    Coupon's budget is defined in
    :attr:`coupon.models.CouponConstraint.budget`.
    If this value is None, then this validator is ignored.
    """

    def __call__(self, coupon):
        coupon_total_usage = coupon.usages.aggregate(Sum('price_applied'))[
            'price_applied__sum']
        if (
            coupon_total_usage and
            coupon.constraint.budget and
            coupon.constraint.budget < coupon_total_usage
        ):
            raise BudgetException(
                coupon, _('بودجه این کوپن تمام شده است'),
                coupon.constraint.budget)


class CityValidator:
    """Insure that this coupon is valid for cart's city

    Coupon's valid cities are defined in
    :attr:`coupon.models.CouponConstraint.cities`.
    If this value is empty, then this validator is ignored.
    """

    def __init__(self, cart):
        self.city = cart.address.city if cart.address else None

    def __call__(self, coupon):
        if (
            coupon.constraint.cities.all() and
            self.city not in coupon.constraint.cities.all()
        ):
            raise CityException(
                coupon,
                _('این کوپن برای استفاده در این شهر تعریف نشده است'),
                self.city)
