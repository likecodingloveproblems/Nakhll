from rest_framework import serializers
from cart.models import Cart, CartItem
from nakhll_market.models import Product
from nakhll_market.serializers import ProductSerializer



class CartItemSerializer(serializers.ModelSerializer):
    cart = serializers.PrimaryKeyRelatedField(read_only=True)
    # TODO: I should think a way of changing queryset=Product.objects.all() to a request that not hit product db directly
    # product = serializers.SlugRelatedField(slug_field='Slug', many=False, read_only=False, queryset=Product.objects.all())
    product = serializers.PrimaryKeyRelatedField(many=False, read_only=False, queryset=Product.objects.all())
    class Meta:
        model = CartItem
        fields = '__all__'
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
    class Meta:
        model = Cart
        fields = ('user', 'guest_unique_id', 'total_price', 'total_old_price', 'created_datetime', 'ordered_items', 'get_diffrences')

# class CartTransmissionSerializer(serializers.ModelSerializer):
#     cart = serializers.PrimaryKeyRelatedField(queryset=CartTransmission.objects.all(), read_only=False, many=False)
#     class Meta:
#         model = CartTransmission
#         fields = ('cart', )

class ProductLastStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['Price', 'OldPrice', 'Status', 'PreparationDays', 'Publish', 'Title']