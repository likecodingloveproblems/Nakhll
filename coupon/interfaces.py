from datetime import datetime
from django.utils.timezone import make_aware
from rest_framework.validators import ValidationError
from coupon.validators import (BudgetValidator, DateTimeValidator, MaxCountValidator, MaxUserCountValidator, 
                               ProductValidator, AvailableValidator, UserValidator, PriceValidator,
                               ShopValidator, )
from coupon.exceptions import CouponException


class CouponValidation:
    ALL_VALIDATORS = '__all__'

    def _get_validators(self):
        assert hasattr(self, '_validators'), 'You must call coupon object with user, invoice and validators first'
            
        if self._validators == self.ALL_VALIDATORS:
            self._validators = [
                DateTimeValidator(),
                # MaxUserCountValidator(self._user),
                # MaxCountValidator(),
                PriceValidator(self._invoice),
                ProductValidator(self._invoice),
                AvailableValidator(),
                UserValidator(self._user),
                ShopValidator(self._invoice),
                BudgetValidator(),
            ]
        return self._validators



    def is_valid(self, invoice, validators=ALL_VALIDATORS, raise_exception=False):
        self._user = invoice.cart.user
        self._invoice = invoice
        self._validators = validators
        # if hasattr(self, '_errors'):
            # return True if len(self._errors) == 0 else False

        # TODO: Check if this coupon is in an active invoice or not

        self._final_price = None
        self._errors = []
        for validator in self._get_validators():
            try:
                validator(self)
            except CouponException as e:
                self._errors.append(e.message)
        return not self._errors

    def get_final_price(self):
        assert hasattr(self, '_errors'), 'You should call .is_valid() on coupon first'
        self._final_price = None
        if len(self._errors) == 0:
            # TODO: Some calculations
            return self.__calculate_coupon_price()

    def __calculate_coupon_price(self):
        if self.amount:
            return self.amount
        if self.presentage:
            amount = self.presentage * self._invoice.cart.total_price / 100
            return min(amount, self.max_amount) or amount
        return 0

    def apply(self, invoice):
        self.final_price = self.get_final_price()
        if self.final_price:
           self.usages.create(
               used_datetime=make_aware(datetime.now()),
               price_applied=self._final_price,
               invoice=invoice,
           )

    @property
    def final_price(self):
        assert hasattr(self, '_final_price'), 'You should call .is_valid() on coupon first'
        return self._final_price or 0

    @final_price.setter
    def final_price(self, value):
        assert hasattr(self, '_final_price'), 'You should call .is_valid() on coupon first'
        self._final_price = value

    @property
    def errors(self):
        assert hasattr(self, '_errors'), 'You should call .is_valid() on coupon first'
        return self._errors


