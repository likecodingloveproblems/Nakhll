import jdatetime
from rest_framework import serializers
from .models import Invoice, InvoiceItem
from cart.models import Cart
from cart.serializers import CartSerializer
from logistic.models import Address
from logistic.serializers import AddressSerializer
from coupon.models import Coupon
from coupon.serializers import CouponUsageSerializer
from nakhll_market.serializers import UserSerializer


class InvoiceItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(read_only=True)
    added_date_jalali = serializers.SerializerMethodField()
    added_time_jalali = serializers.SerializerMethodField()
    buyer = serializers.SerializerMethodField()
    class Meta:
        model = InvoiceItem
        fields = ['id', 'product', 'slug', 'name', 'count', 'price_with_discount', 'price_without_discount', 'weight', 
                    'image', 'image_thumbnail', 'shop_name', 'added_date_jalali', 'added_time_jalali', 'buyer', 'status']

    def get_added_date_jalali(self, obj):
        jalali_datetime = jdatetime.datetime.fromgregorian(datetime=obj.added_datetime, locale='fa_IR')
        return jalali_datetime.strftime('%Y/%m/%d')
        
    def get_added_time_jalali(self, obj):
        jalali_datetime = jdatetime.datetime.fromgregorian(datetime=obj.added_datetime, locale='fa_IR')
        return jalali_datetime.strftime('%H:%M')

    def get_buyer(self, obj):
        return obj.invoice.user.get_full_name()
        

class InvoiceWriteSerializer(serializers.ModelSerializer):
    address = serializers.PrimaryKeyRelatedField(queryset=Address.objects.all(), required=False)
    coupon = serializers.SlugRelatedField(slug_field='code', queryset=Coupon.objects.all(), required=False)

    class Meta:
        model = Invoice
        fields = (
            'address',
            'coupon',
        )


class InvoiceRetrieveSerializer(serializers.ModelSerializer):
    address = AddressSerializer(many=False, read_only=True)
    coupon_usages = CouponUsageSerializer(read_only=True, many=True)
    user = UserSerializer(many=False, read_only=True)
    items = serializers.SerializerMethodField(method_name='get_invoie_items')
    receiver_mobile_number = serializers.SerializerMethodField()
    created_time_jalali = serializers.SerializerMethodField()
    created_date_jalali = serializers.SerializerMethodField()

    def get_receiver_mobile_number(self, obj):
        if obj.address:
            return obj.address.receiver_mobile_number
        return None
    def get_created_date_jalali(self, obj):
        jalali_datetime = jdatetime.datetime.fromgregorian(datetime=obj.created_datetime, locale='fa_IR')
        return jalali_datetime.strftime('%Y/%m/%d')
    def get_created_time_jalali(self, obj):
        jalali_datetime = jdatetime.datetime.fromgregorian(datetime=obj.created_datetime, locale='fa_IR')
        return jalali_datetime.strftime('%H:%M')
    def get_invoie_items(self, obj):
        items = obj.items.order_by('product__FK_Shop')
        return InvoiceItemSerializer(items, many=True, read_only=True).data
    class Meta:
        model = Invoice
        fields = (
            'id',
            'items',
            'address',
            'address_json',
            'user',
            'payment_unique_id',
            'status',
            'invoice_price_with_discount',
            'invoice_price_without_discount',
            'coupon_usages',
            'logistic_price',
            'logistic_errors',
            'final_price',
            'created_date_jalali',
            'created_time_jalali',
            'coupons_total_price',
            'payment_request_datetime',
            'receiver_mobile_number',
        )


class OnlyInvoiceSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False, read_only=True)
    receiver_mobile_number = serializers.SerializerMethodField()
    created_time_jalali = serializers.SerializerMethodField()
    created_date_jalali = serializers.SerializerMethodField()

    def get_receiver_mobile_number(self, obj):
        if obj.address:
            return obj.address.receiver_mobile_number
        return None
    def get_created_date_jalali(self, obj):
        jalali_datetime = jdatetime.datetime.fromgregorian(datetime=obj.created_datetime, locale='fa_IR')
        return jalali_datetime.strftime('%Y/%m/%d')
    def get_created_time_jalali(self, obj):
        jalali_datetime = jdatetime.datetime.fromgregorian(datetime=obj.created_datetime, locale='fa_IR')
        return jalali_datetime.strftime('%H:%M')
    def get_invoie_items(self, obj):
        items = obj.items.order_by('product__FK_Shop')
        return InvoiceItemSerializer(items, many=True, read_only=True).data
    class Meta:
        model = Invoice
        fields = (
            'id',
            'address_json',
            'user',
            'payment_unique_id',
            'status',
            'invoice_price_with_discount',
            'invoice_price_without_discount',
            'coupon_usages',
            'logistic_price',
            'logistic_errors',
            'final_price',
            'created_date_jalali',
            'created_time_jalali',
            'payment_request_datetime',
            'receiver_mobile_number',
        )


