import json
import jdatetime
from django.utils.timezone import localtime
from rest_framework import serializers
from logistic.models import Address
from logistic.serializers import AddressSerializer, ShopOwnerAddressSerializer
from coupon.models import Coupon
from coupon.serializers import CouponUsageSerializer
from nakhll_market.serializers import UserSerializer
from .models import Invoice, InvoiceItem


class InvoiceItemSerializer(serializers.ModelSerializer):
    """Serializer class for InvoiceItem model"""
    product = serializers.PrimaryKeyRelatedField(read_only=True)
    added_date_jalali = serializers.SerializerMethodField()
    added_time_jalali = serializers.SerializerMethodField()
    buyer = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    image_thumbnail = serializers.SerializerMethodField()
    shop_slug = serializers.SerializerMethodField()

    class Meta:
        model = InvoiceItem
        fields = [
            'id',
            'product',
            'slug',
            'name',
            'count',
            'price_with_discount',
            'weight',
            'price_without_discount',
            'barcode',
            'image',
            'image_thumbnail',
            'shop_slug',
            'shop_name',
            'added_date_jalali',
            'added_time_jalali',
            'buyer',
            'status']

    def get_added_date_jalali(self, obj):
        """Jalali format of added date"""
        jalali_datetime = jdatetime.datetime.fromgregorian(
            datetime=obj.added_datetime, locale='fa_IR')
        return jalali_datetime.strftime('%Y/%m/%d')

    def get_added_time_jalali(self, obj):
        """Jalali format of added time"""
        jalali_datetime = jdatetime.datetime.fromgregorian(
            datetime=obj.added_datetime, locale='fa_IR')
        return jalali_datetime.strftime('%H:%M')

    def get_buyer(self, obj):
        """Get buyer of invoice item"""
        return obj.invoice.user.get_full_name()

    def get_image(self, obj):
        """Get image of invoice item product or return default image"""
        if obj.product.image:
            return obj.product.image
        return 'https://nakhll.com/media/Pictures/default.jpg'

    def get_image_thumbnail(self, obj):
        """Get image thumbnail of invoice item product or return default"""
        if obj.product.image_thumbnail_url:
            return obj.product.image_thumbnail_url
        return 'https://nakhll.com/media/Pictures/default.jpg'

    def get_shop_slug(self, obj):
        """Get shop slug of invoice item product"""
        return obj.product.shop.slug


class InvoiceWriteSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating Invoice model"""
    address = serializers.PrimaryKeyRelatedField(
        queryset=Address.objects.all(), required=False)
    coupon = serializers.SlugRelatedField(
        slug_field='code',
        queryset=Coupon.objects.all(),
        required=False)

    class Meta:
        model = Invoice
        fields = (
            'address',
            'coupon',
        )


class InvoiceRetrieveSerializer(serializers.ModelSerializer):
    """Serializer for retrieving Invoice model details"""
    address = ShopOwnerAddressSerializer(many=False, read_only=True)
    coupon_usages = CouponUsageSerializer(read_only=True, many=True)
    user = UserSerializer(many=False, read_only=True)
    items = serializers.SerializerMethodField(method_name='get_invoie_items')
    receiver_mobile_number = serializers.SerializerMethodField()
    created_time_jalali = serializers.SerializerMethodField()
    created_date_jalali = serializers.SerializerMethodField()

    def get_receiver_mobile_number(self, obj):
        """Reciever mobile number of invoice buyer"""
        if obj.address_json:
            address = json.loads(obj.address_json)
            return address.get('receiver_mobile_number')
        return None

    def get_created_date_jalali(self, obj):
        """Jalali format of created date"""
        jalali_datetime = jdatetime.datetime.fromgregorian(
            datetime=obj.created_datetime, locale='fa_IR')
        return jalali_datetime.strftime('%Y/%m/%d')

    def get_created_time_jalali(self, obj):
        """Jalali format of created time"""
        time = obj.created_datetime
        time = localtime(obj.created_datetime)
        jalali_datetime = jdatetime.datetime.fromgregorian(
            datetime=time, locale='fa_IR')
        return jalali_datetime.strftime('%H:%M')

    def get_invoie_items(self, obj):
        """All invoice items as dictinary using InvoiceItemSerializer"""
        items = obj.items.order_by('product__FK_Shop')
        return InvoiceItemSerializer(items, many=True, read_only=True).data

    class Meta:
        model = Invoice
        fields = (
            'id',
            'items',
            'address',
            'address_json',
            'user',
            'payment_unique_id',
            'status',
            # 'inoivce_type',
            'invoice_price_with_discount',
            'invoice_price_without_discount',
            'coupon_usages',
            'logistic_price',
            'final_price',
            'created_date_jalali',
            'created_time_jalali',
            'coupons_total_price',
            'payment_request_datetime',
            'receiver_mobile_number',
            'logistic_unit_details',
        )


class InvoiceProviderRetrieveSerializer(serializers.ModelSerializer):
    """Serializer for Invoice model for shop owner of invioce

    This serializer is used for shop owner of invoice. Shop owner is passed
    to this serializer as context. Any data of invoice will be filtered for
    this shop owner.
    """
    address = AddressSerializer(many=False, read_only=True)
    coupon_usages = CouponUsageSerializer(read_only=True, many=True)
    user = UserSerializer(many=False, read_only=True)
    items = serializers.SerializerMethodField(method_name='get_invoie_items')
    receiver_mobile_number = serializers.SerializerMethodField()
    created_time_jalali = serializers.SerializerMethodField()
    created_date_jalali = serializers.SerializerMethodField()
    final_price = serializers.SerializerMethodField()
    invoice_price_with_discount = serializers.SerializerMethodField()
    invoice_price_without_discount = serializers.SerializerMethodField()

    def get_final_price(self, obj):
        """Final price of invoice

        Only products that is belogs to shop owner will be calculated
        """
        user = self.context.get('request').user
        total = 0
        for item in obj.items.filter(product__FK_Shop__FK_ShopManager=user):
            price = item.product.Price
            total += price
        return total

    def get_receiver_mobile_number(self, obj):
        """Get receiver mobile number of invoice buyer"""
        if obj.address_json:
            address = json.loads(obj.address_json)
            return address.get('receiver_mobile_number')
        return None

    def get_created_date_jalali(self, obj):
        """Jalali format of created date"""
        jalali_datetime = jdatetime.datetime.fromgregorian(
            datetime=obj.created_datetime, locale='fa_IR')
        return jalali_datetime.strftime('%Y/%m/%d')

    def get_created_time_jalali(self, obj):
        """Jalali format of created time"""
        jalali_datetime = jdatetime.datetime.fromgregorian(
            datetime=obj.created_datetime, locale='fa_IR')
        return jalali_datetime.strftime('%H:%M')

    def get_invoie_items(self, obj):
        """All invoice items as dictinary using InvoiceItemSerializer

        Only items that is belogs to shop owner will be returned.
        """
        user = self.context.get('request').user
        items = obj.items.filter(
            product__FK_Shop__FK_ShopManager=user).order_by('product__FK_Shop')
        return InvoiceItemSerializer(items, many=True, read_only=True).data

    def get_invoice_price_with_discount(self, obj):
        """Get invoice price with discount

        Only products that is belogs to shop owner will be calculated.
        """
        user = self.context.get('request').user
        total = 0
        for item in obj.items.filter(product__FK_Shop__FK_ShopManager=user):
            price = item.product.Price
            total += price
        return total

    def get_invoice_price_without_discount(self, obj):
        """Get invoice price without discount

        Only products that is belogs to shop owner will be calculated.
        """
        user = self.context.get('request').user
        total = 0
        for item in obj.items.filter(product__FK_Shop__FK_ShopManager=user):
            oldprice = item.product.OldPrice
            price = item.product.Price
            total += oldprice or price
        return total

    class Meta:
        model = Invoice
        fields = (
            'id',
            'items',
            'address',
            'address_json',
            'user',
            'payment_unique_id',
            'status',
            'invoice_price_with_discount',
            'invoice_price_without_discount',
            'coupon_usages',
            'logistic_price',
            'final_price',
            'created_date_jalali',
            'created_time_jalali',
            'coupons_total_price',
            'payment_request_datetime',
            'receiver_mobile_number',
            'logistic_unit_details',
        )


class BarcodeSerializer(serializers.ModelSerializer):
    """Barcode serializer"""
    class Meta:
        model = InvoiceItem
        fields = ('barcode', )
