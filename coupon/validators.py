from datetime import date, datetime
from django.db.models.aggregates import Sum
from django.utils.translation import ugettext as _
from django.utils.timezone import make_aware
from rest_framework.validators import ValidationError
from coupon.exceptions import (AvailableException, BudgetException, CountException, UserException,
                               ShopException, DateTimeException, MaxCountException,
                               MaxUserCountException, PriceException, ProductException)

class AvailableValidator:
    def __call__(self, coupon):
        if not coupon.available:
            raise AvailableException(coupon, _('Coupon is not available'))


class MaxUserCountValidator:
    def __init__(self, user):
        self.user = user
    def __call__(self, coupon):
        max_usage = coupon.constraint.max_usage_per_user 
        user_usage = coupon.usages.filter(invoice__user=self.user).aggregate(Sum('count'))['count__sum']
        if user_usage >= max_usage:
            raise MaxUserCountException(coupon, _('Maximum usage per user for this coupon reached'), self.user)

class MaxCountValidator:
    def __call__(self, coupon):
        max_usage = coupon.constraint.max_usage
        usage = coupon.usages.count()
        if usage >= max_usage:
            raise MaxCountException(coupon, _('Maximum usage for this coupon reached'))


class DateTimeValidator:
    def __call__(self, coupon):
        now = datetime.now().date()
        valid_from = coupon.constraint.valid_from
        valid_to = coupon.constraint.valid_to
        if valid_from and valid_from > now or valid_to and valid_to < now:
            raise DateTimeException(coupon, _('Datetime validation error'), valid_from, valid_to)

class PriceValidator:
    def __init__(self, invoice):
        self.total_invoice_price = invoice.total_price
    def __call__(self, coupon):
        if coupon.constraint.max_purchase_amount and self.total_invoice_price > coupon.constraint.max_purchase_amount\
            or coupon.constraint.min_purchase_amount and self.total_invoice_price < coupon.constraint.min_purchase_amount:
            raise PriceException(coupon, _('Price Error'), self.total_invoice_price)

class CountValidator:
    def __init__(self, invoice):
        self.total_invoice_count = invoice.total_product_count
    def __call__(self, coupon):
        if coupon.constraint.max_purchase_count and self.total_invoice_count > coupon.constraint.max_purchase_count\
            or coupon.constraint.min_purchase_count and self.total_invoice_count < coupon.constraint.min_purchase_count:
            raise CountException(coupon, _('Count error'), self.total_invoice_count)

class UserValidator:
    def __init__(self, user):
        self.user = user
    def __call__(self, coupon):
        if coupon.constraint.users.all() and self.user not in coupon.constraint.users.all():
            raise UserException(coupon, _('User error'), self.user)

class ShopValidator:
    def __init__(self, invoice):
        self.shops = invoice.shops
    def __call__(self, coupon):
        if coupon.constraint.shops.all() and self.shops not in coupon.constraint.shops.all():
            raise ShopException(coupon, _('ShopValidator'), self.shops)

class ProductValidator:
    def __init__(self, invoice):
        self.products = invoice.products
    def __call__(self, coupon):
        if coupon.constraint.products.all() and self.products not in coupon.constraint.products.all():
            raise ProductException(coupon, _('ProductValidator'), self.products)

class BudgetValidator:
    def __call__(self, coupon):
        coupon_total_usage = coupon.usages.aggregate(Sum('price_applied'))['price_applied__sum']
        if coupon_total_usage and coupon.constraint.budget and self.budget < coupon_total_usage:
            raise BudgetException(coupon, _('BudgetError'), self.budget)

