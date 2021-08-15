from rest_framework import serializers
from coupon.models import Coupon, CouponUsage



# class CouponSerializers(serializers.ModelSerializer):
#     cart = serializers.PrimaryKeyRelatedField(read_only=True)
#     product = serializers.PrimaryKeyRelatedField(many=False, read_only=False, queryset=Product.objects.all())
#     class Meta:
#         model = Coupon
#         fields = (
#             'code',
#             'valid_from',
#             'valid_to',
#             'max_count',
#             'is_publish',
#             'price',
#             'min_price',
#             'max_price',
#             'user',
#             'shop',
#             'product',
#             'description',
#         )


