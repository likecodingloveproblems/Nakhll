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
            raise AvailableException(coupon, _('کوپن مورد نظر شما فعال نیست'))


class MaxUserCountValidator:
    def __init__(self, user):
        self.user = user
    def __call__(self, coupon):
        max_usage = coupon.constraint.max_usage_per_user 
        user_usage = coupon.usages.filter(invoice__user=self.user).count()
        if user_usage >= max_usage:
            raise MaxUserCountException(coupon, _('شما بیشتر از این نمی‌توانید از این کوپن استفاده کنید'), self.user)

class MaxCountValidator:
    def __call__(self, coupon):
        max_usage = coupon.constraint.max_usage
        usage = coupon.usages.count()
        if usage >= max_usage:
            raise MaxCountException(coupon, _('شما بیش از این نمی‌توانید از این کوپن استفاده کنید'))


class DateTimeValidator:
    def __call__(self, coupon):
        now = datetime.now().date()
        valid_from = coupon.constraint.valid_from
        valid_to = coupon.constraint.valid_to
        if valid_from and valid_from > now or valid_to and valid_to < now:
            raise DateTimeException(coupon, _('بازه زمانی استفاده از این کوپن به پایان رسیده است'), valid_from, valid_to)

class PriceValidator:
    def __init__(self, invoice):
        self.total_invoice_price = invoice.invoice_price_with_discount
    def __call__(self, coupon):
        if coupon.constraint.max_purchase_amount and self.total_invoice_price > coupon.constraint.max_purchase_amount\
            or coupon.constraint.min_purchase_amount and self.total_invoice_price < coupon.constraint.min_purchase_amount:
            raise PriceException(coupon, _('مبلغ فاکتور برای استفاده از این کوپن تخفیف مناسب نیست'), self.total_invoice_price)

class CountValidator:
    def __init__(self, invoice):
        self.total_invoice_count = invoice.items.count()
    def __call__(self, coupon):
        if coupon.constraint.max_purchase_count and self.total_invoice_count > coupon.constraint.max_purchase_count\
            or coupon.constraint.min_purchase_count and self.total_invoice_count < coupon.constraint.min_purchase_count:
            raise CountException(coupon, _('بیش از این نمی‌توانید از این کوپن استفاده کنید'), self.total_invoice_count)

class UserValidator:
    def __init__(self, user):
        self.user = user
    def __call__(self, coupon):
        if coupon.constraint.users.all() and self.user not in coupon.constraint.users.all():
            raise UserException(coupon, _('این کوپن برای استفاده شما تعریف نشده است'), self.user)

class ShopValidator:
    def __init__(self, invoice):
        self.shops = invoice.shops
    def __call__(self, coupon):
        if coupon.constraint.shops.all() and self.shops not in coupon.constraint.shops.all():
            raise ShopException(coupon, _('این کوپن برای استفاده از این فروشگاه تعریف نشده است'), self.shops)

class ProductValidator:
    def __init__(self, invoice):
        self.products = invoice.items.all().values_list('product', flat=True)
    def __call__(self, coupon):
        if coupon.constraint.products.all() and self.products not in coupon.constraint.products.all().values_list('ID', flat=True):
            raise ProductException(coupon, _('این کوپن برای استفاده روی این محصول تعریف نشده است'), self.products)

class BudgetValidator:
    def __call__(self, coupon):
        coupon_total_usage = coupon.usages.aggregate(Sum('price_applied'))['price_applied__sum']
        if coupon_total_usage and coupon.constraint.budget and self.budget < coupon_total_usage:
            raise BudgetException(coupon, _('بودجه این کوپن تمام شده است'), self.budget)

