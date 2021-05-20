from django.urls import re_path, include, path
from nakhll_market.api import (
    AmazingProductViewSet, CategoryViewSet, LastCreatedDiscountedProductsViewSet,
    LastCreatedProductsViewSet, MostDiscountPrecentageProductsViewSet, SliderViewSet,
    MostSoldShopsViewSet, RandomShopsViewSet
    )
from rest_framework import routers

app_name = 'nakhll_market'

router = routers.DefaultRouter()
router.register(r'sliders', SliderViewSet, basename="sliders")
router.register(r'categories', CategoryViewSet, basename="categories")
router.register(r'amazing-products', AmazingProductViewSet, basename="amazing-products")
router.register(r'last-created-products', LastCreatedProductsViewSet, basename="last-created-products")
router.register(r'last-created-discounted-products', LastCreatedDiscountedProductsViewSet, basename="last-created-discounted-products")
router.register(r'most-discount-prec-products', MostDiscountPrecentageProductsViewSet, basename="most-discount-prec-products")
router.register(r'most-sold-shops', MostSoldShopsViewSet, basename="most-sold-shops")
router.register(r'random-shops', RandomShopsViewSet, basename="random-shops")

urlpatterns = [
    path('landing/', include(router.urls)),
]
