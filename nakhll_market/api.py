from nakhll_market.models import AmazingProduct, Product, Shop, Slider, Category
from nakhll_market.serializers import (
    AmazingProductSerializer, ProductSerializer, ShopSerializer,
    SliderSerializer, CategorySerializer
    )
from rest_framework import generics, routers, views, viewsets
from rest_framework import permissions, filters, mixins
from django.db.models import Q, F, Count
import random


class SliderViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SliderSerializer
    permission_classes = [permissions.AllowAny, ]
    search_fields = ('Location', )
    filter_backends = (filters.SearchFilter,)
    queryset = Slider.objects.filter(Publish=True)

class CategoryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny, ]

    def get_queryset(self):
        categories = Category.objects\
            .filter(Publish = True, Available = True, FK_SubCategory = None)\
            .annotate(product_count = Count('ProductCategory'))\
            .filter(product_count__gt=5)
        categories_id = list(categories\
            .values_list('id', flat=True))
        categories = categories\
            .filter(pk__in=random.sample(categories_id, 12))
        return categories

class AmazingProductViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = AmazingProductSerializer
    permission_classes = [permissions.AllowAny, ]

    def get_queryset(self):
        return AmazingProduct.objects.get_amazing_products()

class LastCreatedProductsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny, ]

    def get_queryset(self):
        return Product.objects\
            .filter(Publish = True, Available = True, OldPrice = '0', Status__in = ['1', '2', '3'])\
                .order_by('-DateCreate')[:12]

class LastCreatedDiscountedProductsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny, ]

    def get_queryset(self):
        return Product.objects\
            .filter(Publish = True, Available = True, Status__in = ['1', '2', '3'])\
            .exclude(OldPrice='0')\
            .order_by('-DateCreate')[:16]

class RandomShopsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny, ]

    def get_queryset(self):
        pubshopsquery = Shop.objects.filter(Publish = True, Available = True)\
            .annotate(product_count = Count('ShopProduct')).filter(product_count__gt=1)
        numpubshops = pubshopsquery.count()
        pubshops = []
        for i in random.sample(range(0, numpubshops), 12):
            pubshops.append(pubshopsquery[i])
        return pubshops

class MostDiscountPrecentageProductsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny, ]

    def get_queryset(self):
        return Product.objects\
            .get_most_discount_precentage_available_product()

class MostSoldShopsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = ShopSerializer
    permission_classes = [permissions.AllowAny, ]

    def get_queryset(self):
        return Shop.objects.most_last_week_sale_shops()
