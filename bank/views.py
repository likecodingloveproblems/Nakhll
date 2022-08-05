from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework import permissions
from bank.constants import NAKHLL_ACCOUNT_ID, RequestTypes
from bank.models import Account, AccountRequest


class Withdraw(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        amount = request.POST.get('amount')
        account = Account.objects.get(user=request.user)
        account.withdraw(amount)
        return HttpResponse('درخواست تسویه با موفقیت ثبت شد.', status=201)


def buy_from_shop(buyer, shop, amount, description):
    buyer_account = Account.objects.get_or_create(user=buyer)[0]
    shop_manager_account = Account.objects.get_or_create(
        user=shop.FK_ShopManager)[0]
    AccountRequest.objects.create(
        from_account=buyer_account,
        to_account=shop_manager_account,
        value=amount,
        request_type=RequestTypes.BUY_FROM_SHOP,
        description=description,
    )


def deposit_user(user, request_type, amount, description):
    nakhll_account = Account.objects.get(pk=NAKHLL_ACCOUNT_ID)
    user_account = Account.objects.get_or_create(user=user)[0]
    AccountRequest.objects.create(
        from_account=nakhll_account,
        to_account=user_account,
        value=amount,
        request_type=request_type,
        description=description,
    )
