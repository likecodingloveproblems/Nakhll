from rest_framework import serializers
from coupon.models import Coupon, CouponUsage
from nakhll_market.models import Product


class CouponSerializer(serializers.ModelSerializer):
    """Serializer for Coupon model"""
    class Meta:
        model = Coupon
        fields = (
            'code',
            'title',
            'description',
        )


class GiftCouponSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=100)
    mobile = serializers.CharField(max_length=11)


class CouponUsageSerializer(serializers.ModelSerializer):
    """Serializer for CouponUsage model"""
    coupon = serializers.SlugRelatedField(
        slug_field='code', read_only=True, many=False)

    class Meta:
        model = CouponUsage
        fields = (
            'coupon',
            'used_datetime',
            'price_applied',
        )
