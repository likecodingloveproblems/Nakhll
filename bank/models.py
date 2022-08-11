from django.core import validators, exceptions
from django.db import models, transaction
from django.db.models import F, Q, Sum, CheckConstraint, When, Case
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from django_jalali.db import models as jmodels
import pgtrigger
from bank.account_requests import ConfirmRequest, CreateRequest, RejectRequest
from bank.constants import (
    COIN_RIAL_RATIO,
    NAKHLL_ACCOUNT_ID,
    RequestStatuses,
    RequestTypes,
    CASHABLE_REQUESTS_TYPES,
)
from bank.managers import (
    AccountManager,
    AccountRequestManager,
)


class CoinMintBurn(models.Model):

    '''Coin Burn Logic
    on create it will subtract value from balance of nakhll account
    but we must decide on coin burn we subtract from nakhll balance or net balance
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
    is_mint = models.BooleanField(verbose_name='آیا ضرب سکه است؟')
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
            nakhll_account = Account.objects.nakhll_account_for_update
            nakhll_account.balance += self.get_value()
            nakhll_account.save()
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

            if self.value > Account.objects.nakhll_account_for_update.net_balance:
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
                check=Q(~Q(pk=NAKHLL_ACCOUNT_ID) & ~Q(user=None)) |
                Q(pk=NAKHLL_ACCOUNT_ID, user=None),
                name='only_nakhll_account_can_have_null_user'),
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
        return f'{self.user} - balance:{self.balance} - cashable amount:{self.cashable_amount}'

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

    def withdraw(self, amount=None):
        amount = amount if amount else self.cashable_amount
        AccountRequest.objects.create(
            from_account=self,
            to_account=Account.objects.nakhll_account,
            value=amount,
            request_type=RequestTypes.WITHDRAW,
            description='withdraw',
        )

    def deposit_from_nakhll(self, value, request_type, description):
        """Deposit to account from nakhll account"""
        AccountRequest.objects.create(
            from_account=Account.objects.nakhll_account,
            to_account=self,
            value=value,
            request_type=request_type,
            description=description,
        )


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


class AccountRequest(models.Model):
    from_account = models.ForeignKey(
        Account,
        on_delete=models.PROTECT,
        related_name='from_account_request')
    to_account = models.ForeignKey(
        Account,
        on_delete=models.PROTECT,
        related_name='to_account_request')
    staff_user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        blank=True)
    value = models.PositiveIntegerField()
    request_type = models.IntegerField(choices=RequestTypes.choices)
    description = models.TextField()
    status = models.IntegerField(
        choices=RequestStatuses.choices,
        default=RequestStatuses.PENDING)
    cashable_value = models.IntegerField(blank=True)
    date_created = jmodels.jDateTimeField(auto_now_add=True)
    date_confirmed = jmodels.jDateTimeField(null=True, blank=True)
    date_rejected = jmodels.jDateTimeField(null=True, blank=True)
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
                        staff_user=None)) | Q(
                            staff_user=None,
                            status=RequestStatuses.PENDING),
                name='staff_user_check_for_different_statuses'),
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
                        RequestStatuses.REJECTED)))]
        permissions = [
            ('confirm_accountrequest', _('Can confirm account request!')),
            ('reject_accountrequest', _('Can reject account request!')),
            ('create_accountrequest', _('Can create account request.'))
        ]

    def __str__(self):
        return f'{self.from_account} - {self.to_account} - {self.value}'

    @property
    def deposit_cashable_value(self):
        return self.value if self.request_type in CASHABLE_REQUESTS_TYPES else 0

    def create(self):
        with transaction.atomic():
            CreateRequest(self).create()

    def confirm(self, user):
        with transaction.atomic():
            ConfirmRequest(self, user).confirm()

    def reject(self, user):
        with transaction.atomic():
            RejectRequest(self, user).reject()

    def is_withdraw(self):
        '''we can check it by to account, so I create this method to have flexibility in statuses'''
        return self.request_type == RequestTypes.WITHDRAW

    def generate_withdraw_transaction_description(self):
        return f'{self.from_account} - {self.to_account} - {self.value}'

    def generate_deposit_transaction_description(self):
        return f'{self.to_account} - {self.from_account} - {self.value}'


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
        return f'cart:{self.cart}, account request:{self.account_request}'

    def save(self, *args, **kwargs):
        self.price_amount = self.account_request.value * COIN_RIAL_RATIO
        super().save(*args, **kwargs)
