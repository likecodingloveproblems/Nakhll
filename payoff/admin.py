from django.contrib import admin
from django.utils.timezone import localtime
import jdatetime
from payoff.models import Transaction, TransactionConfirmation, TransactionResult, TransactionReverse

# Register your models here.

admin.site.register(TransactionResult)
admin.site.register(TransactionReverse)
admin.site.register(TransactionConfirmation)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display=('id', 'amount', 'order_number', 'description', 'ipg', 'mobile',
                  'created_datetime_jalali', 'payoff_datetime_jalali', 'token',
                  'token_request_status', 'token_request_message',)
    list_filter=('ipg', 'created_datetime', )
    ordering=['-id', ]
    # search_fields = ('id', 'shop', 'payment_unique_id', )
    fields=('id', 'amount', 'order_number', 'description', 'ipg', 'mobile',
                'created_datetime_jalali', 'payoff_datetime_jalali', 'token',
                'token_request_status', 'token_request_message',)
    readonly_fields = fields

    def created_datetime_jalali(self, obj):
        datetime = localtime(obj.created_datetime)
        datetime = jdatetime.datetime.fromgregorian(datetime=datetime)
        return datetime.strftime('%Y/%m/%d %H:%M')
    created_datetime_jalali.short_description = 'زمان شروع'

    def payoff_datetime_jalali(self, obj):
        datetime = localtime(obj.payoff_datetime)
        datetime = jdatetime.datetime.fromgregorian(datetime=datetime)
        return datetime.strftime('%Y/%m/%d %H:%M')
    payoff_datetime_jalali.short_description = 'زمان پایان'



@admin.register(TransactionResult)
class TransactionResultAdmin(admin.ModelAdmin):
    list_display=('id', 'token', 'order_id', 'status', 'amount',
                  'created_datetime_jalali', 'trans_id' )
    list_filter=('status', 'created_datetime', 'amount')
    ordering=['-id', ]
    fields=('id', 'token', 'order_id', 'terminal_no', 'rrn', 'status', 'amount',
            'hash_card_number', 'created_datetime_jalali', 'discounted_amount', )
    readonly_fields = fields + ('trans_id', )

    def created_datetime_jalali(self, obj):
        datetime = localtime(obj.created_datetime)
        datetime = jdatetime.datetime.fromgregorian(datetime=datetime)
        return datetime.strftime('%Y/%m/%d %H:%M')
    created_datetime_jalali.short_description = 'زمان شروع'

    def trans_id(self, obj):
        return obj.transaction.id if hasattr(obj, 'transaction') and obj.transaction else ''
    trans_id.short_description = 'شماره تراکنش'

@admin.register(TransactionConfirmation)
class TransactionConfirmationAdmin(admin.ModelAdmin):
    list_display=('id', 'token', 'rrn', 'status', 'trans_res_id',
                  'created_datetime_jalali')
    list_filter=('status', 'created_datetime', 'amount')
    ordering=['-id', ]
    fields=('id', 'token', 'rrn', 'status', 'transaction_result',
            'card_number_masked', 'created_datetime_jalali',)
    readonly_fields = fields + ('trans_res_id', )

    def created_datetime_jalali(self, obj):
        datetime = localtime(obj.created_datetime)
        datetime = jdatetime.datetime.fromgregorian(datetime=datetime)
        return datetime.strftime('%Y/%m/%d %H:%M')
    created_datetime_jalali.short_description = 'زمان شروع'

    def trans_res_id(self, obj):
        return (
                obj.transaction_result.id
                if hasattr(obj, 'transaction_result') and obj.transaction_result
                else ''
            )
    trans_res_id.short_description = 'شماره تراکنش'
