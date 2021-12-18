from django.db.models import fields
from rest_framework import serializers
from logistic.models import Address, LogisticUnitConstraint, LogisticUnitMetric, ShopLogisticUnit, ShopLogisticUnitConstraint, LogisticUnit, LogisticUnitConstraintParameter, ShopLogisticUnitMetric
from nakhll_market.models import Field, Product, State, BigCity, City


class AddressSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    state = serializers.SlugRelatedField(
        slug_field='name', queryset=State.objects.all())
    big_city = serializers.SlugRelatedField(
        slug_field='name', queryset=BigCity.objects.all())
    city = serializers.SlugRelatedField(
        slug_field='name', queryset=City.objects.all())

    class Meta:
        model = Address
        fields = ('id', 'user', 'state', 'big_city', 'city', 'zip_code', 'address',
                  'phone_number', 'receiver_full_name', 'receiver_mobile_number',)
        read_only_fields = ('id', 'user')

    def get_user(self, obj):
        return obj.user.first_name + ' ' + obj.user.last_name


class ShopOwnerAddressSerializer(AddressSerializer):
    class Meta:
        model = Address
        fields = ('id', 'user', 'state', 'big_city', 'city', 'zip_code',
                  'address', 'receiver_full_name', 'receiver_mobile_number',)
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
        fields = ('id', 'is_active', 'logistic_unit', 'use_default_setting')
        read_only_fields = ('id', )


class LogisticUnitMetricSerializer(serializers.ModelSerializer):
    class Meta:
        modcel = LogisticUnitMetric
        fields = ("id", "price_per_kg", "price_per_extra_kg", )
        read_only_fields = ("id",)


class LogisticUnitConstraintParameterSerializer(serializers.ModelSerializer):
    price_per_kg = serializers.IntegerField(required=False, source='\
                                            shop_logistic_unit_constraint.shop_logistic_unit_metric.price_per_kg\
                                            ')
    price_per_extra_kg = serializers.IntegerField(required=False, source='\
                                            shop_logistic_unit_constraint.shop_logistic_unit_metric.price_per_extra_kg\
                                            ')
    cities = serializers.PrimaryKeyRelatedField(
        many=True, queryset=City.objects.all())
    categories = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    products = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Product.objects.all())

    class Meta:
        model = LogisticUnitConstraintParameter
        fields = ("id", "cities", "products", "min_price", "categories",
                  "max_weight_g", "max_package_value", "price_per_kg", "price_per_extra_kg",)
        read_only_fields = ("id",)

# class LogisticUnitConstraintSerializer(serializers.ModelSerializer):
#     logistic_unit = LogisticUnitSerializer()
#     constraint = LogisticUnitConstraintParameterSerializer()
#     class Meta:
#         model = LogisticUnitConstraint
#         fields = ("id","is_publish", "logistic_unit", "constraint")
#         read_only_fields = ("id",)


class ShopLogisticUnitConstraintSerializer(serializers.ModelSerializer):
    shop_logistic_unit = serializers.PrimaryKeyRelatedField(queryset=ShopLogisticUnit.objects.all())
    cities_count = serializers.SerializerMethodField()
    products_count = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()

    class Meta:
        model = ShopLogisticUnitConstraint
        fields = ("id", "is_active", "shop_logistic_unit", "cities_count", "products_count", "title")
        read_only_fields = ("id",)

    def get_cities_count(self, obj):
        if not obj.constraint or not obj.constraint.cities:
            return 0
        return obj.constraint.cities.count()

    def get_products_count(self, obj):
        if not obj.constraint or not obj.constraint.products:
            return 0
        return obj.constraint.products.count()

    def get_title(self, obj):
        return f'محدوده {obj.id}'


class ShopLogisticUnitMetricSerializer(serializers.ModelSerializer):
    shop_logistic_unit_constraint = ShopLogisticUnitSerializer
    metric = LogisticUnitMetricSerializer

    class Meta:
        model = ShopLogisticUnitMetric
        fields = ("id", "metric", "shop_logistic_unit_constraint",)
        read_only_fields = ("id",)
