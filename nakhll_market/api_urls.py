from django.urls import re_path, include, path
from nakhll_market.api import (
    AmazingProductViewSet, CategoryViewSet, SliderViewSet
    )
from rest_framework import routers

app_name = 'nakhll_market'

router = routers.DefaultRouter()
router.register(r'sliders', SliderViewSet, basename="sliders")
router.register(r'categories', CategoryViewSet, basename="categories")
router.register(r'amazing-products', AmazingProductViewSet, basename="amazing products")

urlpatterns = [
    path('landing/', include(router.urls)),
]
