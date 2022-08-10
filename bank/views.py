from django.http import HttpResponse
from rest_framework import permissions, views, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from bank.constants import RequestTypes
from bank.models import Account, AccountRequest, CoinPayment
from bank.serializers import AccountReadOnlySerializer


class AccountViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AccountReadOnlySerializer

    def get_object(self, request):
        return Account.objects.get(user=request.user)

    @action(detail=False, methods=['get'], name='get account info')
    def me(self, request):
        account = self.get_object(request)
        serializer = self.get_serializer(account)
        return Response(serializer.data)


class Withdraw(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        amount = request.POST.get('amount')
        account = Account.objects.get(user=request.user)
        account.withdraw(amount)
        return HttpResponse('درخواست تسویه با موفقیت ثبت شد.', status=201)


def buy_from_nakhll(invoice, coin_amount, description):
    buyer = invoice.user
    buyer_account = Account.objects.get_or_create(user=buyer)[0]
    nakhll_account = Account.objects.nakhll_account
    account_request = AccountRequest.objects.create(
        from_account=buyer_account,
        to_account=nakhll_account,
        value=coin_amount,
        request_type=RequestTypes.BUY_FROM_NAKHLL,
        description=description,
    )
    CoinPayment.objects.create(
        invoice=invoice,
        account_request=account_request,
    )


def deposit_user(user, request_type, amount, description):
    user_account = Account.objects.get_or_create(user=user)[0]
    user_account.deposit_from_nakhll(
        value=amount,
        request_type=request_type,
        description=description,
    )
