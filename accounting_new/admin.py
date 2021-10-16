import jdatetime, json
from django.contrib import admin
from accounting_new.models import Invoice, InvoiceItem
from coupon.models import CouponUsage

# Register your models here.
class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    fields = ('name', 'count', 'price_with_discount', 'price_without_discount', 'weight', 'shop_name', )
    extra = 0
    # readonly_fields = fields

class CouponUsageInline(admin.TabularInline):
    model = CouponUsage
    extra = 0
    fields = ('coupon', 'price_applied', )
    # readonly_fields = ('coupon', 'used_count', 'used_at', )

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display=('id', 'FactorNumber', 'user', 'status',  'final_price', 'post_price', 'coupons_total_price',
                    'receiver_mobile_number', 'receiver_full_name', 'created_datetime_jalali',  )
    list_filter=('status','user',)
    readonly_fields = ('id',)
    ordering=['-created_datetime', ]
    search_fields = ('id', 'FactorNumber')
    inlines = [InvoiceItemInline, CouponUsageInline]

    def receiver_mobile_number(self, obj):
        user_mobile_number = obj.user.User_Profile.MobileNumber
        if obj.address_json:
            address = json.loads(obj.address_json)
            return address.get('receiver_mobile_number', user_mobile_number)
        return user_mobile_number
    receiver_mobile_number.short_description = 'شماره همراه'

    def receiver_full_name(self, obj):
        if obj.address_json:
            address = json.loads(obj.address_json)
            return address.get('receiver_full_name', '')
        return ''
    receiver_full_name.short_description = 'نام گیرنده'

    def created_datetime_jalali(self, obj):
        return jdatetime.datetime.fromgregorian(datetime=obj.created_datetime).strftime('%Y/%m/%d %H:%M:%S')
    created_datetime_jalali.short_description = 'تاریخ ثبت'

    def final_price(self, obj):
        return f'{obj.final_price:,} ریال'
    final_price.short_description = 'قیمت نهایی'

    def post_price(self, obj):
        return f'{obj.logistic_price:,} ریال'
    post_price.short_description = 'هزینه ارسال'

    def coupons_total_price(self, obj):
        return f'{obj.coupons_total_price:,} ریال'
    coupons_total_price.short_description = 'هزینه کوپن'