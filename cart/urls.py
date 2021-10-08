from django.db.models import base
from rest_framework import routers
from Payment.views import show_cart
from django.urls import path, include
from cart.api import UserCartViewSet, UserCartItemViewSet
from cart.views import add_to_cart, show_cart



cart_router = routers.DefaultRouter()
cart_router.register('carts', UserCartViewSet, basename='api_carts')
cart_router.register('cart_items', UserCartItemViewSet, basename='api_cart_items')


app_name = 'cart_new'
urlpatterns = [
    path('add-to-cart/<product_ID>/', add_to_cart, name='add_to_cart'),
    path('detail/', show_cart, name='show_cart'),
    path('api/', include(cart_router.urls)),
]


