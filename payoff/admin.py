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

