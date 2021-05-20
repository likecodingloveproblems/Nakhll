from nakhll_market.models import AmazingProduct, Slider, Category
from nakhll_market.serializers import AmazingProductSerializer, SliderSerializer, CategorySerializer
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
        amazing_products = AmazingProduct.objects.get_amazing_products()
        return amazing_products
