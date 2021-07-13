from django.urls import re_path, include, path
from nakhll_market.api import (
    AddCategoryToProduct, AmazingProductViewSet, CategoryViewSet, LastCreatedDiscountedProductsViewSet,
    LastCreatedProductsViewSet, MostDiscountPrecentageProductsViewSet,
    UserProductViewSet, ProductsInSameFactorViewSet, SliderViewSet,
    MostSoldShopsViewSet, RandomShopsViewSet, RandomProductsViewSet,
    MarketList, CreateShop, GetShopWithSlug, CheckShopSlug, CheckProductSlug
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
landing_router.register(r'products', UserProductViewSet, basename="products")


urlpatterns = [
    path('landing/', include(landing_router.urls)),
    path('product-page/same-factor/<uuid:ID>/', ProductsInSameFactorViewSet.as_view()),
    path('markets/', MarketList.as_view()),
    path('shop/', GetShopWithSlug.as_view()),
    path('shop/create/', CreateShop.as_view()),
    path('shop/check/', CheckShopSlug.as_view()),
    path('product/check/', CheckProductSlug.as_view()),
    path('product/category/', AddCategoryToProduct.as_view()),
]
