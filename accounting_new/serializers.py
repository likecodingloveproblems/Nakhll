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
    class Meta:
        model = InvoiceItem
        fields = ['id', 'product', 'name', 'count', 'price_with_discount', 'price_without_discount', 'weight', 
                    'image', 'image_thumbnail', 'shop_name', 'added_datetime']

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
    items = InvoiceItemSerializer(many=True, read_only=True)
    class Meta:
        model = Invoice
        fields = (
            'id',
            'items',
            'address',
            'address_json',
            'user',
            'status',
            'invoice_price_with_discount',
            'invoice_price_without_discount',
            'coupon_usages',
            'logistic_price',
            'logistic_errors',
            'final_price',
            'created_datetime',
            'coupons_total_price',
            'payment_request_datetime',
        )

