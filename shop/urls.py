from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import ShopFeatureViewSet, ShopFeatureInvoiceViewSet, ShopLandingViewSet, PinnedURLViewSet

shop_router = DefaultRouter()
shop_router.register('shop_feature_invoice', ShopFeatureInvoiceViewSet, basename='shop_feature_invoice')
shop_router.register('shop_feature', ShopFeatureViewSet, basename='shop_feature')
shop_router.register('shop_landing', ShopLandingViewSet, basename='shop_landing')
shop_router.register('pinned_url', PinnedURLViewSet, basename='pinned_url')

app_name = 'shop'
urlpatterns = [
    path('', include(shop_router.urls)),
]

