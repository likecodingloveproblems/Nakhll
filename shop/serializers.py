from rest_framework import serializers
from nakhll_market.models import Shop
from .models import ShopFeature, ShopFeatureInvoice, ShopLanding, PinnedURL

class ShopFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopFeature
        fields = ('id', 'name', 'unit', 'demo_days',
                  'price_per_unit_without_discount', 
                  'price_per_unit_with_discount')

class ShopFeatureDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopFeature
        fields = ('id', 'name', 'description', 'unit', 'demo_days',
                  'price_per_unit_without_discount', 
                  'price_per_unit_with_discount')



class ShopFeatureInvoiceSerializer(serializers.ModelSerializer):
    shop = serializers.SlugRelatedField(slug_field='Slug', read_only=True)
    feature = ShopFeatureSerializer(many=False)
    class Meta:
        model = ShopFeatureInvoice
        fields = ('id', 'shop', 'feature', 'status', 'bought_price_per_unit',
                    'bought_unit', 'unit_count', 'start_datetime',
                    'expire_datetime', 'payment_datetime', 'is_demo')

class ShopFeatureInvoiceWriteSerializer(serializers.ModelSerializer):
    shop = serializers.SlugRelatedField(slug_field='Slug', queryset=Shop.objects.all())
    feature = serializers.PrimaryKeyRelatedField(queryset=ShopFeature.objects.all())
    class Meta:
        model = ShopFeatureInvoice
        fields = ('id', 'shop', 'feature',)

    def is_valid(self, raise_exception=False, is_demo=False):
        is_valid = super().is_valid(raise_exception=True)
        if is_valid and is_demo:
            self.demo_validation(self.validated_data)
        return is_valid

    def demo_validation(self, data):
        shop = data.get('shop')
        feature = data.get('feature')
        if not feature.demo_days:
            raise serializers.ValidationError({'error': 'این قابلیت حالت آزمایشی را پشتیبانی نمی‌کند'})
        if feature.is_enabled_before(shop):
            raise serializers.ValidationError({'error': 'شما قبلا از نسخه آزمایشی این قابلیت استفاده کرده اید'})
    
class ShopLandingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopLanding
        fields = ('id', 'name', 'created_at', 'updated_at', 'status' )

class ShopLandingDetailsSerializer(serializers.ModelSerializer):
    shop = serializers.SlugRelatedField(slug_field='Slug', queryset=Shop.objects.all(), required=False)
    class Meta:
        model = ShopLanding
        fields = ('id', 'name', 'shop', 'page_data')

class UserPinnedURLSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    class Meta:
        model = PinnedURL
        fields = ('id', 'name', 'link', 'user')


