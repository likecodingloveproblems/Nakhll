class CouponException(Exception):
    '''Error raised when a coupon is invalid.

    Attributes:
        coupon: Coupon object that failed validation.
    '''
    def __init__(self, coupon):
        self.coupon = coupon


class MaxUserCountException(CouponException):
    '''Error raised when user cannot use the coupon anymore '''
    def __init__(self, coupon, user):
        super().__init__(coupon)
        self.user = user

class MaxCountException(CouponException):
    '''Error raised  coupon reached maximum used number'''

class DateTimeException(CouponException):
    '''Error raised when coupon is not in valid datetime'''
    def __init__(self, coupon, valid_from, valid_to):
        super().__init__(coupon)
        self.valid_form = valid_from
        self.valid_to = valid_to
    
class AvailableException(CouponException):
    '''Error raised  coupon is unavailable'''

class PriceException(CouponException):
    '''Error raised when invoice price is not in range of coupon price '''
    def __init__(self, coupon, total_invoice_price):
        super().__init__(coupon)
        self.total_invoice_price = total_invoice_price

class CountException(CouponException):
    '''Error raised when invoice total products not in range of coupon count '''
    def __init__(self, coupon, total_invoice_count):
        super().__init__(coupon)
        self.total_invoice_count = total_invoice_count

class UserException(CouponException):
    '''Error raised when requested user is not allowed to use this coupon '''
    def __init__(self, coupon, users):
        super().__init__(coupon)
        self.users = users
    
class ShopException(CouponException):
    '''Error raised when coupon is not valid for this shop '''
    def __init__(self, coupon, shops):
        super().__init__(coupon)
        self.shops = shops

class ProductException(CouponException):
    '''Error raised when coupon is not valid for this product '''
    def __init__(self, coupon, products):
        super().__init__(coupon)
        self.products = products


class BudgetException(CouponException):
    '''Error raised when coupon total usage is greater than coupon budget '''
    def __init__(self, coupon, budget):
        super().__init__(coupon)
        self.budget = budget
