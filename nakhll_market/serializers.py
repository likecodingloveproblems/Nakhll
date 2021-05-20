from django.db.models import fields
from nakhll_market.models import AmazingProduct, Category, Product, Profile, Slider
from rest_framework import serializers


class SliderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Slider
        fields = [
            'URL', 'Image', 'Title', 'ShowInfo', 'Description', 'Location',
            ]

class CategorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Category
        fields = [
            'Slug', 'Title', 'url', 'Image_thumbnail_url',
        ]

class ShopSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Category
        fields = [
            'Slug', 'Title', 'get_absolute_url', 'Image_thumbnail_url',
        ]

class ProductSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Product
        fields = [
            'Image_thumbnail_url', 'get_url', 'OldPrice', 'Price', 'Slug',
            'Title', 'Status',
        ]

class AmazingProductSerializer(serializers.HyperlinkedModelSerializer):
    product = ProductSerializer(many=False, read_only=True)
    class Meta:
        model = AmazingProduct
        fields = [
            'product', 'start_date', 'end_date'
        ]
