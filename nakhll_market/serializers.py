from django.contrib.auth.models import User
from django.db.models import fields
from rest_framework import serializers
from rest_framework.relations import HyperlinkedIdentityField, HyperlinkedRelatedField
from rest_framework.utils import field_mapping
from nakhll_market.models import (
    AmazingProduct, AttrPrice, AttrProduct, Attribute,
    Category, Market, PostRange, Product, ProductBanner, Shop, Slider, Comment,
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
            'id', 'Slug', 'title', 'url', 'image_thumbnail',
        ]

class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = [
            'slug', 'title', 'url', 'image_thumbnail_url',
            'state'
        ]

class CreateShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ['Slug', 'Title', 'State', 'BigCity', 'City', ]
   

class ProductSerializer(serializers.ModelSerializer):
    shop = ShopSerializer(many=False, read_only=True)
    class Meta:
        model = Product
        fields = [
            'image_thumbnail_url', 'url', 'old_price', 'price', 'slug',
            'title', 'status', 'discount', 'id', 'shop'
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

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name',
        ]

class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False, read_only=True)
    class Meta:
        model = Comment
        fields = [
            'user', 'description', 'number_like',
            'date_create',
        ]

class ProductCommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False, read_only=True)
    reply = CommentSerializer(many=False, read_only=True)
    class Meta:
        model = Comment
        fields = [
            'user', 'description', 'number_like',
            'reply', 'date_create',
        ]

class MarketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Market
        fields = [
            'title', 'url', 'id',
        ]

class SubMarketSerializer(serializers.ModelSerializer):
    market = MarketSerializer(many=False, read_only=False)
    class Meta:
        model = SubMarket
        fields = [
            'title', 'market', 'url', 'id'
        ]

class PostRangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostRange
        fields = [
            'state', 'big_city', 'city'
        ]

class ProductDetailSerializer(serializers.HyperlinkedModelSerializer):
    related_products = ProductSerializer(many=True, read_only=True)
    attributes = AttrProductSerializer(many=True, read_only=True)
    attributes_price = AttrPriceSerializer(many=True, read_only=True)
    banners = ProductBannerSerializer(many=True, read_only=True)
    comments = ProductCommentSerializer(many=True , read_only=True)
    sub_market = SubMarketSerializer(many=False, read_only=True)
    shop = ShopSerializer(many=False, read_only=False)
    post_range = PostRangeSerializer(many=True, read_only=True)
    exception_post_range = PostRangeSerializer(many=True, read_only=True)
    class Meta:
        model = Product
        fields = [
            'id', 'title', 'image', 'description', 'slug', 'price',
            'available', 'publish', 'discount', 'related_products',
            'attributes', 'attributes_price', 'banners', 'reviews',
            'net_weight', 'weight_with_packing',  'length_with_packing',
            'height_with_packaging', 'story', 'width_with_packing','comments',
            'status', 'exception_post_range', 'post_range', 'sub_market',
            'shop',
        ]


class ProductListSerializer(serializers.ModelSerializer):
    # FK_User = serializers.SlugRelatedField(slug_field='username', queryset=User.objects.all())
    category = CategorySerializer(many=True, read_only=True)
    shop = serializers.SlugRelatedField(slug_field='Slug', read_only=True)
    class Meta:
        model = Product
        fields = [
            'id',
            'title',
            'slug',
            'inventory',
            'category',
            'image_thumbnail_url',
            'price',
            'shop',
            'old_price',
            'net_weight',
            'weight_with_packing',
            'description',
            'status',
            'post_range_type',
            'preparation_days',
            'comments_count',
            'average_user_point',
            'total_sell',
        ]
class ProductWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'ID',
            'Title',
            'Slug',
            'Inventory',
            'Price',
            'OldPrice',
            'Net_Weight',
            'Weight_With_Packing',
            'Description',
            'Status',
            'PostRangeType',
            'PreparationDays',
            'FK_Shop'
        ]

class FullMarketSerializer(serializers.ModelSerializer):
    submarkets = SubMarketSerializer(many=True, read_only=True)
    class Meta:
        model = Market
        fields = [
            'id',
            'title',
            'description',
            'image',
            'slug',
            'url',
            'submarkets',
        ]


class ProductCategorySerializer(serializers.Serializer):
    product = serializers.SlugField()
    categories = serializers.ListField(
        child=serializers.IntegerField(min_value=0)
    )


class ProductImagesSerializer(serializers.Serializer):
    product = serializers.SlugField()
    images = serializers.ImageField()


class ProductPriceWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['Slug', 'OldPrice', 'Price' ] 
        extra_kwargs = {
            'Slug': {'validators': []},
        }

class ProductInventoryWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['Slug', 'Inventory'] 
        extra_kwargs = {
            'Slug': {'validators': []},
        }


