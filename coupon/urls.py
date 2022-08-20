from django.urls import path, include
from rest_framework import routers
from .api import CouponViewset

app_name = 'coupon'

coupon_router = routers.DefaultRouter()
coupon_router.register('gift_coupon', CouponViewset, basename='gift_coupon')

urlpatterns = [
    path('', include(coupon_router.urls)),
]
