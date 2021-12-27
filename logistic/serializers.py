from django.db.models.expressions import Case, Value, When
import logistic
from django.db.models import fields
from django.utils.translation import ugettext as _
from rest_framework import serializers
from logistic.models import Address, ShopLogisticUnit, ShopLogisticUnitConstraint, ShopLogisticUnitCalculationMetric
from nakhll_market.models import Field, Product, Shop, State, BigCity, City
from nakhll_market.serializer_fields import Base64ImageField


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


class ProductSerializer(serializers.ModelSerializer):
    is_checked = serializers.SerializerMethodField()
    class Meta:
        model = Product
        fields = ('ID', 'Title', 'is_checked')

    def get_is_checked(self, obj):
        return obj.is_checked



class ShopLogisticUnitSerializer(serializers.ModelSerializer):
    shop = serializers.SlugRelatedField(slug_field='Slug', queryset=Shop.objects.all())
    constraint_id = serializers.SerializerMethodField()
    metric_id = serializers.SerializerMethodField()
    cities_count = serializers.SerializerMethodField()
    products_count = serializers.SerializerMethodField()
    logo = Base64ImageField(max_length=None, use_url=True, allow_empty_file=False, required=False)
    class Meta:
        model = ShopLogisticUnit
        fields = ('id', 'shop', 'name', 'description', 'logo', 'is_active', 'is_publish',
                  'constraint_id', 'metric_id', 'cities_count', 'products_count', )
        read_only_fields = ('id', 'is_publish', )

    def get_constraint_id(self, obj):
        return obj.constraint.id if hasattr(obj, 'constraint') else None
    
    def get_metric_id(self, obj):
        return obj.calculation_metric.id if hasattr(obj, 'calculation_metric') else None

    def get_cities_count(self, obj):
        if not obj.constraint or not obj.constraint.cities:
            return 0
        return obj.constraint.cities.count()

    def get_products_count(self, obj):
        if not obj.constraint or not obj.constraint.products:
            return 0
        return obj.constraint.products.count()

        

class ShopLogisticUnitConstraintReadSerializer(serializers.ModelSerializer):
    shop_logistic_unit = serializers.PrimaryKeyRelatedField(read_only=True)
    products = serializers.SerializerMethodField()
    class Meta:
        model = ShopLogisticUnitConstraint
        fields = ('id', 'shop_logistic_unit', 'cities', 'products', 'categories', 'max_weight', 'min_weight', 
                  'max_cart_price', 'min_cart_price', 'max_cart_count', 'min_cart_count', )
        read_only_fields = ('id', 'shop_logistic_unit', )
    
    def get_products(self, obj):
        shop = obj.shop_logistic_unit.shop
        products = Product.objects.filter(
            FK_Shop=shop).annotate(is_checked=Case(
                When(ID__in=obj.products.values('ID'), then=Value(True)),
                default=Value(False),
                output_field=fields.BooleanField()
            ))
        return ProductSerializer(products, many=True).data
        

class ShopLogisticUnitConstraintWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopLogisticUnitConstraint
        fields = ('id', 'cities', 'products', 'categories', 'max_weight', 'min_weight', 
                  'max_cart_price', 'min_cart_price', 'max_cart_count', 'min_cart_count', )
        read_only_fields = ('id', )

    def validate_products(self, products):
        if not self._are_products_belong_to_shop(products):
            raise serializers.ValidationError(_('این محصولات متعلق به فروشگاه شما نیستند.'))
        return products

    def _are_products_belong_to_shop(self, products):
        if not products:
            return True
        shop_products = self.instance.shop_logistic_unit.shop.ShopProduct.all()
        return set(products).issubset(set(shop_products))


class ShopLogisticUnitCalculationMetricSerializer(serializers.ModelSerializer):
    shop_logistic_unit = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = ShopLogisticUnitCalculationMetric
        fields = ('id', 'shop_logistic_unit', 'price_per_kilogram', 'price_per_extra_kilogram', )
        read_only_fields = ('id', 'shop_logistic_unit', )


class ShopLogisticUnitConstraintWithoutM2MSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopLogisticUnitConstraint
        fields = ('id', 'max_weight', 'min_weight', 'max_cart_price',
                  'min_cart_price', 'max_cart_count', 'min_cart_count', )
        read_only_fields = ('id', )



class ShopLogisticUnitFullSerializer(serializers.ModelSerializer):
    shop = serializers.SlugRelatedField(slug_field='Slug', queryset=Shop.objects.all())
    constraint = ShopLogisticUnitConstraintWithoutM2MSerializer(read_only=False, required=False)
    calculation_metric = ShopLogisticUnitCalculationMetricSerializer(read_only=False, required=False)
    cities_count = serializers.SerializerMethodField()
    products_count = serializers.SerializerMethodField()
    logo = Base64ImageField(max_length=None, use_url=True, allow_empty_file=False, required=False)
    class Meta:
        model = ShopLogisticUnit
        fields = ('id', 'shop', 'name', 'description', 'logo', 'is_active', 'is_publish',
                  'constraint', 'calculation_metric', 'cities_count', 'products_count', )
        read_only_fields = ('id', 'is_publish', )

    def get_constraint_id(self, obj):
        return obj.constraint.id if hasattr(obj, 'constraint') else None
    
    def get_metric_id(self, obj):
        return obj.calculation_metric.id if hasattr(obj, 'calculation_metric') else None

    def get_cities_count(self, obj):
        if not obj.constraint or not obj.constraint.cities:
            return 0
        return obj.constraint.cities.count()

    def get_products_count(self, obj):
        if not obj.constraint or not obj.constraint.products:
            return 0
        return obj.constraint.products.count()

 
    def update(self, instance, validated_data):
        constraint_dict = validated_data.pop('constraint', {})
        metric_dict = validated_data.pop('calculation_metric', {})
        instance = super().update(instance, validated_data)

        constraint = instance.constraint
        for key, value in constraint_dict.items():
            setattr(constraint, key, value)
        constraint.save()

        metric = instance.calculation_metric
        for key, value in metric_dict.items():
            setattr(metric, key, value)
        metric.save()

        return instance









# class LogisticUnitSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = LogisticUnit
#         fields = ('id', 'name', 'description',)
#         read_only_fields = ('id',)

# class ShopLogisticUnitSerializer(serializers.ModelSerializer):
#     logistic_unit = LogisticUnitSerializer(read_only=True)

#     class Meta:
#         model = ShopLogisticUnit
#         fields = ('id', 'is_active', 'logistic_unit', 'use_default_setting')
#         read_only_fields = ('id', )



# class LogisticUnitMetricSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = LogisticUnitMetric
#         fields = ("id", "price_per_kg", "price_per_extra_kg", )
#         read_only_fields = ("id",)

# class LogisticUnitConstraintParameterSerializer(serializers.ModelSerializer):
#     price_per_kg = serializers.IntegerField(required=False, source='shop_logistic_unit_constraint.shop_logistic_unit_metric.metric.price_per_kg')
#     price_per_extra_kg = serializers.IntegerField(required=False, source='shop_logistic_unit_constraint.shop_logistic_unit_metric.metric.price_per_extra_kg')
#     cities = serializers.PrimaryKeyRelatedField(many=True, queryset=City.objects.all())
#     categories = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
#     products = serializers.PrimaryKeyRelatedField(many=True, queryset=Product.objects.all())

#     class Meta:
#         model = LogisticUnitConstraintParameter
#         fields = ("id", "cities", "products", "min_price", "categories",
#                   "max_weight_g", "max_package_value", "price_per_kg", "price_per_extra_kg",)
#         read_only_fields = ("id",)

#     def validate(self, attrs):
#         return super().validate(attrs)

#     def validate_products(self, products):
#         if not self._are_products_belong_to_shop(products):
#             raise serializers.ValidationError(_('این محصولات متعلق به فروشگاه شما نیستند'))
#         restricted_category_ids = self._get_restricted_products(products)
#         if restricted_category_ids:
#             restricted_products = Product.objects.filter(new_category__in=restricted_category_ids, ID__in=[p.ID for p in products])
#             raise serializers.ValidationError(_(
#                 'محصولات زیر به دلیل محدودیت در واحد پستی، قابل ارسال نیستند:<br />{}'.format(
#                     '<br />'.join(map(str, restricted_products)))
#             ))
#         return products

#     def _are_products_belong_to_shop(self, products):
#         if not products:
#             return True
#         shop_products = self.instance.shop_logistic_unit_constraint.shop_logistic_unit.shop.ShopProduct.all()
#         return set(products).issubset(set(shop_products))
            
            
#     def _get_restricted_products(self, products):
#         if not products:
#             products = self.instance.shop_logistic_unit_constraint.shop_logistic_unit.shop.ShopProduct.all()
#         category_set = set()
#         for product in products:
#             category_set.add(product.new_category.id)

#         category_constraint_ids = set(LogisticUnitConstraintParameter.objects.filter(
#            logisticunitconstraint__logistic_unit=self.instance.shop_logistic_unit_constraint.shop_logistic_unit.logistic_unit
#         ).values_list('categories', flat=True))

#         diffrences = category_set.intersection(category_constraint_ids)
#         return  diffrences

#     def update(self, instance, validated_data):
#         sluc = validated_data.pop('shop_logistic_unit_constraint', {})
#         slum = sluc.get('shop_logistic_unit_metric', {})
#         metric = slum.get('metric', {})
#         metric_object = instance.shop_logistic_unit_constraint.shop_logistic_unit_metric.metric

#         price_per_extra_kg = metric.get('price_per_extra_kg', metric_object.price_per_extra_kg)
#         price_per_kg = metric.get('price_per_kg', metric_object.price_per_kg)

#         instance = super().update(instance, validated_data)

#         metric_object.price_per_kg = price_per_kg
#         metric_object.price_per_extra_kg = price_per_extra_kg
#         metric_object.save()
#         return instance
        
# class LogisticUnitConstraintParameterReadSerializer(serializers.ModelSerializer):
#     price_per_kg = serializers.IntegerField(read_only=True, source='shop_logistic_unit_constraint.shop_logistic_unit_metric.metric.price_per_kg')
#     price_per_extra_kg = serializers.IntegerField(read_only=True, source='shop_logistic_unit_constraint.shop_logistic_unit_metric.metric.price_per_extra_kg')
#     cities = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
#     products = serializers.SerializerMethodField()

#     class Meta:
#         model = LogisticUnitConstraintParameter
#         fields = ("id", "cities", "products", "min_price", "max_weight_g", "max_package_value",
#                   "price_per_kg", "price_per_extra_kg",)
#         read_only_fields = ("id",)

#     def get_products(self, obj):
#         shop = obj.shop_logistic_unit_constraint.shop_logistic_unit.shop
#         products = Product.objects.filter(
#             FK_Shop=shop).annotate(is_checked=Case(
#                 When(ID__in=obj.products.values('ID'), then=Value(True)),
#                 default=Value(False),
#                 output_field=fields.BooleanField()
#             ))
#         return ProductSerializer(products, many=True).data
        


        
        
        
        
        


# class LogisticUnitConstraintSerializer(serializers.ModelSerializer):
#     logistic_unit = LogisticUnitSerializer()
#     constraint = LogisticUnitConstraintParameterSerializer()
#     class Meta:
#         model = LogisticUnitConstraint
#         fields = ("id","is_publish", "logistic_unit", "constraint")
#         read_only_fields = ("id",)


# class ShopLogisticUnitConstraintSerializer(serializers.ModelSerializer):
#     shop_logistic_unit = serializers.PrimaryKeyRelatedField(queryset=ShopLogisticUnit.objects.all())
#     cities_count = serializers.SerializerMethodField()
#     products_count = serializers.SerializerMethodField()
#     title = serializers.SerializerMethodField()

#     class Meta:
#         model = ShopLogisticUnitConstraint
#         fields = ("id", "is_active", "shop_logistic_unit", "cities_count", "products_count", "title")
#         read_only_fields = ("id",)

#     def get_cities_count(self, obj):
#         if not obj.constraint or not obj.constraint.cities:
#             return 0
#         return obj.constraint.cities.count()

#     def get_products_count(self, obj):
#         if not obj.constraint or not obj.constraint.products:
#             return 0
#         return obj.constraint.products.count()

#     def get_title(self, obj):
#         return f'محدوده {obj.id}'


# class ShopLogisticUnitMetricSerializer(serializers.ModelSerializer):
#     shop_logistic_unit_constraint = ShopLogisticUnitSerializer
#     metric = LogisticUnitMetricSerializer

#     class Meta:
#         model = ShopLogisticUnitMetric
#         fields = ("id", "metric", "shop_logistic_unit_constraint",)
#         read_only_fields = ("id",)
