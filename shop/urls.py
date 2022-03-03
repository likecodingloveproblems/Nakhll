from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import (ShopAdvertisementViewSet, ShopFeatureViewSet,
                  ShopFeatureInvoiceViewSet, ShopInvoicesViewSet,
                  ShopLandingViewSet, PinnedURLViewSet, ShopViewSet,
                  )

shop_router = DefaultRouter()
shop_router.register('', ShopViewSet, basename='shops')
shop_router.register('features', ShopFeatureViewSet, basename='shop_features')
shop_router.register(
    'feature-invoices',
    ShopFeatureInvoiceViewSet,
    basename='shop_feature_invoices')
shop_router.register(
    'advertisements',
    ShopAdvertisementViewSet,
    basename='shop_advertisements')
shop_router.register(
    'landings/(?P<shop__Slug>[^/.]+)',
    ShopLandingViewSet,
    basename='shop_landings')
shop_router.register('pinned-urls', PinnedURLViewSet, basename='pinned_urls')
shop_router.register(
    '(?P<shop__Slug>[^/.]+)/invoices',
    ShopInvoicesViewSet,
    basename='shop_invoices')

urlpatterns = [
    path('', include(shop_router.urls)),
]
