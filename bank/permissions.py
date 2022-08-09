from django.utils.translation import ugettext as _
from rest_framework.permissions import BasePermission
from bank.constants import WITHDRAW_BALANCE_LIMIT
from bank.models import Account


class UserHasWithdrawLimitBalance(BasePermission):
    """Check if user is the owner of the cart"""
    message = f"شما باید حداقل {WITHDRAW_BALANCE_LIMIT} سکه داشته باشید تا بتوانید درخواست تسویه بدهید."

    def has_permission(self, request, view):
        account = Account.objects.get_or_create(user=request.user)[0]
        result = account.balance >= WITHDRAW_BALANCE_LIMIT
        return result
