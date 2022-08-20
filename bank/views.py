from django.http import HttpResponse
from django.db import transaction
from rest_framework import permissions, views, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters import rest_framework as filters
from bank.constants import RequestTypes
from bank.permissions import UserHasWithdrawLimitBalance
from .filters import AccountRequestFilter
from bank.models import Account, AccountRequest, CoinPayment
from bank.serializers import AccountReadOnlySerializer, AccountRequestReportSerializer


class AccountViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AccountReadOnlySerializer

    def get_account(self, request):
        return Account.objects.get_or_create(user=self.request.user)[0]

    @action(detail=False, methods=['get'], name='get account info')
    def me(self, request):
        account = self.get_account(request)
        serializer = self.get_serializer(account)
        return Response(serializer.data)


class AccountRequestViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AccountRequestReportSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = AccountRequestFilter

    def get_queryset(self):
        account = Account.objects.get_or_create(user=self.request.user)[0]
        return AccountRequest.objects.all().filter_account_requests(account)

    @action(detail=False, methods=['get'], name='get account request report')
    def me(self, request):
        account_request = self.filter_queryset(self.get_queryset())
        account_request = account_request.request_coins_report(
        ).update_request_and_status_to_labels()
        serializer = self.get_serializer(account_request, many=True)
        return Response(serializer.data)


class Withdraw(views.APIView):
    permission_classes = [
        UserHasWithdrawLimitBalance,
        permissions.IsAuthenticated]

    def post(self, request):
        amount = request.POST.get('amount')
        account = Account.objects.get_or_create(user=request.user)[0]
        account.withdraw(amount)
        return HttpResponse('درخواست تسویه با موفقیت ثبت شد.', status=201)


def buy_from_nakhll(invoice, coin_amount, description):
    buyer = invoice.user
    buyer_account = Account.objects.get_or_create(user=buyer)[0]
    financial_account = Account.objects.financial_account
    account_request = AccountRequest.objects.create(
        from_account=buyer_account,
        to_account=financial_account,
        value=coin_amount,
        request_type=RequestTypes.BUY_FROM_NAKHLL,
        description=description,
    )
    CoinPayment.objects.create(
        invoice=invoice,
        account_request=account_request,
    )


def deposit_user(user, request_type, amount, description):
    with transaction.atomic():
        user_account = Account.objects.get_or_create(user=user)[0]
        user_account.deposit_from_bank(
            value=amount,
            request_type=request_type,
            description=description,
        )
