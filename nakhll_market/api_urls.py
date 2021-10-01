from django.urls import re_path, include, path
from nakhll_market.api import (
    AddSubMarketToProduct, AllShopSettings, AmazingProductViewSet, CategoryViewSet, ImageShopSettings, LastCreatedDiscountedProductsViewSet,
    LastCreatedProductsViewSet, MostDiscountPrecentageProductsViewSet, ShopMultipleUpdateInventory, ShopMultipleUpdatePrice, SocialMediaShopSettings, StateFullViewSet,
    UserProductViewSet, ProductsInSameFactorViewSet, SliderViewSet, SubMarketList, UserProfileViewSet,
    MostSoldShopsViewSet, RandomShopsViewSet, RandomProductsViewSet, ProductsViewSet, GetShop,
    MarketList, CreateShop, GetShopWithSlug, CheckShopSlug, CheckProductSlug, ShopProductsViewSet,
    ProductBannerViewSet, AddImagesToProduct, ProductDetailsViewSet, BankAccountShopSettings, ProductCommentsViewSet, ProductRelatedItemsViewSet,
    LandingPageSchemaViewSet,
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
landing_router.register(r'shop_products', ShopProductsViewSet, basename="shop_products")
landing_router.register(r'product_banner', ProductBannerViewSet, basename="product_banners")
landing_router.register(r'schema', LandingPageSchemaViewSet, basename="landing_page_schema")

product_page_router = routers.DefaultRouter()
product_page_router.register(r'', ProductsViewSet, basename="all_products")
product_page_router.register(r'details', ProductDetailsViewSet, basename="details")
product_page_router.register(r'comments', ProductCommentsViewSet, basename="comments")
product_page_router.register(r'related_products', ProductRelatedItemsViewSet, basename="related_products")

util_router = routers.DefaultRouter()
util_router.register(r'states', StateFullViewSet, basename="states")

profile_router = routers.DefaultRouter()
profile_router.register(r'', UserProfileViewSet, basename="profile")

urlpatterns = [
    path('landing/', include(landing_router.urls)),
    path('products/', include(product_page_router.urls)),
    path('product-page/', include(product_page_router.urls)),
    path('product-page/same-factor/<uuid:ID>/', ProductsInSameFactorViewSet.as_view()),

    path('markets/', MarketList.as_view()),
    path('sub_markets/', SubMarketList.as_view()),
    path('util/', include(util_router.urls)),

    path('shop/', GetShopWithSlug.as_view()),
    path('shop/<shop_slug>/settings/', AllShopSettings.as_view()),
    path('shop/<shop_slug>/settings/bank_account/', BankAccountShopSettings.as_view()),
    path('shop/<shop_slug>/settings/social_media/', SocialMediaShopSettings.as_view()),
    path('shop/<shop_slug>/settings/avatar/', ImageShopSettings.as_view()),
    path('shop/create/', CreateShop.as_view()),
    path('shop/<Slug>/', GetShop.as_view({'get': 'retrieve'})),
    path('shop/check/', CheckShopSlug.as_view()),
    path('shop/multiple-update/price/', ShopMultipleUpdatePrice.as_view()),
    path('shop/multiple-update/inventory/', ShopMultipleUpdateInventory.as_view()),

    path('product/check/', CheckProductSlug.as_view()),
    path('product/categories/', AddSubMarketToProduct.as_view()),
    path('product/images/', AddImagesToProduct.as_view()),

    path('profile/', include(profile_router.urls)),

    # path('torob/products/', TorobAllProducts.as_view()),
]
