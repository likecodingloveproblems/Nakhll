from rest_framework import serializers
from nakhll_market.serializers import ProductSerializer, UserSerializer
from nakhll_market.models import Product
from custom_list.models import Favorite


class UserFavoriteProductSerializer(serializers.ModelSerializer):
    """Serializer for the user's favorite list"""
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), write_only=True)
    products = ProductSerializer(many=True, read_only=True)
    user = UserSerializer(many=False, read_only=True)

    class Meta:
        model = Favorite
        fields = ['product', 'products', 'user']

    def save(self, **kwargs):
        fav_list = kwargs.pop('fav_list')
        fav_list.products.add(self.validated_data['product'])
        return fav_list
