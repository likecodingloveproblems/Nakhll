from rest_framework import routers
from django.urls import path, include
from cart.api import UserCartViewSet, UserCartItemViewSet



cart_router = routers.DefaultRouter()
cart_router.register('carts', UserCartViewSet, basename='api_carts')
cart_router.register('cart_items', UserCartItemViewSet, basename='api_cart_items')


app_name = 'cart_new'
urlpatterns = [
    path('api/', include(cart_router.urls)),
]


