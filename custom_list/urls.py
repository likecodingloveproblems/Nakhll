from django.urls import path, include
from rest_framework import routers
from custom_list.api import UserFavoriteProductsViewset

favorite_router = routers.DefaultRouter()
favorite_router.register('favotites', UserFavoriteProductsViewset, basename='favorites')

app_name = 'custom_list'
urlpatterns = [
    path('lists/', include(favorite_router.urls))
]