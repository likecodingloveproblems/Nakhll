from django.utils import timezone
from django.utils.translation import gettext as _
from coupon.validators import (BudgetValidator, DateTimeValidator,
                               MaxCountValidator, MaxUserCountValidator,
                               ProductValidator, AvailableValidator,
                               UserValidator, PriceValidator, ShopValidator,
                               UserUsagePerCartValidator, CityValidator,
                               MinPriceValidator, MaxPriceValidator)
from coupon.exceptions import CouponException


class CouponValidation:
    """Validating, calculating and applying coupon

    Raises:
        CouponException: if coupon is not valid, it will raise this exception
            or any other exception that is derived from it
    """
    ALL_VALIDATORS = '__all__'

    def _get_validators(self):
        """Get all or specific validators from :attr:`self._validators`

        Returns:
            list: list of all validator instances (not validator classes)
            Each validator should be callable (has __call__ magic method),
            initial values required for validation in each validator must pass
            to the validator in __init__ function during initialization.
            Process of validating coupon should be done in __call__ method of
            each validator
        """
        assert hasattr(self, '_validators'), '''You must call coupon object
                                                with user, invoice and
                                                validators first'''

        if self._validators == self.ALL_VALIDATORS:
            self._validators = [
                UserUsagePerCartValidator(self._cart),
                DateTimeValidator(),
                MaxUserCountValidator(self._user),
                MaxCountValidator(),
                PriceValidator(self._cart),
                MinPriceValidator(self._cart),
                MaxPriceValidator(self._cart),
                ProductValidator(self._cart),
                AvailableValidator(),
                UserValidator(self._user),
                ShopValidator(self._cart),
                BudgetValidator(),
                CityValidator(self._cart),
            ]
        return self._validators

    def is_valid(self, cart, validators=ALL_VALIDATORS):
        """Validate coupon using all validators by default

        For each validator, if it raise any deriven class of
        :attr:`coupon.exceptions.CouponException`, means there is validation
        error. The error message is accessible in exception message. The
        message will add to self._errors.

        Returns:
            bool: indicates whether coupon is valid or not
        """
        self._cart = cart
        self._user = cart.user
        self._cart._coupon_shops_total_price = self._get_total_cart_price(cart)
        self._validators = validators
        self._final_price = None
        self._errors = []

        for validator in self._get_validators():
            try:
                validator(self)
            except CouponException as e:
                self._errors.append(e.message)
        return not bool(self._errors)

    def apply(self, invoice):
        """Save coupon as coupon_usage for this specific invoice"""
        self._final_price = self.get_final_price()
        if self._final_price > invoice.invoice_price_with_discount:
            raise CouponException(_('مبلغ کوپن از مبلغ فاکتور بیشتر است'))
        if self._final_price:
            self.usages.create(
                used_datetime=timezone.now(),
                price_applied=self._final_price,
                invoice=invoice,
            )

    def get_final_price(self):
        """Calculate final price after applying coupon

        Returns:
            int: final price after applying coupon
        """
        assert hasattr(
            self, '_errors'), 'You should call .is_valid() on coupon first'
        self._final_price = None
        if len(self._errors) == 0:
            return self.calculate_coupon_price()

    def calculate_coupon_price(self):
        """Caculate coupon price according to coupon type

        If coupon type is percent, it should be calculated as:
        coupon_price = (total_cart_price * coupon_value) / 100, but make sure
        it is not greater that coupon max_amount

        If coupon type is amount, it should just return that amount
        """
        if self.amount:
            return self.amount
        if self.presentage:
            amount = self.presentage * self._cart.cart_price / 100
            return min(amount, self.max_amount) or amount
        return 0

    def _get_total_cart_price(self, cart):
        """Get total amount of all products in cart

        Return logistic_price plus total cart price if there are no shop
        constraints else it should only return total price of that shops, not
        all shops. This is because if there are shop constraints, the coupon
        should be applied only to that shops, so we have to make sure not to
        apply any amount larger than the shops total price.
        """
        if self.constraint.shops.all():
            total_price = 0
            shop_ids = self.constraint.shops.all().values_list('ID', flat=True)
            items = cart.items.filter(product__FK_Shop__ID__in=shop_ids)
            for item in items:
                total_price += item.product.price * item.count
            return total_price + cart.logistic_price
        return cart.cart_price + cart.logistic_price

    @property
    def final_price(self):
        assert hasattr(self, '_final_price'), '''You should call .is_valid()
                                                 on coupon first'''
        return self._final_price or 0

    @property
    def errors(self):
        assert hasattr(
            self, '_errors'), 'You should call .is_valid() on coupon first'
        return self._errors
