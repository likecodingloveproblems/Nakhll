from rest_framework import serializers
from logistic.models import Address, ShopLogisticUnit
from nakhll_market.models import State, BigCity, City



class AddressSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    state = serializers.SlugRelatedField(slug_field='name', queryset=State.objects.all())
    big_city = serializers.SlugRelatedField(slug_field='name', queryset=BigCity.objects.all())
    city = serializers.SlugRelatedField(slug_field='name', queryset=City.objects.all())
    class Meta:
        model = Address
        fields = ('id', 'user', 'state', 'big_city', 'city', 'zip_code', 'address', 'phone_number', 'receiver_full_name', 'receiver_mobile_number',)
        read_only_fields = ('id', 'user')

    def get_user(self, obj):
        return obj.user.first_name + ' ' + obj.user.last_name


class ShopOwnerAddressSerializer(AddressSerializer):
    class Meta:
        model = Address
        fields = ('id', 'user', 'state', 'big_city', 'city', 'zip_code', 'address', 'receiver_full_name', 'receiver_mobile_number',)
        read_only_fields = ('id', 'user')

        
        
class ShopLogisticUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopLogisticUnit
        fields = ('is_active', 'logistic_unit.name', 'logistic_unit.description',)