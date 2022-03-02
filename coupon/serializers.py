from rest_framework import serializers
from coupon.models import Coupon, CouponUsage
from nakhll_market.models import Product



class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = (
            'code',
            'title',
            'description',
        )


class CouponUsageSerializer(serializers.ModelSerializer):
    coupon = serializers.SlugRelatedField(slug_field='code', read_only=True, many=False)
    class Meta:
        model = CouponUsage
        fields = (
            'coupon',
            'used_datetime',
            'price_applied',
        )
 
