from rest_framework import serializers
from nakhll_market.models import Product

class TorobProductListRequestSerializer(serializers.Serializer):
    page_unique = serializers.CharField(max_length=200, required=False, label='شناسه محصول', )
    page_url = serializers.CharField(max_length=200, required=False, label='لینک محصول', )
    page = serializers.IntegerField(required=False, label='شماره صفحه', )

class TorobProductListResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'title',
            'subtitle',
            'page_unique',
            'current_price',
            'old_price',
            'availability',
            'category_name',
            'image_link',
            'page_url',
            'short_desc',
            # 'spec',
            # 'registry',
            # 'guarantee'
        ]

