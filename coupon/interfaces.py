from datetime import datetime
from django.utils.timezone import make_aware
from rest_framework.validators import ValidationError
from coupon.validators import (DateTimeValidator, CountValidator, PriceValidator,
                               ProductValidator, PublishValidator, UserValidator,
                               ShopValidator, )


class CouponValidation:
    ALL_VALIDATORS = '__all__'

    def __call__(self, user, invoice, validators=ALL_VALIDATORS):
        self._user = user
        self._invoice = invoice
        self._validators = validators

    def get_validators(self):
        assert hasattr(self, '_validators'), 'You must call coupon object with user, invoice and validators first'
            
        if self._validators == self.ALL_VALIDATORS:
            self._validators = [
                DateTimeValidator(),
                CountValidator(self._user),
                PriceValidator(self._invoice),
                ProductValidator(self._invoice),
                PublishValidator(),
                UserValidator(self._user),
                ShopValidator(self._invoice)
            ]
        return self._validators



    def is_valid(self):
        # if hasattr(self, '_errors'):
            # return True if len(self._errors) == 0 else False

        # TODO: Check if this coupon is in an active invoice or not

        self._errors = []
        for validator in self.get_validators():
            try:
                validator(self)
            except ValidationError as exc:
                self._errors.append(exc.args)
        self.__get_final_price()

        return not self._errors

    def __get_final_price(self):
        assert hasattr(self, '_errors'), 'You should call .is_valid() on coupon first'
        self._final_price = None
        if len(self._errors) == 0:
            # Some calculations
            self.final_price = self.price

    def apply(self, order):
       if hasattr(self, '_final_price') and self._final_price is not None:
           self.usages.create(
               user=self._user,
               used_date=make_aware(datetime.now()),
               price_applied=self._final_price,
               # order=order,
           )

    @property
    def final_price(self):
        assert hasattr(self, '_final_price'), 'You should call .is_valid() on coupon first'
        return self._final_price

    @final_price.setter
    def final_price(self, value):
        assert hasattr(self, '_final_price'), 'You should call .is_valid() on coupon first'
        self._final_price = value

    @property
    def total_invoice_price(self):
        return self.invoice.total_price


    @property
    def errors(self):
        assert hasattr(self, '_errors'), 'You should call .is_valid() on coupon first'
        return self._errors


