from django.db.models import fields
from rest_framework import serializers
from logistic.models import Address, LogisticUnitMetric, ShopLogisticUnit, ShopLogisticUnitConstraint, LogisticUnit,LogisticUnitConstraintParameter, ShopLogisticUnitMetric
from nakhll_market.models import Field, State, BigCity, City



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

        
class LogisticUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = LogisticUnit
        fields = ('id', 'name', 'description',)
        read_only_fields = ('id',)
        
class ShopLogisticUnitSerializer(serializers.ModelSerializer):
    logistic_unit = LogisticUnitSerializer(read_only=True)
    class Meta:
        model = ShopLogisticUnit
        fields = ('id', 'is_active', 'logistic_unit')
        read_only_fields = ('id', )
        
        
class LogisticUnitMetricSerializer(serializers.ModelSerializer):
    class Meta:
        modcel = LogisticUnitMetric
        fields = ("id","price_per_kg","price_per_extra_kg","is_default")
        read_only_fields = ("id",)
            
        
class LogisticUnitConstraintParameterSerializer(serializers.ModelSerializer):
    class Meta:
        model = LogisticUnitConstraintParameter
        fields = ("id","cities","products","min_price","categories","max_weight_g","max_package_value")
        read_only_fields = ("id",)

class LogisticUnitConstraintSerializer(serializers.ModelSerializer):
    logistic_unit = LogisticUnitSerializer
    constraint = LogisticUnitConstraintParameter
    class Meta:
        model = ShopLogisticUnitConstraint
        fields = ("id","is_publish",)
        read_only_fields = ("id",)
        
        
class ShopLogisticUnitConstraintSerializer(serializers.ModelSerializer):
    shop_logistic_unit = ShopLogisticUnitSerializer
    constraint = LogisticUnitConstraintParameterSerializer
    class Meta:
        model = ShopLogisticUnitConstraint
        fields = ("id","is_active",)
        read_only_fields = ("id",)
        
class ShopLogisticUnitMetricSerializer(serializers.ModelSerializer):
    shop_logistic_unit_constraint = ShopLogisticUnitSerializer
    metric = LogisticUnitMetricSerializer
    class Meta:
        model =ShopLogisticUnitMetric
        fields = ("id",)
        read_only_fields = ("id",)