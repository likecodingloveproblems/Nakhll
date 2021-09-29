from rest_framework import serializers
from nakhll_market.serializers import ProductSerializer, UserSerializer
from custom_list.models import Favorite


class UserFavoriteProductSerializer(serializers.ModelSerializer):
    product = ProductSerializer(many=True, read_only=False)
    user = UserSerializer(many=False, read_only=True)
    class Meta:
        model = Favorite
        fields = ['product', 'user']

class SimpleFavoriteSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(many=False, read_only=True)
    class Meta:
        model = Favorite
        fields = ['product', ]
