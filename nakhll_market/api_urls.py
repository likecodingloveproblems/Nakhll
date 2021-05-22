from django.urls import re_path, include, path
from nakhll_market.api import (
    AmazingProductViewSet, CategoryViewSet, LastCreatedDiscountedProductsViewSet,
    LastCreatedProductsViewSet, MostDiscountPrecentageProductsViewSet,
    ProductDetailsViewSet, ProductsInSameFactorViewSet, SliderViewSet,
    MostSoldShopsViewSet, RandomShopsViewSet, RandomProductsViewSet
    )
from rest_framework import routers

app_name = 'nakhll_market'

landing_router = routers.DefaultRouter()
landing_router.register(r'sliders', SliderViewSet, basename="sliders")
landing_router.register(r'categories', CategoryViewSet, basename="categories")
landing_router.register(r'amazing-products', AmazingProductViewSet, basename="amazing-products")
landing_router.register(r'last-created-products', LastCreatedProductsViewSet, basename="last-created-products")
landing_router.register(r'last-created-discounted-products', LastCreatedDiscountedProductsViewSet, basename="last-created-discounted-products")
landing_router.register(r'most-discount-prec-products', MostDiscountPrecentageProductsViewSet, basename="most-discount-prec-products")
landing_router.register(r'most-sold-shops', MostSoldShopsViewSet, basename="most-sold-shops")
landing_router.register(r'random-shops', RandomShopsViewSet, basename="random-shops")
landing_router.register(r'random-products', RandomProductsViewSet, basename="random-products")

product_page_router = routers.DefaultRouter()
product_page_router.register(r'details', ProductDetailsViewSet, basename="details")

urlpatterns = [
    path('landing/', include(landing_router.urls)),
    path('product-page/', include(product_page_router.urls)),
    path('product-page/same-factor/<uuid:ID>/',ProductsInSameFactorViewSet.as_view() )
]
