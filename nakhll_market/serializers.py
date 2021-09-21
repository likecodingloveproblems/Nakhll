from django.shortcuts import get_object_or_404
from nakhll_market.serializer_fields import Base64ImageField
from restapi.serializers import BigCitySerializer, ProfileSerializer, UserDetailSerializer
from django.contrib.auth.models import User
from django.db.models import fields, query
from rest_framework import serializers
from rest_framework.relations import HyperlinkedIdentityField, HyperlinkedRelatedField
from rest_framework.utils import field_mapping
from nakhll_market.models import (
    Alert, AmazingProduct, AttrPrice, AttrProduct, Attribute, BankAccount, BigCity, City, ShopBankAccount, ShopSocialMedia,
    Category, Market, PostRange, Product, ProductBanner, Profile, Shop, ShopBankAccount, Slider, Comment,
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
            'state', 'show_contact_info', 'publish', 'available'
        ]

class CreateShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ['Slug', 'Title', 'State', 'BigCity', 'City', 'show_contact_info']
        extra_kwargs = {
            'Slug': {'validators': [], 'allow_null': True, 'required': False}
        }
   

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

class SimplePostRangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostRange
        fields = ['city', ]


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
    sub_market = SubMarketSerializer(read_only=True)
    shop = serializers.SlugRelatedField(slug_field='Slug', read_only=True)
    banners = ProductBannerSerializer(read_only=True, many=True)
    post_range_cities = BigCitySerializer(many=True, read_only=True)
    class Meta:
        model = Product
        fields = [
            'id',
            'title',
            'slug',
            'inventory',
            'category',
            'sub_market',
            'banners',
            'image_thumbnail_url',
            # 'Image',
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
            'publish',
            'available',
            'post_range_cities'
        ]
    # Image = serializers.SerializerMethodField(method_name='get_absolute_image_url')
    # def get_absolute_image_url(self, product):
        # request = self.context.get('request')
        # photo_url = product.Image.url if product.Image else None
        # return request.build_absolute_uri(photo_url)

class ProductSubMarketSerializer(serializers.Serializer):
    product = serializers.UUIDField()
    submarkets = serializers.ListField(
        child=serializers.UUIDField()
    )

class ProductImagesSerializer(serializers.Serializer):
    product = serializers.UUIDField()
    images = serializers.ListField(
        child=Base64ImageField(max_length=None, use_url=True)
    )

class ProductBannerSerializer(serializers.ModelSerializer):
    FK_Product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), pk_field=serializers.UUIDField(format='hex'))
    Image = Base64ImageField(max_length=None, use_url=True)
    class Meta:
        model = ProductBanner
        fields = [
            'id', 'Image', 'FK_Product'
        ]



class Base64ImageSerializer(serializers.Serializer):
    image = Base64ImageField(max_length=None, use_url=True)

class ProductUpdateSerializer(serializers.ModelSerializer):
    # FK_Shop = serializers.SlugRelatedField(slug_field='Slug', many=False, read_only=True)
    FK_SubMarket = serializers.PrimaryKeyRelatedField(read_only=False, many=False, queryset=SubMarket.objects.all())
    Product_Banner = serializers.PrimaryKeyRelatedField(queryset=ProductBanner.objects.all(), many=True, read_only=False)
    post_range = serializers.PrimaryKeyRelatedField(source='post_range_cities', read_only=False, many=True, queryset=BigCity.objects.all())
    class Meta:
        model = Product
        fields = [
            'ID',
            'Title',
            'Inventory',
            'Price',
            'OldPrice',
            'Net_Weight',
            'Weight_With_Packing',
            'Description',
            'Status',
            'PostRangeType',
            'PreparationDays',
            'FK_SubMarket',
            'Product_Banner',
            'post_range'
        ]
    def update(self, instance, validated_data):
        # Direct assignment to the reverse side of a related set is prohibited, 
        # so I am deleteing related ProductBanner objects to clean database from
        # ProductBanners that have no Product assigned to
        product_banners = validated_data.pop('Product_Banner')
        deleted_banners = [banner.delete() 
                           for banner in instance.Product_Banner.all() 
                           if banner not in product_banners]

        for prop in validated_data:
            setattr(instance, prop, validated_data[prop])
        instance.save()
        return instance


class ProductWriteSerializer(serializers.ModelSerializer):
    FK_Shop = serializers.SlugRelatedField(slug_field='Slug', many=False, read_only=False, queryset=Shop.objects.all())
    post_range = serializers.PrimaryKeyRelatedField(source='post_range_cities', read_only=False, many=True, queryset=BigCity.objects.all())
    class Meta:
        model = Product
        fields = [
            'ID',
            'Title',
            'Inventory',
            'Price',
            'OldPrice',
            'Net_Weight',
            'Weight_With_Packing',
            'Description',
            'Status',
            'PostRangeType',
            'PreparationDays',
            'FK_Shop',
            'post_range'
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
    product = serializers.UUIDField()
    categories = serializers.ListField(
        child=serializers.IntegerField(min_value=0)
    )


class ShopFullSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True, many=False)
    sub_market = SubMarketSerializer(read_only=True, many=True)
    class Meta:
        model = Shop
        fields = [
            'title', 'slug', 'url', 'description', 'profile', 'image_thumbnail_url',
            'state', 'sub_market',
        ]

class ShopBankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopBankAccount
        fields = ['iban', 'owner']
class ShopSocialMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopSocialMedia
        fields = ['telegram', 'instagram']

class SettingsProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['NationalCode', 'MobileNumber', 'PhoneNumber', 'State', 'BigCity', 'City', 'Address', 'ZipCode']
        extra_kwargs = {
            'NationalCode': {'validators': []},
            'MobileNumber': {'validators': []}
        }

class UserProfileSerializer(serializers.ModelSerializer):
    User_Profile = SettingsProfileSerializer(read_only=False)
    class Meta:
        model = User
        fields = ['User_Profile']
class ShopSettingsSerializer(serializers.ModelSerializer):
    FK_ShopManager = UserProfileSerializer(read_only=False)
    class Meta:
        model = Shop
        fields = [
            'Title', 'Slug', 'Description', 'FK_ShopManager', 
        ]
        extra_kwargs = {
            'Slug': {'validators': []},
        }

class ShopAllSettingsSerializer(serializers.ModelSerializer):
    FK_ShopManager = UserProfileSerializer(read_only=False)
    bank_account = ShopBankAccountSerializer(read_only=True)
    social_media = ShopSocialMediaSerializer(read_only=True)
    class Meta:
        model = Shop
        fields = [
            'Title', 'Slug', 'Description', 'FK_ShopManager', 'bank_account', 'social_media', 'image_thumbnail_url' 
        ]
        extra_kwargs = {
            'Slug': {'validators': []},
        }
    def update(self, instance, validated_data):
        user = validated_data.get('FK_ShopManager')
        if not user:
            return instance

        profile_data = user.get('User_Profile')
        if not profile_data:
            return instance

        instance.Title = validated_data.get('Title')
        instance.Description = validated_data.get('Description')

        profile = instance.FK_ShopManager.User_Profile
        profile.NationalCode = profile_data.get('NationalCode')
        profile.MobileNumber = profile_data.get('MobileNumber')
        profile.PhoneNumber = profile_data.get('PhoneNumber')
        profile.State = profile_data.get('State')
        profile.BigCity = profile_data.get('BigCity')
        profile.City = profile_data.get('City')
        profile.Address = profile_data.get('Address')
        profile.ZipCode = profile_data.get('ZipCode')

        profile.save()
        instance.save()
        return instance
            
class ShopBankAccountSettingsSerializer(serializers.ModelSerializer):
    bank_account = ShopBankAccountSerializer(read_only=False)
    class Meta:
        model = Shop
        fields = ['bank_account', ]
    def update(self, instance, validated_data):
        bank_account_data = validated_data.get('bank_account')
        if not bank_account_data:
            return instance
        bank_account, created = ShopBankAccount.objects.get_or_create(shop=instance)
        bank_account.iban = bank_account_data.get('iban')
        bank_account.owner = bank_account_data.get('owner')
        bank_account.save()
        return instance
 
class SocialMediaAccountSettingsSerializer(serializers.ModelSerializer):
    social_media = ShopSocialMediaSerializer(read_only=False)
    class Meta:
        model = Shop
        fields = ['social_media', ]
    def update(self, instance, validated_data):
        social_media_data = validated_data.get('social_media')
        if not social_media_data:
            return instance
        social_media, created = ShopSocialMedia.objects.get_or_create(shop=instance)
        social_media.telegram = social_media_data.get('telegram')
        social_media.instagram = social_media_data.get('instagram')
        social_media.save()
        return instance
 


 

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


