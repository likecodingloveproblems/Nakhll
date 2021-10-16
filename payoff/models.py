from django.db import models
from django.db.models.deletion import SET_NULL
from django.utils.translation import ugettext as _
from django.core.serializers.json import DjangoJSONEncoder

# Create your models here.

class Transaction(models.Model):
    class Meta:
        verbose_name = _('تراکنش')
        verbose_name_plural = _('تراکنش‌ها')
    class IPGTypes(models.TextChoices):
        PEC = 'pec', _('درگاه پرداخت پارسیان')
        ZARIN = 'zarin', _('زرین پال')

    def __str__(self):
        return '{} - {} - {}'.format(self.id, self.amount, self.created_datetime)


    referrer_model = models.CharField(_('مدل ارجاع دهنده'), max_length=255, null=True, blank=True)
    referrer_app = models.CharField(_('ماژول ارجاع دهنده'), max_length=255, null=True, blank=True)
    amount = models.DecimalField(_('مبلغ (ریال)'), max_digits=15, decimal_places=0)
    order_number = models.CharField(_('شماره سفارش'), max_length=50, null=True, blank=True)
    created_datetime = models.DateTimeField(_('تاریخ ایجاد تراکنش'), auto_now_add=True)
    payoff_datetime = models.DateTimeField(_('تاریخ پرداخت'), null=True, blank=True)
    description = models.TextField(_('توضیحات'), null=True, blank=True)
    ipg = models.CharField(max_length=5, choices=IPGTypes.choices, default=IPGTypes.PEC, verbose_name=_('درگاه پرداخت'))
    token_request_status = models.CharField(max_length=50, verbose_name=_('وضعیت'), null=True)
    token = models.CharField(_('توکن'), max_length=200, null=True)
    token_request_message = models.TextField(_('پیام'), null=True)
    mobile = models.CharField(max_length=20, verbose_name=_('تلفن همراه'), null=True)

    def is_succeed(self):
        if self.result and self.result.status == 0 and self.result.rrn > 0:
            return True
        return False


class TransactionResult(models.Model):
    class Meta:
        verbose_name = _('نتیجه تراکنش')
        verbose_name_plural = _('نتایج تراکنش')
    transaction = models.OneToOneField(Transaction, verbose_name=_('تراکنش'), on_delete=models.CASCADE,
                                        related_name='result', null=True, blank=True)
    token = models.CharField(_('توکن'), max_length=200, null=True)
    order_id = models.CharField(_('شماره سفارش'), max_length=200, null=True)
    terminal_no = models.CharField(_('شماره پایانه'), max_length=200, null=True)
    rrn = models.CharField(_('RNN'), max_length=200, null=True)
    status = models.IntegerField(_('وضعیت'), default=200)
    hash_card_number = models.CharField(_('شماره کارت هش شده'), max_length=200, null=True)
    amount = models.CharField(_('مبلغ (ریال)'), max_length=200, null=True)
    discounted_amount = models.CharField(_('میزان تخفیف'), max_length=200, null=True)
    created_datetime = models.DateTimeField(_('تاریخ ایجاد تراکنش'), auto_now_add=True)



class TransactionConfirmation(models.Model):
    status = models.IntegerField(verbose_name='کد وضعیت')
    card_number_masked = models.CharField(verbose_name='شماره کارت خریدار', max_length=127)
    token = models.BigIntegerField(verbose_name='توکن')
    rrn = models.BigIntegerField(verbose_name='شماره یکتایی')
    transaction_result = models.ForeignKey(TransactionResult, verbose_name=_('نتیجه تراکنش'),
                                            null=True, blank=True, on_delete=models.SET_NULL)
    created_datetime = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    extra_data = models.JSONField(null=True, blank=True, encoder=DjangoJSONEncoder)

    class Meta:
        verbose_name = "تراکنش تایید شده پارسیان"
        verbose_name_plural = "تراکنش های تایید شده پارسیان"

class TransactionReverse(models.Model):
    status = models.IntegerField(verbose_name='کد وضعیت')
    token = models.BigIntegerField(verbose_name='توکن')
    message = models.CharField(verbose_name='پیام پارسیان', max_length=127, null=True, blank=True)
    transaction_result = models.ForeignKey(TransactionResult, verbose_name=_('نتیجه تراکنش'),
                                            null=True, blank=True, on_delete=models.SET_NULL)
    created_datetime = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    extra_data = models.JSONField(null=True, blank=True, encoder=DjangoJSONEncoder)

    class Meta:
        verbose_name = "تراکنش برگشتی پارسیان"
        verbose_name_plural = "تراکنش های برگشتی پارسیان"
