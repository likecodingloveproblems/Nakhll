from rest_framework import serializers
from .models import Invoice
from cart.models import Cart
from cart.serializers import CartSerializer
from logistic.models import Address
from logistic.serializers import AddressSerializer
from coupon.models import Coupon
from nakhll_market.serializers import UserSerializer


class InvoiceWriteSerializer(serializers.ModelSerializer):
    cart = serializers.PrimaryKeyRelatedField(queryset=Cart.objects.all())
    address = serializers.PrimaryKeyRelatedField(queryset=Address.objects.all(), required=False)
    coupon = serializers.SlugRelatedField(slug_field='code', queryset=Coupon.objects.all(), required=False)

    class Meta:
        model = Invoice
        fields = (
            'cart',
            'address',
            'coupon',
        )


class InvoiceReadSerializer(serializers.ModelSerializer):
    cart = CartSerializer(many=False, read_only=True)
    address = AddressSerializer(many=False, read_only=True)
    coupon = serializers.SlugRelatedField(slug_field='code', read_only=True)
    user = UserSerializer(many=False, read_only=True)
    class Meta:
        model = Invoice
        fields = (
            'id',
            'cart',
            'address',
            'user',
            'status',
            'coupon',
            'logistic_price',
            'logistic_errors',
        )

