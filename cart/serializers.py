from rest_framework import serializers
from cart.models import Cart, CartItem
from coupon.models import Coupon
from logistic.models import Address
from nakhll_market.models import Product
from nakhll_market.serializers import ProductSerializer



class CartItemSerializer(serializers.ModelSerializer):
    cart = serializers.PrimaryKeyRelatedField(read_only=True)
    product = serializers.PrimaryKeyRelatedField(many=False, read_only=False, queryset=Product.objects.all())
    class Meta:
        model = CartItem
        fields = ('cart', 'product', 'count', 'added_datetime', 'product_last_state', )
        read_only_fields = ('product_last_state', )


class CartItemReadSerializer(serializers.ModelSerializer):
    cart = serializers.PrimaryKeyRelatedField(read_only=True)
    product = ProductSerializer(read_only=True, many=False)
    total_price = serializers.SerializerMethodField()
    total_old_price = serializers.SerializerMethodField()

    def get_total_old_price(self, obj):
        return obj.product.old_price * obj.count

    def get_total_price(self, obj):
        return obj.product.price * obj.count
    class Meta:
        model = CartItem
        fields = '__all__'
        read_only_fields = ('product_last_state', )





class CartSerializer(serializers.ModelSerializer):
    ordered_items = CartItemReadSerializer(many=True, read_only=True)
    count = serializers.SerializerMethodField()
    class Meta:
        model = Cart
        fields = ('user', 'total_price', 'total_old_price', 'ordered_items', 'get_diffrences', 'count')
    
    def get_count(self, object):
        return object.items.count()


class CartWriteSerializer(serializers.ModelSerializer):
    address = serializers.PrimaryKeyRelatedField(queryset=Address.objects.all(), required=False)
    coupon = serializers.SlugRelatedField(slug_field='code', queryset=Coupon.objects.all(), required=False)

    class Meta:
        model = Cart
        fields = (
            'address',
            'coupon',
        )