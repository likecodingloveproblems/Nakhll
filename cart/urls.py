from rest_framework import routers
from django.urls import path, include
from cart.api import UserCartViewSet, UserCartItemViewSet


cart_router = routers.DefaultRouter()
cart_router.register('', UserCartViewSet, basename='api_carts')
cart_router.register('items', UserCartItemViewSet, basename='api_cart_items')


urlpatterns = [
    path('', include(cart_router.urls)),
]
