from rest_framework import serializers
from logistic.models import Address
from nakhll_market.serializers import UserSerializer
from nakhll_market.models import State, BigCity, City



class AddressSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True, many=False)
    state = serializers.SlugRelatedField(slug_field='name', queryset=State.objects.all())
    big_city = serializers.SlugRelatedField(slug_field='name', queryset=BigCity.objects.all())
    city = serializers.SlugRelatedField(slug_field='name', queryset=City.objects.all())
    class Meta:
        model = Address
        # fields = ('user', 'state', 'bigcity', 'city', 'zip_code', 'address', 'phone_number')
        fields = '__all__'

