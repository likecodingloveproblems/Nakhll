from abc import ABC, abstractmethod
from django.utils import timezone

from bank.constants import NAKHLL_ACCOUNT_ID, RequestStatuses


class BaseAccountRequest(ABC):

    def __init__(self, account_request, user=None) -> None:
        self.check_user_permission(user)
        account_request.staff_user = user
        from bank.models import Account
        self.account_request = account_request
        self.from_account = Account.objects.select_for_update().get(
            pk=self.account_request.from_account_id)
        self.to_account = Account.objects.select_for_update().get(
            pk=self.account_request.to_account_id)
        self.cashable_value = 0

    @abstractmethod
    def validate(self):
        ''' validate request:
        1. from account balance is greater than or equal to request value
        (now we create this fields as positive integer fields, so django will create
        a constraint for them in DB, but we can send user friendly error messages by
        checking them in python too.)
        2. for withdraw, cashable amount is greater than or equal to request value
        it get one account request and confirm it'''

    def check_user_permission(self, user):
        '''this method can have extra checks, for example hard coded id of staff user.id'''


class CreateRequest(BaseAccountRequest):

    def create(self):
        self.validate()
        self.block_account_balance_and_cashable_amount()

    def block_account_balance_and_cashable_amount(self):
        self.from_account.blocked_balance += self.account_request.value
        if self.account_request.is_withdraw():
            self.cashable_value = self.account_request.value
        else:
            if self.from_account.non_cashable_balance < self.account_request.value:
                self.cashable_value = self.account_request.value - self.from_account.non_cashable_balance
        self.from_account.blocked_cashable_amount += self.cashable_value
        self.from_account.save()
        self.account_request.cashable_value = self.cashable_value
        self.account_request.save()

    def validate(self):
        if self.account_request.is_withdraw():
            if self.from_account.net_cashable_amount < self.account_request.value:
                raise Exception('not enough cashable amount')
        if self.from_account.net_balance < self.account_request.value:
            raise Exception('not enough balance')


class ConfirmRequest(BaseAccountRequest):

    def confirm(self):
        self.validate()
        self.__confirm()

    def __confirm(self):
        '''this will confirm request
        and update accounts balance and cashable amount
        and generate transactions
        '''
        self.__update_accounts_balance_and_cashable_amount()
        self.__generate_transactions()
        self.__update_account_request_status()

    def __update_accounts_balance_and_cashable_amount(self):
        '''update accounts balance and cashable amount
        '''
        self.__update_cashable_amount()
        self.__update_balance()
        self.from_account.save()
        self.to_account.save()

    def __update_cashable_amount(self):
        if self.account_request.is_withdraw():
            self.from_account.cashable_amount -= self.account_request.value
            self.from_account.blocked_cashable_amount -= self.account_request.value

    def __update_balance(self):
        self.from_account.blocked_balance -= self.account_request.value
        self.from_account.balance -= self.account_request.value
        if not self.from_account.id == NAKHLL_ACCOUNT_ID:
            self.from_account.cashable_amount -= self.account_request.cashable_value
        self.to_account.balance += self.account_request.value
        self.to_account.cashable_amount += self.account_request.deposit_cashable_value

    def __generate_transactions(self):
        self.__generate_withdraw_transaction()
        self.__generate_deposit_transaction()

    def __generate_withdraw_transaction(self):
        from bank.models import AccountTransaction
        AccountTransaction.objects.create(
            request=self.account_request,
            account=self.from_account,
            account_opposite=self.to_account,
            value=self.account_request.value * -1,
            cashable_value=self.account_request.cashable_value * -1,
            description=self.account_request.generate_withdraw_transaction_description(),
        )

    def __generate_deposit_transaction(self):
        from bank.models import AccountTransaction
        AccountTransaction.objects.create(
            request=self.account_request,
            account=self.to_account,
            account_opposite=self.from_account,
            value=self.account_request.value,
            cashable_value=self.account_request.deposit_cashable_value,
            description=self.account_request.generate_deposit_transaction_description(),
        )

    def __update_account_request_status(self):
        self.account_request.date_confirmed = timezone.now()
        self.account_request.status = RequestStatuses.CONFIRMED
        self.account_request.save()

    def validate(self):
        if self.from_account.blocked_balance < self.account_request.value:
            raise Exception(
                'Some thing went wrong, not enough blocked balance!')
        if self.account_request.is_withdraw():
            if self.from_account.blocked_cashable_amount < self.account_request.value:
                raise Exception(
                    'Some thing went wrong, not enough blocked cashable amount!')


class RejectRequest(BaseAccountRequest):

    def reject(self):
        self.__reject()

    def __reject(self):
        self.__update_accounts_balance_and_cashable_amount()
        self.__update_account_request_status()

    def __update_accounts_balance_and_cashable_amount(self):
        self.__update_blocked_balance()
        self.__update_blocked_cashable_amount()
        self.from_account.save()

    def __update_blocked_balance(self):
        self.from_account.blocked_balance -= self.account_request.value

    def __update_blocked_cashable_amount(self):
        if self.account_request.is_withdraw():
            self.from_account.blocked_cashable_amount -= self.account_request.value

    def __update_account_request_status(self):
        self.account_request.date_rejected = timezone.now()
        self.account_request.status = RequestStatuses.REJECTED
        self.account_request.save()

    def validate(self):
        pass
