from django.db import models
from django.utils.translation import ugettext as _

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
    reversed_status = models.CharField(_('وضعیت درخواست بازگشت وجه'), max_length=100, null=True, blank=True)
    reversed_message = models.CharField(_('نتیجه درخواست بازگشت وجه'), max_length=200, null=True, blank=True)
    reversed_token = models.CharField(_('توکن درخواست بازگشت وجه'), max_length=20, null=True, blank=True)

