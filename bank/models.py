from django.core import validators, exceptions
from django.db import models, transaction
from django.db.models import F, Q, Sum, CheckConstraint, When, Case
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from django_jalali.db import models as jmodels
import pgtrigger
from bank.account_requests import ConfirmRequest, CreateRequest, RejectRequest
from bank.constants import (
    AUTOMATIC_CONFIRM_REQUEST_TYPES,
    FUND_ACCOUNT_ID,
    COIN_RIAL_RATIO,
    FINANCIAL_ACCOUNT_ID,
    SYSTEMIC_ACCOUNTS_ID_UPPER_LIMIT,
    RequestStatuses,
    RequestTypes,
    CASHABLE_REQUEST_TYPES,
)
from bank.managers import (
    AccountManager,
    AccountRequestManager,
    BuyFromNakhllRequestManager,
    DepositRequestManager,
    WithdrawRequestManager,
    FinancialToFundRequestManager,
)


class CoinMintBurn(models.Model):

    '''Coin Burn Logic
    on create it will subtract value from balance of bank account
    but we must decide on coin burn we subtract from bank balance or net balance
    if we let user to subtract from balance some of account request will be blocked
    on the other way if we let user to subtract from net balance, user can't burn coins that are blocked
    delete and update are not allowed
    '''
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name='سوزاننده سکه')
    value = models.PositiveIntegerField(
        verbose_name='مقدار', validators=[
            validators.MinValueValidator(1)])
    is_mint = models.BooleanField(verbose_name='آیا ضرب سکه است؟', default=True)
    description = models.TextField(verbose_name='توضیحات')
    date_created = jmodels.jDateTimeField(
        auto_now_add=True, verbose_name='تاریخ ایجاد')

    class Meta:
        verbose_name = _("MintBurn")
        verbose_name_plural = _("MintBurns")
        triggers = [
            pgtrigger.Protect(
                name='protect_from_deletes_and_updates',
                operation=(pgtrigger.Delete | pgtrigger.Update)
            )
        ]

    def __str__(self):
        return f'{self.user} - {self.value} - {self.description} - {str(self.date_created)}'

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        '''coin only can be transferred to account'''
        if self.pk is not None:
            raise Exception('you can\'t update this model.')
        from bank.models import Account
        with transaction.atomic():
            self.validate()
            fund_account = Account.objects.fund_account_for_update
            fund_account.balance += self.get_value()
            fund_account.save()
            return super().save(force_insert, force_update, using, update_fields)

    def get_value(self):
        if self.is_mint:
            return self.value
        else:
            return -self.value

    def validate(self):
        from bank.models import Account
        if not self.is_mint:
            # check total balance of coins minted.
            total_coins = CoinMintBurn.objects.annotate(
                signed_value=Case(
                    When(is_mint=False, then=-1 * F('value')),
                    default=F('value'),
                    output_field=models.IntegerField()
                ),
            ).aggregate(Sum('signed_value'))['signed_value__sum']
            if total_coins - self.value < 0:
                raise exceptions.ValidationError(
                    'you can\'t burn more coins than minted.')

            if self.value > Account.objects.fund_account_for_update.net_balance:
                raise exceptions.ValidationError('not enough cashable amount')


class Account(models.Model):
    user = models.ForeignKey(
        User,
        unique=True,
        null=True,
        on_delete=models.PROTECT)
    balance = models.PositiveIntegerField(default=0)
    blocked_balance = models.PositiveIntegerField(default=0)
    cashable_amount = models.PositiveIntegerField(default=0)
    blocked_cashable_amount = models.PositiveIntegerField(default=0)
    date_created = jmodels.jDateTimeField(auto_now_add=True)
    objects = AccountManager()

    class Meta:
        verbose_name = _("Account")
        verbose_name_plural = _("Accounts")
        constraints = [
            CheckConstraint(
                check=Q(~Q(pk__lt=SYSTEMIC_ACCOUNTS_ID_UPPER_LIMIT) & ~Q(user=None)) |
                Q(pk__lt=SYSTEMIC_ACCOUNTS_ID_UPPER_LIMIT, user=None),
                name='only_systemic_accounts_can_have_null_user'),
            CheckConstraint(
                check=Q(balance__gte=F('blocked_balance')),
                name='balance_is_more_than_or_equal_to_blocked_balance'),
            CheckConstraint(
                check=Q(cashable_amount__gte=F('blocked_cashable_amount')),
                name='cashable_amount_is_more_than_or_equal_to_blocked_cashable_amount'),
            CheckConstraint(
                check=Q(balance__gte=F('cashable_amount')),
                name='balance_is_more_than_or_equal_to_cashable_amount'),
            CheckConstraint(
                check=Q(blocked_balance__gte=F('blocked_cashable_amount')),
                name='blocked_balance_is_more_than_or_equal_to_blocked_cashable_amount')]
        triggers = [
            pgtrigger.Protect(
                name='protect_from_deletes',
                operation=pgtrigger.Delete
            )
        ]

    def __str__(self):
        if self.id == FUND_ACCOUNT_ID:
            return 'صندوق'
        elif self.id == FINANCIAL_ACCOUNT_ID:
            return 'حساب مالی'
        else:
            return f'{self.user.username}-{self.user.first_name} {self.user.last_name}'

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        '''coin only can be transferred to account'''
        if self.pk is None:
            self.balance = self.cashable_amount = self.blocked_balance = self.blocked_cashable_amount = 0
        return super().save(force_insert, force_update, using, update_fields)

    @property
    def net_balance(self):
        return self.balance - self.blocked_balance

    @property
    def net_cashable_amount(self):
        return self.cashable_amount - self.blocked_cashable_amount

    @property
    def non_cashable_balance(self):
        return self.balance - self.cashable_amount

    @property
    def requests_coin_report(self):
        return AccountRequest.objects.account_request_coins_report(self)

    @property
    def is_systemic(self):
        return self.pk <= SYSTEMIC_ACCOUNTS_ID_UPPER_LIMIT or self.user is None

    def withdraw(self, amount=None):
        amount = amount if amount else self.cashable_amount
        AccountRequest.objects.create(
            from_account=self,
            to_account=Account.objects.financial_account,
            value=amount,
            request_type=RequestTypes.WITHDRAW,
            description='withdraw',
        )

    def deposit_from_bank(self, value, request_type, description):
        """Deposit to account from bank account"""
        AccountRequest.objects.create(
            from_account=Account.objects.fund_account,
            to_account=self,
            value=value,
            request_type=request_type,
            description=description,
        )


class AccountRequest(models.Model):
    from_account = models.ForeignKey(
        Account,
        verbose_name='حساب مبدا',
        on_delete=models.PROTECT,
        related_name='from_account_request')
    to_account = models.ForeignKey(
        Account,
        verbose_name='حساب مقصد',
        on_delete=models.PROTECT,
        related_name='to_account_request')
    staff_user = models.ForeignKey(
        User,
        verbose_name='کارمند تایید/رد کننده',
        on_delete=models.PROTECT,
        null=True,
        blank=True)
    value = models.PositiveIntegerField(
        verbose_name='مقدار سکه', validators=[validators.MinValueValidator(1)])
    request_type = models.IntegerField(
        verbose_name='نوع درخواست',
        choices=RequestTypes.choices)
    description = models.TextField(verbose_name='توضیحات')
    status = models.IntegerField(
        verbose_name='وضعیت',
        choices=RequestStatuses.choices,
        default=RequestStatuses.PENDING)
    cashable_value = models.IntegerField(
        verbose_name='مقدار قابل تسویه از حساب مبدا', blank=True)
    date_created = jmodels.jDateTimeField(
        verbose_name='تاریخ ایجاد', auto_now_add=True)
    date_confirmed = jmodels.jDateTimeField(
        verbose_name='تاریخ تایید', null=True, blank=True)
    date_rejected = jmodels.jDateTimeField(
        verbose_name='تاریخ رد', null=True, blank=True)
    objects = AccountRequestManager()

    class Meta:
        verbose_name = _("AccountRequest")
        verbose_name_plural = _("AccountRequest")
        constraints = [
            CheckConstraint(
                check=Q(
                    Q(
                        status__in=[
                            RequestStatuses.CONFIRMED,
                            RequestStatuses.REJECTED]) & ~Q(
                        staff_user=None)) |
                Q(
                    Q(staff_user=None) & Q(Q(status=RequestStatuses.PENDING) |
                                           Q(request_type__in=AUTOMATIC_CONFIRM_REQUEST_TYPES),
                                           )
                ),
                name='staff_user_check_for_different_statuses'),
            CheckConstraint(
                check=~Q(from_account=F('to_account')),
                name='from_account_must_not_be_equal_to_to_account'
            ),
            CheckConstraint(
                check=Q(
                    Q(
                        request_type__in=[
                            RequestTypes.DEPOSIT,
                            RequestTypes.REFERRER_VISIT_REWARD,
                            RequestTypes.REFERRER_SIGNUP_REWARD,
                            RequestTypes.REFERRER_PURCHASE_REWARD,
                            RequestTypes.PURCHASE_REWARD,
                        ],
                        from_account=FUND_ACCOUNT_ID,
                        to_account__gt=SYSTEMIC_ACCOUNTS_ID_UPPER_LIMIT) |
                    Q(
                        request_type__in=[RequestTypes.WITHDRAW, RequestTypes.BUY_FROM_NAKHLL],
                        from_account__gt=SYSTEMIC_ACCOUNTS_ID_UPPER_LIMIT,
                        to_account=FINANCIAL_ACCOUNT_ID) |
                    Q(
                        request_type=RequestTypes.FINANCIAL_TO_FUND,
                        from_account=FINANCIAL_ACCOUNT_ID,
                        to_account=FUND_ACCOUNT_ID
                    )
                ),
                name='check_request_types_requirements'
            ),
        ]
        triggers = [
            pgtrigger.Protect(
                name='protect_from_deletes',
                operation=pgtrigger.Delete),
            pgtrigger.Protect(
                name='protect_confirmed_or_rejected_from_updates',
                operation=pgtrigger.Update,
                condition=pgtrigger.Q(
                    old__status__in=(
                        RequestStatuses.CONFIRMED,
                        RequestStatuses.REJECTED))),
            pgtrigger.Protect(
                name='create_official_interface',
                operation=pgtrigger.Insert
            ),
            pgtrigger.Protect(
                name='confirm_reject_official_interface',
                operation=pgtrigger.Update
            )]
        permissions = [
            ('confirm_accountrequest', _('Can confirm account request!')),
            ('reject_accountrequest', _('Can reject account request!')),
            ('create_accountrequest', _('Can create account request.'))
        ]

    def __str__(self):
        return f'{self.from_account} - {self.to_account} - {self.value}'

    @property
    def deposit_cashable_value(self):
        return self.value if self.request_type in CASHABLE_REQUEST_TYPES else 0

    @pgtrigger.ignore("bank.AccountRequest:create_official_interface")
    def create(self):
        with transaction.atomic():
            return CreateRequest(self).create()

    @pgtrigger.ignore("bank.AccountRequest:confirm_reject_official_interface")
    def confirm(self, user=None):
        with transaction.atomic():
            return ConfirmRequest(self, user).confirm()

    @pgtrigger.ignore("bank.AccountRequest:confirm_reject_official_interface")
    def reject(self, user):
        with transaction.atomic():
            return RejectRequest(self, user).reject()

    def is_withdraw(self):
        '''we can check it by to account, so I create this method to have flexibility in statuses'''
        return self.request_type == RequestTypes.WITHDRAW

    def generate_withdraw_transaction_description(self):
        return f'{self.from_account} - {self.to_account} - {self.value}'

    def generate_deposit_transaction_description(self):
        return f'{self.to_account} - {self.from_account} - {self.value}'


class AccountTransaction(models.Model):
    request = models.ForeignKey(
        'AccountRequest', on_delete=models.PROTECT)
    account = models.ForeignKey(
        Account,
        on_delete=models.PROTECT,
        related_name='account_transaction')
    account_opposite = models.ForeignKey(
        Account,
        on_delete=models.PROTECT,
        related_name='account_opposite_transaction')
    value = models.IntegerField()
    cashable_value = models.IntegerField()
    description = models.CharField(max_length=1023)
    date_created = jmodels.jDateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("AccountTransaction")
        verbose_name_plural = _("AccountTransaction")
        triggers = [
            pgtrigger.Protect(
                name='protect_from_updates_and_deleted',
                operation=(
                    pgtrigger.Update | pgtrigger.Delete))]

    def __str__(self):
        return f'{self.account} - {self.account_opposite} - {self.value} - {self.date_created}'


class CoinPayment(models.Model):
    invoice = models.ForeignKey(
        "invoice.Invoice",
        verbose_name=_("invoice"),
        on_delete=models.PROTECT)
    account_request = models.ForeignKey(
        AccountRequest,
        verbose_name=_("account request"),
        on_delete=models.PROTECT,
        unique=True)
    price_amount = models.DecimalField(
        verbose_name=_('Rial amount paid'),
        max_digits=12, decimal_places=0, default=0)
    date_created = jmodels.jDateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("CoinPayment")
        verbose_name_plural = _("CoinPayments")

    def __str__(self):
        return f'invoice:{self.invoice}, account request:{self.account_request}'

    def save(self, *args, **kwargs):
        self.price_amount = self.account_request.value * COIN_RIAL_RATIO
        super().save(*args, **kwargs)


class DepositRequest(AccountRequest):
    objects = DepositRequestManager()

    class Meta:
        proxy = True

    def __str__(self):
        return f'Deposit to {self.to_account}: {self.value}'

    def create(self, *args, **kwargs):
        self.from_account = Account.objects.fund_account
        self.request_type = RequestTypes.DEPOSIT
        super().create()

    def clean(self) -> None:
        if self.to_account.is_systemic:
            raise exceptions.ValidationError(
                "واریز فقط به حساب کاربران می تواند انجام شود.")


class WithdrawRequest(AccountRequest):
    objects = WithdrawRequestManager()

    class Meta:
        proxy = True

    def __str__(self):
        return f'درخواست تسویه از {self.from_account}: {self.value}'

    def create(self, *args, **kwargs):
        self.to_account = Account.objects.financial_account
        self.request_type = RequestTypes.WITHDRAW
        super().create()

    def clean(self) -> None:
        if self.from_account.is_systemic:
            raise exceptions.ValidationError(
                "فقط حساب های کاربری می توانند تسویه کنند.")


class BuyFromNakhllRequest(AccountRequest):
    objects = BuyFromNakhllRequestManager()

    class Meta:
        proxy = True

    def __str__(self):
        return f'خرید از نخل توسط {self.from_account}: {self.value}'

    def create(self, *args, **kwargs):
        self.to_account = Account.objects.financial_account
        self.request_type = RequestTypes.BUY_FROM_NAKHLL
        super().create()

    def clean(self) -> None:
        if self.from_account.is_systemic:
            raise exceptions.ValidationError(
                "فقط حساب های کاربری می توانند از نخل خرید کنند.")


class FinancialToFundRequest(AccountRequest):
    objects = FinancialToFundRequestManager()

    class Meta:
        proxy = True

    def __str__(self):
        return f'انتقال از حساب مالی به حساب نخل: {self.value}'

    def create(self, *args, **kwargs):
        self.from_account = Account.objects.financial_account
        self.to_account = Account.objects.fund_account
        self.request_type = RequestTypes.FINANCIAL_TO_FUND
        super().create()
