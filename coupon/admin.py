from django.contrib import admin
from django.utils.timezone import localtime
import jdatetime
from .models import Coupon, CouponUsage, CouponConstraint

# Register your models here.

class CouponConstraintInline(admin.StackedInline):
    model = CouponConstraint
    # fields = ('name', 'count', 'price_with_discount', 'price_without_discount', 'weight', 'shop_name', 'barcode')
    extra = 0

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'code', 'amount_display', 'creator', 'available', 'created_at_jalali')
    readonly_fields = ('creator', 'created_at', 'updated_at')
    ordering=['-created_at', ]
    list_filter = ('available', 'created_at')
    inlines = [CouponConstraintInline]

    def amount_display(self, obj):
        if obj.amount:
            return f'{obj.amount:,} ریال'
        max_amount = obj.max_amount
        percentage = obj.presentage
        return f'{percentage}% (max: {max_amount:,})'
    amount_display.short_description = 'مقدار کوپن'

    def created_at_jalali(self, obj):
        localtime_time = localtime(obj.created_at)
        return jdatetime.datetime.fromgregorian(datetime=localtime_time).strftime('%Y/%m/%d %H:%M:%S')
    created_at_jalali.short_description = 'تاریخ ایجاد'
    created_at_jalali.admin_order_field = 'created_at'

    def save_model(self, request, obj, form, change):
        obj.creator = request.user
        obj.save()
 
