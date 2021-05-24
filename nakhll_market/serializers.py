from rest_framework import serializers
from rest_framework.utils import field_mapping
from nakhll_market.models import (
    AmazingProduct, AttrPrice, AttrProduct, Attribute,
    Category, Product, ProductBanner, Shop, Slider, Comment
    )

# landing serializers
class SliderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Slider
        fields = [
            'url', 'image', 'title', 'show_info', 'description', 'Location',
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
            'slug', 'title', 'get_absolute_url', 'Image_thumbnail_url',
            'state'
        ]

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'Image_thumbnail_url', 'get_url', 'old_price', 'price', 'slug',
            'title', 'status', 'get_discounted', 'id'
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
            'dscription', 'id', 'value', 'extra_price', 'unit',
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



class ProductDetailSerializer(serializers.ModelSerializer):
    get_related_products = ProductSerializer(many=True, read_only=True)
    Product_Attr = AttrProductSerializer(many=True, read_only=True)
    AttrPrice_Product = AttrPriceSerializer(many=True, read_only=True)
    Product_Banner = ProductBannerSerializer(many=True, read_only=True)
    Product_Comment = ProductCommentSerializer(many=True , read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'title', 'image', 'description', 'slug', 'price',
            'available', 'publish', 'get_discounted', 'get_related_products',
            'Product_Attr', 'AttrPrice_Product', 'Product_Banner',
            'Product_Review', 'net_weight' , 'weight_with_packing' , 
            'length_with_packing' , 'height_with_packaging' , 'story' , 'width_with_packin','Product_Comment' , 
            'product_status' , 'exception_post_range' , 'post_range' 
        

        ]
