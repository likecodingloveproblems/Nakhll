from rest_framework import serializers
from cart.models import Cart, CartItem
from coupon.models import Coupon
from coupon.serializers import CouponSerializer
from logistic.models import Address
from logistic.serializers import AddressSerializer
from nakhll_market.models import Product
from nakhll_market.serializers import ProductSerializer


class CartItemSerializer(serializers.ModelSerializer):
    """Serializer for CartItem model

    This is used to create and update CartItem objects
    """
    cart = serializers.PrimaryKeyRelatedField(read_only=True)
    product = serializers.PrimaryKeyRelatedField(many=False, read_only=False, queryset=Product.objects.all())

    class Meta:
        model = CartItem
        fields = ('cart', 'product', 'count', 'added_datetime', )
        read_only_fields = ('product_last_state', )

    def create(self, validated_data):
        cart = validated_data.pop('cart')
        product = validated_data.pop('product')
        return cart.add_product(product)


class CartItemReadSerializer(serializers.ModelSerializer):
    """Serializer for CartItem model

    This serializer is used for read only purposes.
    """
    cart = serializers.PrimaryKeyRelatedField(read_only=True)
    product = ProductSerializer(read_only=True, many=False)
    total_price = serializers.SerializerMethodField()
    total_old_price = serializers.SerializerMethodField()

    def get_total_old_price(self, obj):
        """Get total old price of the cart item"""
        return obj.product.old_price * obj.count

    def get_total_price(self, obj):
        """Get total price of the cart item"""
        return obj.product.price * obj.count

    class Meta:
        model = CartItem
        fields = '__all__'
        read_only_fields = ('product_last_state', )


class CartSerializer(serializers.ModelSerializer):
    """Serializer for Cart model

    This is a read-only serializer for cart objects.
    """
    ordered_items = CartItemReadSerializer(many=True, read_only=True)
    count = serializers.SerializerMethodField()
    address = AddressSerializer(read_only=True)
    coupon_details = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = (
            'user',
            'cart_price',
            'cart_old_price',
            'address',
            'logistic_details',
            'coupon_details',
            'ordered_items',
            'count',
            'total_price',
            'paid_by_coin',
            'coin_price')

    def get_count(self, object):
        """Get total count of items in cart"""
        return object.items.count()

    def get_coupon_details(self, cart):
        """Get coupon details for cart"""
        coupons = cart.get_coupons_price()
        total_price = sum([coupon['price'] for coupon in coupons])
        return {'total': total_price, 'coupons': coupons}


class CartWriteSerializer(serializers.ModelSerializer):
    """Serializer for Cart model

    This is a write serializer for cart objects.
    """
    address = serializers.PrimaryKeyRelatedField(queryset=Address.objects.all(), required=False)
    coupon = serializers.SlugRelatedField(slug_field='code', error_messages={
        'does_not_exist': 'کوپن تخفیف وارد شده نامعتبر است',
    }, required=False, queryset=Coupon.objects.all())

    class Meta:
        model = Cart
        fields = (
            'address',
            'coupon',
            'paid_by_coin',
        )
