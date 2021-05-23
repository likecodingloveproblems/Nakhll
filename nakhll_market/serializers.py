from rest_framework import serializers
from nakhll_market.models import (
    AmazingProduct, AttrPrice, AttrProduct, Attribute,
    Category, Product, ProductBanner, Shop, Slider,
    )

# landing serializers
class SliderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Slider
        fields = [
            'URL', 'Image', 'Title', 'ShowInfo', 'Description', 'Location',
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
            'Slug', 'Title', 'get_absolute_url', 'Image_thumbnail_url',
        ]

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'Image_thumbnail_url', 'get_url', 'OldPrice', 'Price', 'Slug',
            'Title', 'Status', 'get_discounted', 'ID'
        ]

class AmazingProductSerializer(serializers.ModelSerializer):
    product = ProductSerializer(many=False, read_only=True)
    class Meta:
        model = AmazingProduct
        fields = [
            'product', 'start_date', 'end_date'
        ]

# product page serializer
class AttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attribute
        fields = [
            'Title', 'Unit'
        ]

class AttrProductSerializer(serializers.ModelSerializer):
    FK_Attribute = AttributeSerializer(many=False, read_only=True)
    class Meta:
        model = AttrProduct
        fields = [
            'FK_Attribute', 'Value'
        ]

class AttrPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttrPrice
        fields = [
            'count', 'Description', 'id', 'Value', 'ExtraPrice', 'Unit',
        ]

class ProductBannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductBanner
        fields = [
            'Image', 'id'
        ]


class ProductDetailSerializer(serializers.ModelSerializer):
    get_related_products = ProductSerializer(many=True, read_only=True)
    Product_Attr = AttrProductSerializer(many=True, read_only=True)
    AttrPrice_Product = AttrPriceSerializer(many=True, read_only=True)
    Product_Banner = ProductBannerSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'ID', 'Title', 'Image', 'Description', 'Slug', 'Price',
            'Available', 'Publish', 'get_discounted', 'get_related_products',
            'Product_Attr', 'AttrPrice_Product', 'Product_Banner',
            'Product_Comment', 'Product_Review',
        ]
