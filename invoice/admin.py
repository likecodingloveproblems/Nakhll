import jdatetime
import json
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.utils.timezone import localtime
from coupon.models import CouponUsage
from .models import Invoice, InvoiceItem


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    fields = (
        'name',
        'count',
        'price_with_discount',
        'price_without_discount',
        'weight',
        'shop_name',
        'preperation',
        'barcode')
    readonly_fields = ('preperation',)
    extra = 0

    def preperation(self, obj):
        return obj.product.PreparationDays
    preperation.short_description = 'زمان آماده سازی'


class CouponUsageInline(admin.TabularInline):
    model = CouponUsage
    extra = 0
    fields = ('coupon', 'price_applied', )


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'status',
        'is_payed',
        'final_price',
        'post_price',
        'coupons_total_price',
        'receiver_full_name',
        'created_datetime_jalali',
        'post_tracking_code',
    )
    list_filter = ('status', 'user',)
    readonly_fields = (
        'id',
        'final_price',
        'post_price',
        'coupons_total_price',
        'display_address',
        'receiver_full_name',
        'created_datetime_jalali',
        'post_tracking_code',
        'status',
        'shop_iban',
        'is_payed',
    )
    ordering = ['-created_datetime', ]
    search_fields = ('id', 'FactorNumber')
    fields = (
        'id',
        'user',
        'old_id',
        'FactorNumber',
        'status',
        'display_address',
        'invoice_price_with_discount',
        'invoice_price_without_discount',
        'logistic_price',
        'payment_request_datetime',
        'payment_datetime',
        'logistic_unit_details',
        'payment_unique_id',
        'total_weight_gram',
        'final_price',
        'shop_iban',
        'is_payed',
        'created_datetime_jalali',
        'coupons_total_price')

    inlines = [InvoiceItemInline, CouponUsageInline]
    change_form_template = "admin/custom/invoice_changeform.html"

    def receiver_full_name(self, obj):
        """Return the receiver full name

        receiver_full_name is an attribute of address_json, so it needs to be
        parsed from address_json.
        """
        if obj.address_json:
            address = json.loads(obj.address_json)
            return address.get('receiver_full_name', '')
        return ''
    receiver_full_name.short_description = 'نام گیرنده'

    def created_datetime_jalali(self, obj):
        """Return created datetime in jalali format"""
        localtime_time = localtime(obj.created_datetime)
        return jdatetime.datetime.fromgregorian(
            datetime=localtime_time).strftime('%Y/%m/%d %H:%M:%S')
    created_datetime_jalali.short_description = 'تاریخ ثبت'

    def shop_iban(self, obj):
        """All Shop owner's IBAN (International Bank Account Number)"""
        text = ''
        for shop in obj.shops.all():
            text += f'{shop.Title}: {shop.bank_account.iban}\n'
        return text
    shop_iban.short_description = 'شماره حساب'

    def is_payed(self, obj: Invoice):
        """Whether the invoice is payed or not"""
        return not obj.status == obj.Statuses.AWAIT_PAYMENT
    is_payed.short_description = 'پرداخت شده؟'
    is_payed.boolean = True

    def final_price(self, obj):
        """Return final price of the invoice in formatted string"""
        return f'{obj.final_price:,} ریال'
    final_price.short_description = 'قیمت نهایی'

    def post_price(self, obj):
        """Return post price of the invoice in formatted string"""
        return f'{obj.logistic_price:,} ریال'
    post_price.short_description = 'هزینه ارسال'

    def post_tracking_code(self, obj):
        """Return all post tracking codes of the invoice, comma separated"""
        barcodes_set = set()
        for item in obj.items.all():
            if item.barcode:
                barcodes_set.add(item.barcode)
        return ','.join(barcodes_set)
    post_tracking_code.short_description = 'بارکد رهگیری پستی'

    def coupons_total_price(self, obj):
        """Return total price of the invoice coupons in formatted string"""
        return f'{obj.coupons_total_price:,} ریال'
    coupons_total_price.short_description = 'هزینه کوپن'

    def display_address(self, obj):
        """Return address of the invoice in formatted string"""
        if obj.address_json:
            address = json.loads(obj.address_json)
            state = address.get('state', '')
            big_city = address.get('big_city', '')
            city = address.get('city', '')
            address_text = address.get('address', '')
            zip_code = address.get('zip_code', '')
            reveiver_name = address.get('receiver_full_name', '')
            reveiver_mobile_number = address.get('receiver_mobile_number', '')
            return (f'{state}, {big_city}, {city}, {address_text}\n'
                    f'کد پستی: {zip_code} - گیرنده:{reveiver_name}'
                    f'- شماره تماس:{reveiver_mobile_number}')
        return '-'
    display_address.short_description = 'آدرس'

    def response_change(self, request, obj: Invoice):
        """Change invoice status to completed if user clicks on checkout button

        This is an override of django's response_change method to make the
        invoice status change to completed by clicking on checkout button.
        This function should be only available to users in accounting group.
        """
        if "checkout_invoice" in request.POST:
            if request.user.has_perm('invoice.checkout_invoice'):
                obj.status = obj.Statuses.COMPLETED
                obj.save()
                self.message_user(request, "وضعیت فاکتور با موفقیت تغییر کرد")
                return HttpResponseRedirect(".")
            else:
                self.message_user(
                    request, "شما دسترسی لازم برای این کار را ندارید")
                return HttpResponseRedirect(".")
        return super().response_change(request, obj)
