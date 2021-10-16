from django.contrib import admin
from accounting_new.models import Invoice, InvoiceItem
import jdatetime

# Register your models here.
admin.site.register(InvoiceItem)


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display=('id', 'FactorNumber', 'user', 'status',  'final_price', 'post_price',
                    'mobile_number', 'created_datetime_jalali',  )
    list_filter=('status','user',)
    readonly_fields = ('id',)
    ordering=['-created_datetime', ]
    search_fields = ('id', 'FactorNumber')

    def mobile_number(self, obj):
        if obj.address_json:
            return obj.address_json['receiver_mobile_number']
        return obj.user.User_Profile.MobileNumber
    mobile_number.short_description = 'شماره همراه'

    def created_datetime_jalali(self, obj):
        return jdatetime.datetime.fromgregorian(datetime=obj.created_datetime).strftime('%Y/%m/%d %H:%M:%S')
    created_datetime_jalali.short_description = 'تاریخ ثبت'

    def final_price(self, obj):
        return f'{obj.final_price:,} ریال'
    final_price.short_description = 'قیمت نهایی'

    def post_price(self, obj):
        return f'{obj.logistic_price:,} ریال'
    post_price.short_description = 'هزینه ارسال'