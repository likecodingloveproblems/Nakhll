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

class UserUsagePerInvoiceValidator:
    def __init__(self, invoice):
        self.invoice = invoice

    def __call__(self, coupon):
        invoice_usages = coupon.usages.filter(invoice=self.invoice).count()
        if invoice_usages > 0:
            raise UserException(coupon, _('کوپن تکراری است'), self.invoice.user)
        

class MaxUserCountValidator:
    def __init__(self, user):
        self.user = user
    def __call__(self, coupon):
        max_usage = coupon.constraint.max_usage_per_user 
        user_usage = coupon.usages.filter(invoice__user=self.user).count()
        if max_usage and user_usage >= max_usage:
            raise MaxUserCountException(coupon, _('شما بیشتر از این نمی‌توانید از این کوپن استفاده کنید'), self.user)

class MaxCountValidator:
    def __call__(self, coupon):
        max_usage = coupon.constraint.max_usage
        usage = coupon.usages.count()
        if max_usage and usage >= max_usage:
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
        self.invoice = invoice
    def __call__(self, coupon):
        if coupon.amount > self.invoice._coupon_shops_total_price:
            raise PriceException(coupon, _('مبلغ کوپن بیشتر از مبلغ فاکتور است'), self.invoice._coupon_shops_total_price)

class MinPriceValidator:
    def __init__(self, invoice):
        self.invoice = invoice
    def __call__(self, coupon):
        total_price = self.invoice._coupon_shops_total_price
        if coupon.constraint.min_purchase_amount and total_price < coupon.constraint.min_purchase_amount:
            message = 'حداقل مبلغ فاکتور برای اعمال این کوپن '
            message += 'از فروشگاه‌های {shops}'.format(
                shops=' و '.join(coupon.constraint.shops.values_list('Title', flat=True))
            ) if coupon.constraint.shops.count() else ''
            message += f' باید بیشتر از {coupon.constraint.min_purchase_amount:,} ریال باشد'
            raise PriceException(coupon, _(message), self.invoice._coupon_shops_total_price)

class MaxPriceValidator:
    def __init__(self, invoice):
        self.invoice = invoice
    def __call__(self, coupon):
        total_price = self.invoice._coupon_shops_total_price
        if coupon.constraint.max_purchase_amount and total_price > coupon.constraint.max_purchase_amount:
            message = 'حداکثر مبلغ فاکتور برای اعمال این کوپن '
            message += 'از فروشگاه‌های {shops}'.format(
                shops=' و '.join(coupon.constraint.shops.values_list('Title', flat=True))
            ) if coupon.constraint.shops.count() else ''
            message += ' باید کمتر از {} ریال باشد'.format(coupon.constraint.min_purchase_amount)
            raise PriceException(coupon, _(message), self.invoice._coupon_shops_total_price)
        
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
        if coupon.constraint.shops.all():
            flag = False
            for shop in self.shops:
                if shop in coupon.constraint.shops.all():
                    flag = True
                    break
            if not flag:
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


class CityValidator:
    def __init__(self, invoice):
        self.city = invoice.address.city if invoice.address else None
    def __call__(self, coupon):
        if coupon.constraint.cities.all() and self.city not in coupon.constraint.cities.all():
            raise CityException(coupon, _('این کوپن برای استفاده در این شهر تعریف نشده است'), self.city)