from rest_framework import serializers
from nakhll_market.serializers import ProductSerializer, UserSerializer
from custom_list.models import Favorite


class UserFavoriteProductSerializer(serializers.ModelSerializer):
    product = ProductSerializer(many=True, read_only=False)
    user = UserSerializer(many=False, read_only=True)
    class Meta:
        model = Favorite
        fields = ['product', 'user']

    def save(self, **kwargs):
        fav_list = kwargs.pop('fav_list')
        validated_data = {**self.validated_data, 'user': fav_list.user}
        return self.update(self.instance, validated_data)
