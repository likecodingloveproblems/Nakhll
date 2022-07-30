from django.db import models
from django.utils.translation import ugettext as _
from django.core.serializers.json import DjangoJSONEncoder


class Transaction(models.Model):
    """Data that is going to be sent to the IPG.

    This data must be the final processed data that is going to be sent to the IPG.
    Any change or process between creating this model and sending it to the IPG may 
    cause data inconsistency issue.
    Note: referrer_model and referrer_app are use to identify the model that created this transaction.
    each referrer may want to do some actions when the purchase process is completed, either by success or failure.
    To handle this situation, referrer model should have two methods that are called when the purchase process is completed:
     - complete_payment(transaction_result): this method is called when the purchase process is completed successfully.
     - revert_payment(transaction_result): this method is called when the purchase process is failed.
    As an example, referrer model can be an invoice model, which has these two methods:
     - :attr:`invoice.models.Invoice.complete_payment`: responsible for reducing stock, notifying the customer, etc.
     - :attr:`invoice.models.Invoice.revert_payment`: responsible for filling cart from invoice, unseting coupons, etc.
    """
    class Meta:
        verbose_name = _('تراکنش')
        verbose_name_plural = _('تراکنش‌ها')

    class IPGTypes(models.TextChoices):
        PEC = 'pec', _('درگاه پرداخت پارسیان')
        SEP = 'sep', _('درگاهپرداخت صادرات')

    def __str__(self):
        return '{} - {} - {}'.format(self.id, self.amount, self.created_datetime)

    referrer_model = models.CharField(_('مدل ارجاع دهنده'), max_length=255, null=True, blank=True)
    referrer_app = models.CharField(_('ماژول ارجاع دهنده'), max_length=255, null=True, blank=True)
    amount = models.DecimalField(_('مبلغ (ریال)'), max_digits=15, decimal_places=0)
    order_number = models.BigIntegerField(_('شماره سفارش'), null=True, blank=True)
    created_datetime = models.DateTimeField(_('تاریخ ایجاد تراکنش'), auto_now_add=True)
    payoff_datetime = models.DateTimeField(_('تاریخ پرداخت'), null=True, blank=True)
    description = models.TextField(_('توضیحات'), null=True, blank=True)
    ipg = models.CharField(max_length=5, choices=IPGTypes.choices, default=IPGTypes.PEC, verbose_name=_('درگاه پرداخت'))
    token_request_status = models.CharField(max_length=50, verbose_name=_('وضعیت'), null=True)
    token = models.CharField(_('توکن'), max_length=200, null=True)
    token_request_message = models.TextField(_('پیام'), null=True)
    mobile = models.CharField(max_length=20, verbose_name=_('تلفن همراه'), null=True)


class TransactionResult(models.Model):
    """Data that is received from the IPG before any processing.

    The fist step after receiving data from the IPG must be saving it to this model in order to use as a reference.
    This data must be the data that is received from the IPG before any processing. Any changes between receiving 
    this data and saving it to database may cause data inconsistency issue. So do any changes to need after saving
    this data to database.
    Note: The relation between Transaction and TransactionResult is nullable, which means we can have TransactionResult
    without any transaction. This is because we may have some data that is received from any endpoint to our callback
    url and we may want to investigate it. So first we need to save this data to database and then we try to link it
    to Transaction if it's possible using :attr:`Transaction.order_number` and :attr:`TransactionResult.order_id`.
    """
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
    extra_data = models.JSONField(verbose_name=_('سایر اطلاعات'), null=True, blank=True)
    ref_number = models.CharField(_('شماره مرجع'), max_length=200, null=True, blank=True)


class TransactionConfirmation(models.Model):
    """Information of confirmation request to IPG after all processing.

    Some IPGs require a confirmation request from our server to insure that our server has received the data
    or they will revert the payment after some time. This model is used to save the information of the confirmation
    request.
    """
    status = models.IntegerField(verbose_name='کد وضعیت')
    card_number_masked = models.CharField(verbose_name='شماره کارت خریدار', max_length=127, blank=True)
    token = models.BigIntegerField(verbose_name='توکن', blank=True, null=True)
    rrn = models.BigIntegerField(verbose_name='شماره یکتایی', blank=True, null=True)
    transaction_result = models.ForeignKey(TransactionResult, verbose_name=_('نتیجه تراکنش'),
                                           null=True, blank=True, on_delete=models.SET_NULL)
    created_datetime = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    extra_data = models.JSONField(null=True, blank=True, encoder=DjangoJSONEncoder)

    class Meta:
        verbose_name = "تراکنش تایید شده پارسیان"
        verbose_name_plural = "تراکنش های تایید شده پارسیان"


class TransactionReverse(models.Model):
    """Information of reverse request to IPG after all processing.

    Sometimes we need to reverse a transaction that has been paid due to some invalidity situations.
    This model is used to save the information of the reverse request before sending it to IPG.
    """
    status = models.IntegerField(verbose_name='کد وضعیت')
    token = models.BigIntegerField(verbose_name='توکن', null=True, blank=True)
    message = models.CharField(verbose_name='پیام پارسیان', max_length=127, null=True, blank=True)
    transaction_result = models.ForeignKey(TransactionResult, verbose_name=_('نتیجه تراکنش'),
                                           null=True, blank=True, on_delete=models.SET_NULL)
    created_datetime = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    extra_data = models.JSONField(null=True, blank=True, encoder=DjangoJSONEncoder)

    class Meta:
        verbose_name = "تراکنش برگشتی پارسیان"
        verbose_name_plural = "تراکنش های برگشتی پارسیان"
