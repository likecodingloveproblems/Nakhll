from datetime import datetime
from django.utils.timezone import make_aware
from rest_framework.validators import ValidationError
from coupon.validators import (BudgetValidator, DateTimeValidator, MaxCountValidator, MaxUserCountValidator, 
                               ProductValidator, AvailableValidator, UserValidator, PriceValidator,
                               ShopValidator, )
from coupon.exceptions import (AvailableException, BudgetException, CountException, UserException,
                               ShopException, DateTimeException, MaxCountException,
                               MaxUserCountException, PriceException, ProductException)



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



    def is_valid(self, invoice, validators=ALL_VALIDATORS):
        self._user = invoice.cart.user
        self._invoice = invoice
        self._validators = validators
        # if hasattr(self, '_errors'):
            # return True if len(self._errors) == 0 else False

        # TODO: Check if this coupon is in an active invoice or not

        self._errors = []
        for validator in self._get_validators():
            try:
                validator(self)
            except ProductException:
                self._errors.append('ProductException')
            except PriceException:
                self._errors.append('PriceException')
            except MaxUserCountException:
                self._errors.append('MaxUserCountException')
            except MaxCountException:
                self._errors.append('MaxCountException')
            except DateTimeException:
                self._errors.append('DateTimeException')
            except ShopException:
                self._errors.append('ShopException')
            except UserException:
                self._errors.append('UserException')
            except CountException:
                self._errors.append('CountException')
            except BudgetException:
                self._errors.append('BudgetException')
            except AvailableException:
                self._errors.append('AvailableException')
            except ValidationError as exc:
                self._errors.append(exc.args)
        return not self._errors

    def get_final_price(self):
        assert hasattr(self, '_errors'), 'You should call .is_valid() on coupon first'
        self._final_price = None
        if len(self._errors) == 0:
            # TODO: Some calculations
            self.final_price = self.price

    def apply(self, invoice):
       if hasattr(self, '_final_price') and self._final_price is not None:
           self.usages.create(
               user=self._user,
               used_date=make_aware(datetime.now()),
               price_applied=self._final_price,
               invoice=invoice,
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
    def errors(self):
        assert hasattr(self, '_errors'), 'You should call .is_valid() on coupon first'
        return self._errors


