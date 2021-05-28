from rest_framework import serializers
from rest_framework.utils import field_mapping
from nakhll_market.models import (
    AmazingProduct, AttrPrice, AttrProduct, Attribute,
    Category, Product, ProductBanner, Shop, Slider, Comment,
    SubMarket
    )

# landing serializers
class SliderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Slider
        fields = [
            'url', 'image', 'title', 'show_info', 'description', 'location',
            ]

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            'slug', 'title', 'url', 'image_thumbnail',
        ]

class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = [
            'slug', 'title', 'url', 'image_thumbnail_url',
            'state'
        ]

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'image_thumbnail_url', 'url', 'old_price', 'price', 'slug',
            'title', 'status', 'discounted', 'id'
        ]

class AmazingProductSerializer(serializers.ModelSerializer):
    product = ProductSerializer(many=False, read_only=True)
    class Meta:
        model = AmazingProduct
        fields = [
            'product', 'start_date_field', 'end_date_field'
        ]

# product page serializer
class AttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attribute
        fields = [
            'title', 'unit'
        ]

class AttrProductSerializer(serializers.ModelSerializer):
    FK_Attribute = AttributeSerializer(many=False, read_only=True)
    class Meta:
        model = AttrProduct
        fields = [
            'FK_Attribute', 'value'
        ]

class AttrPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttrPrice
        fields = [
            'description', 'id', 'value', 'extra_price', 'unit',
            'available', 'publish',
        ]

class ProductBannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductBanner
        fields = [
            'image', 'id'
        ]

class ProductCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['user' , 'product' , 
                  'description' , 'number_like'
                  , 'reply' , 'date_create'
                  ]

class SubMarketSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubMarket
        fields = [
            'title',
        ]

class ProductDetailSerializer(serializers.ModelSerializer):
    related_products = ProductSerializer(many=True, read_only=True)
    attributes = AttrProductSerializer(many=True, read_only=True)
    attributes_price = AttrPriceSerializer(many=True, read_only=True)
    banners = ProductBannerSerializer(many=True, read_only=True)
    comments = ProductCommentSerializer(many=True , read_only=True)
    sub_market = SubMarketSerializer(many=False, read_only=True)
    class Meta:
        model = Product
        fields = [
            'id', 'title', 'image', 'description', 'slug', 'price',
            'available', 'publish', 'get_discounted', 'related_products',
            'attributes', 'attributes_price', 'banners', 'reviews',
            'net_weight', 'weight_with_packing',  'length_with_packing',
            'height_with_packaging', 'story', 'width_with_packing','comments',
            'product_status', 'exception_post_range', 'post_range', 'sub_market' 
        ]
