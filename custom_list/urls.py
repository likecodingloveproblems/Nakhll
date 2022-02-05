from django.urls import path, include
from rest_framework import routers
from custom_list.api import UserFavoriteProductsViewset

favorite_router = routers.DefaultRouter()
favorite_router.register('favorites', UserFavoriteProductsViewset, basename='favorites')

urlpatterns = [
    path('', include(favorite_router.urls))
]