from django.urls import path
from django.urls.conf import include
from rest_framework import routers
from .api import ProfileViewSet

profile_router = routers.DefaultRouter()
profile_router.register(r'', ProfileViewSet, basename='profile'),


urlpatterns = [
    path('', include(profile_router.urls)),
]