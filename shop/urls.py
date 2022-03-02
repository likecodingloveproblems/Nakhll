from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import ShopAdvertisementViewSet, ShopFeatureViewSet, ShopFeatureInvoiceViewSet, ShopLandingViewSet, PinnedURLViewSet, ShopViewSet

shop_router = DefaultRouter()
shop_router.register('', ShopViewSet, basename='shop')
shop_router.register('feature', ShopFeatureViewSet, basename='shop_feature')
shop_router.register('feature_invoice', ShopFeatureInvoiceViewSet, basename='shop_feature_invoice')
shop_router.register('advertisement', ShopAdvertisementViewSet, basename='shop_advertisement')
shop_router.register('landing/(?P<shop__Slug>[^/.]+)', ShopLandingViewSet, basename='shop_landing')
shop_router.register('pinned_url', PinnedURLViewSet, basename='pinned_url')

urlpatterns = [
    path('', include(shop_router.urls)),
]

