from rest_framework import serializers
from cart.models import Cart, CartItem, CartTransmission
from nakhll_market.models import Product
from nakhll_market.serializers import ProductSerializer



class CartItemSerializer(serializers.ModelSerializer):
    cart = serializers.PrimaryKeyRelatedField(read_only=True)
    # TODO: I should think a way of changing queryset=Product.objects.all() to a request that not hit product db directly
    # product = serializers.SlugRelatedField(slug_field='Slug', many=False, read_only=False, queryset=Product.objects.all())
    product = serializers.PrimaryKeyRelatedField(many=False, read_only=False, queryset=Product.objects.all())
    class Meta:
        model = CartItem
        # fields = ('cart', 'product', 'count', 'product_last_known_state')
        fields = '__all__'
        read_only_fields = ('product_last_known_state', )


class CartItemReadSerializer(serializers.ModelSerializer):
    cart = serializers.PrimaryKeyRelatedField(read_only=True)
    product = ProductSerializer(read_only=True, many=False)
    class Meta:
        model = CartItem
        # fields = ('cart', 'product', 'count', 'product_last_known_state')
        fields = '__all__'
        read_only_fields = ('product_last_known_state', )





class CartSerializer(serializers.ModelSerializer):
    items = CartItemReadSerializer(many=True, read_only=True)
    class Meta:
        model = Cart
        fields = ('user', 'guest_unique_id', 'status', 'created_datetime', 'change_status_datetime', 'ordered_items', 'get_diffrences')

class CartTransmissionSerializer(serializers.ModelSerializer):
    cart = serializers.PrimaryKeyRelatedField(queryset=CartTransmission.objects.all(), read_only=False, many=False)
    class Meta:
        model = CartTransmission
        fields = ('cart', )
