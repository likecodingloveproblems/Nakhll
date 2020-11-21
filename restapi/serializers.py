from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from django.contrib.auth.models import User
from nakhll_market.models import Profile , Product , Shop , SubMarket , Category , BankAccount , ShopBanner , Attribute , AttrProduct , AttrPrice , ProductBanner , User_View , PageViews , PostRange , Message , User_Message_Status, OptinalAttribute, Details
from Payment.models import Factor , Wallet , FactorPost , Transaction , PostBarCode , Coupon
import re
from rest_framework.exceptions import  ValidationError 
from rest_framework.fields import CurrentUserDefault


# user and profile and home page 
class UserDetailSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
        ]
        read_only_fields = [
            'username',
        ]



class BankAccountSerializer(ModelSerializer):
    class Meta:
        model = BankAccount
        fields = [
            'CreditCardNumber',
            'ShabaBankNumber',
            'AccountOwner',
        ]



class ProfileSerializer(ModelSerializer):
    FK_User = UserDetailSerializer(read_only = True)

    class Meta:
        model = Profile 
        fields = [
            'ID',
            'FK_User',
            'Sex',
            'MobileNumber',
            'ZipCode',
            'NationalCode',
            'Address',
            'State',
            'BigCity',
            'City',
            'BrithDay',
            'CityPerCode',
            'PhoneNumber',
            'Bio',
            'Image_thumbnail_url',
            'UserReferenceCode',
            'Point',
            'TutorialWebsite',
            'get_bank_account_name',
            'get_credit_card_number',
            'get_shaba_number',
            ]
        read_only_fields = [
            'ID',
            'MobileNumber',
            'NationalCode',
        ]


class WalletSerializer(ModelSerializer):
    class Meta:
        model = Wallet
        fields = [
            'Inverntory',
        ]
        read_only_fields = [
            'Inverntory',
        ]



class ShopListHomeSerializer(ModelSerializer):
    class Meta:
        model = Shop
        fields = [
            'ID',
            'Title',
            'Slug',
            'Image_thumbnail_url',
            'Point',
            'Available',
            'Publish',
        ]


class ProductListHomeSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'ID',
            'Title',
            'Slug',
            'Image_medium_url',
            'Price',
            'OldPrice',
            'Point',
            'Available',
            'Publish',
        ]


class ProductTitleSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'Title'
        ]


#factor and payment section
class FactorPostSerializer(ModelSerializer):
    FK_Product = ProductTitleSerializer(read_only = True)
    class Meta:
        model = FactorPost
        fields = [
            'FK_Product',
            'ProductCount',
            'get_total_item_price',
            'Description',
            'get_one_price',
            'EndPrice',
        ]

class CouponSerializer(ModelSerializer):
    class Meta:
        model = Coupon
        fields = [
            'Title',
            'Description',
            'SerialNumber',
            'StartDate',
            'EndDate',
            'DiscountType',
            'DiscountRate',
            'DiscountStatus',
            'MinimumAmount',
            'MaximumAmount',
            'NumberOfUse',
        ]

class FactorListSerializer(ModelSerializer):
    FK_FactorPost = FactorPostSerializer(read_only=True, many=True)
    FK_Coupon = CouponSerializer(read_only=True, many=False)
    class Meta:
        model = Factor
        fields = [
            'ID',
            'FactorNumber',
            'FK_User',
            'Description',
            'MobileNumber',
            'ZipCode',
            'Address',
            'CityPerCode',
            'City',
            'BigCity',
            'State',
            'PhoneNumber',
            'FK_FactorPost',
            'FK_Coupon',
            'DiscountRate',
            'DiscountType',
            'PostPrice',
            'OrderDate',
            'OrderStatus',
            'Checkout',
        ]

class FactorDesSerializer(ModelSerializer):
    FK_FactorPost = FactorPostSerializer(read_only=True, many=True)
    FK_Coupon = CouponSerializer(read_only=True)
    class Meta:
        model = Factor
        fields = [
            'ID',
            'FactorNumber',
            'FK_User',
            'Description',
            'MobileNumber',
            'ZipCode',
            'Address',
            'CityPerCode',
            'City',
            'State',
            'PhoneNumber',
            'FK_FactorPost',
            'FactorType',
            'ShopInfo',
            'FK_Coupon',
            'DiscountRate',
            'DiscountType',
            'FK_Campaign',
            'PostPrice',
            'TotalPrice',
            'PaymentStatus',
            'OrderStatus',
            'Checkout'
        ]

class FactorDetailsSerializer(ModelSerializer):
    FK_Coupon = CouponSerializer(read_only=True)
    class Meta:
        model = Factor
        fields = [
            'ID',
            'FactorNumber',
            'Description',
            'MobileNumber',
            'ZipCode',
            'Address',
            'CityPerCode',
            'City',
            'BigCity',
            'State',
            'PhoneNumber',
            'FK_Coupon',
            'DiscountRate',
            'DiscountType',
            'PostPrice',
            'TotalPrice',
            'OrderDate'
        ]

class TransactionSerializer(ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            'Description',
            'Price',
            'Type',
            'Date',
        ]

class PostBarCodeSerializer(ModelSerializer):
    class Meta:
        model = PostBarCode
        fields = [
            'FK_Factor',
            'User_Sender',
            'FK_Shops',
            'BarCode',
            'PostPrice',
        ]

class SubMarketSerializer(ModelSerializer):
    class Meta:
        model = SubMarket
        fields = [
            'ID',
            'Title',
            'Description',
            'Slug',
        ]

class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = [
            'id',
            'Title',
            'Description',
            'Slug',
        ]


        
# shop and product detail 
class ShopBannerSerializer(ModelSerializer):
    class Meta:
        model = ShopBanner
        fields = [
            'id',
            'FK_Shop',
            'Title',
            'Description',
            'URL',
            'Image',
            'Publish',
        ]

class AttributeSerializer(ModelSerializer):
    class Meta:
        model = Attribute
        fields = [
            'id',
            'Title',
            'Unit',
        ]

class AttrProductSerializer(ModelSerializer):
    class Meta:
        model = AttrProduct
        fields = [
            'id',
            'get_attribute_title',
            'Value',
            'get_attribute_unit',
        ]

class AttrPriceSerializer(ModelSerializer):
    class Meta:
        model = AttrPrice
        fields = [
            'id',
            'Value',
            'ExtraPrice',
            'Unit',
            'Description',
            'Available',
        ]

class DetailsSerializer(ModelSerializer):
    class Meta:
        model = Details
        fields = '__all__'

class OptionalAttributeSerializer(ModelSerializer):
    FK_Details = DetailsSerializer(many = True)
    class Meta:
        model = OptinalAttribute
        fields = [
            'id',
            'Title',
            'Type',
            'Status',
            'FK_Details',
        ]

class ProductBannerSerializer(ModelSerializer):
    class Meta:
        model = ProductBanner
        fields = [
            'id',
            'Image',
        ]

class User_ViewSerializer(ModelSerializer):
    class Meta:
        model = User_View
        fields = [
            'User_Ip',
            'DateTime',
        ]

class PageViewsSerializer(ModelSerializer):
    class Meta:
        model = PageViews
        fields = [
            'Object_Slug',
            'Object_Type',
            'View_Count',
        ]

class PostRangeSerializer(ModelSerializer):
    class Meta:
        model = PostRange
        fields = [
            'id',
            'State',
            'BigCity',
            'City',
        ]

class ShopDetailSerializer(ModelSerializer):
    FK_SubMarket = SubMarketSerializer(many = True)
    class Meta:
        model = Shop
        fields = [
            'ID',
            'Title',
            'FK_SubMarket',
            'Slug',
            'Description',
            'Image_thumbnail_url',
            'Bio',
            'State',
            'BigCity',
            'City',
            'Point',
            'Holidays',
            'Available',
            'Publish',
        ]

class ProductDetailSerializer(ModelSerializer):
    FK_PostRange = PostRangeSerializer(many=True)
    FK_ExceptionPostRange = PostRangeSerializer(many=True)
    FK_SubMarket = SubMarketSerializer(read_only=True)
    FK_Category = CategorySerializer(read_only=True, many=True)
    Attribute = serializers.SerializerMethodField('get_attribute')
    Price_Attribute = serializers.SerializerMethodField('get_price_attribute')
    class Meta:
        model = Product
        fields = [
            'ID',
            'Title',
            'Slug',
            'FK_SubMarket',
            'Story',
            'Description',
            'Bio',
            'Point',
            'Image_medium_url',
            'FK_Shop',
            'FK_Category',
            'Price',
            'OldPrice',
            'PostRangeType',
            'Status',
            'Available',
            'Publish',
            'FK_PostRange',
            'FK_ExceptionPostRange',
            'Net_Weight',
            'Weight_With_Packing',
            'Length_With_Packaging',
            'Width_With_Packaging',
            'Height_With_Packaging',
            'Inventory',
            'Attribute',
            'Price_Attribute',
        ]
    def get_attribute(self, this_product):
        queryset = AttrProduct.objects.filter(FK_Product = this_product, Available = True)
        serializer = AttrProductSerializer(instance = queryset, many = True)
        return serializer.data
    def get_price_attribute(self, this_product):
        queryset = AttrPrice.objects.filter(FK_Product = this_product, Publish = True)
        serializer = AttrPriceSerializer(instance = queryset, many = True)
        return serializer.data


class User_Message_StatusSerializer(ModelSerializer):
    class Meta:
        model = User_Message_Status
        fields = [
            'FK_User',
            'SeenStatus',
        ]

class MessageSerializer(ModelSerializer):

    class Meta:
        model = Message
        fields = [
            'id',
            'Title',
            'Text',
            'Date',
        ]





# //////////// web cart navbar view
class ShopCartView(ModelSerializer):
    class Meta:
        model = Shop
        fields = [
            'Slug',
        ]

class ProductCartView(ModelSerializer):
    FK_Shop = ShopCartView(read_only=True)
    class Meta:
        model = Product
        fields = [
            'Title',
            'Slug',
            'FK_Shop',
            'Image_thumbnail_url'
        ]

class FactorPostCartView(ModelSerializer):
    FK_Product = ProductCartView(read_only=True)
    class Meta:
        model = FactorPost
        fields = [
            'FK_Product',
            'ProductCount',
            'get_total_item_price'

        ]


class FactorCartView(ModelSerializer):
    FK_FactorPost = FactorPostCartView(read_only=True, many=True)
    class Meta:
        model = Factor
        fields = [
            'FK_FactorPost',
        ]


class PostRangeShowString(ModelSerializer):
    class Meta:
        model = PostRange
        fields = [
            'id',
            'State',
            'BigCity',
            'City',
        ]

class ShopDetailForPoint(ModelSerializer):
    class Meta:
        model = Shop
        fields = [
            'ID',
            'Title',
            'Image_thumbnail_url',
            'get_url',
        ]

class PointSerializer(ModelSerializer):
    FK_Shop = ShopDetailForPoint(read_only = True)
    class Meta:
        model = Product
        fields = [
            'ID',
            'Title',
            'get_url',
            'Image_thumbnail_url',
            'FK_Shop',
        ]

class ProductSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'ID',
            'Title',
            'Slug',
            'Image_medium_url',
            'Price',
            'Status',
        ]

class ShopSubMarketsSerializer(ModelSerializer):
    class Meta:
        model = SubMarket
        fields = [
            'ID',
            'Title',
        ]