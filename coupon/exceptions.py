"""Custom exceptions for coupon validation

    These exceptions will raise when coupon is not valid. Caller can use these
    exception to check why coupon is not valid.
"""


class CouponException(Exception):
    """Error raised when a coupon is invalid.

    This is the general coupon error, which is raised when specific coupon
    exception is not available or not created.

    Attributes:
        coupon: Coupon object that failed validation.
    """

    def __init__(self, coupon, message):
        super().__init__(message)
        self.coupon = coupon
        self.message = message


class MaxUserCountException(CouponException):
    """Error raised when user cannot use the coupon anymore

    There is a limit on how many times a user can use a coupon. This limit
    is defined in the coupon constraint at
    :attr:`coupon.models.CouponConstraint.max_usage_per_user`.
    """

    def __init__(self, coupon, message, user):
        super().__init__(coupon, message)
        self.user = user


class MaxCountException(CouponException):
    """Error raised  coupon reached maximum used number

    There is a limit on how many times a coupon can be used in total,
    regradless of usage per user. This limit is defined in the coupon
    constraint at :attr:`coupon.models.CouponConstraint.max_usage`.
    """


class DateTimeException(CouponException):
    """Error raised when coupon is not in valid datetime

    Each coupon has a validation period. Coupon is valid from
    :attr:`coupon.models.CouponConstraint.valid_from` to
    :attr:`coupon.models.CouponConstraint.valid_to`.
    """

    def __init__(self, coupon, message, valid_from, valid_to):
        super().__init__(coupon, message)
        self.valid_form = valid_from
        self.valid_to = valid_to


class AvailableException(CouponException):
    """Error raised  coupon is unavailable

    Coupon is available when :attr:`coupon.models.Coupon.available` is True.
    """


class PriceException(CouponException):
    """Error raised when invoice price is not in range of coupon price

    Coupon can have price limitaion, which is defined in either
    :attr:`coupon.models.CouponConstraint.min_purchase_amount` or
    :attr:`coupon.models.CouponConstraint.max_purchase_amount`. Also, the
    :attr:`coupon.models.Coupon.amount` itself, should be less than total cart
    price.
    """

    def __init__(self, coupon, message, total_invoice_price):
        super().__init__(coupon, message)
        self.total_invoice_price = total_invoice_price


class CountException(CouponException):
    """Error raised when invoice total products not in range of coupon count

    Coupon can have count limitation, which is defined in either
    :attr:`coupon.models.CouponConstraint.min_purchase_count` or
    :attr:`coupon.models.CouponConstraint.max_purchase_count`.
    """

    def __init__(self, coupon, message, total_invoice_count):
        super().__init__(coupon, message)
        self.total_invoice_count = total_invoice_count


class UserException(CouponException):
    """Error raised when requested user is not allowed to use this coupon

    Coupon can have user limitation, which is defined in
    :attr:`coupon.models.CouponConstraint.users`.
    """

    def __init__(self, coupon, message, users):
        super().__init__(coupon, message)
        self.users = users


class ShopException(CouponException):
    """Error raised when coupon is not valid for this shop

    Coupon can have shop limitation, which is defined in
    :attr:`coupon.models.CouponConstraint.shops`.
    """

    def __init__(self, coupon, message, shops):
        super().__init__(coupon, message)
        self.shops = shops


class ProductException(CouponException):
    """Error raised when coupon is not valid for this product

    Coupon can have product limitation, which is defined in
    :attr:`coupon.models.CouponConstraint.products`.
    """

    def __init__(self, coupon, message, products):
        super().__init__(coupon, message)
        self.products = products


class BudgetException(CouponException):
    """Error raised when coupon total usage is greater than coupon budget

    Coupon can have budget limitation, which is defined in
    :attr:`coupon.models.CouponConstraint.budget`. if total usage is greater
    than budget, coupon is not valid.
    """

    def __init__(self, coupon, message, budget):
        super().__init__(coupon, message)
        self.budget = budget


class CityException(CouponException):
    """Error raised when coupon is not valid for this city

    Coupon can have city limitation, which is defined in
    :attr:`coupon.models.CouponConstraint.cities`.
    """

    def __init__(self, coupon, message, cities):
        super().__init__(coupon, message)
        self.cities = cities
