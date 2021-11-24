from django.urls import path
from django.urls.conf import include
from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .api import BeginAuthViewSet, CompeleteAuthViewSet, ProfileViewSet

auth_router = routers.DefaultRouter()
auth_router.register(r'begin', BeginAuthViewSet, basename='begin')
auth_router.register(r'complete', CompeleteAuthViewSet, basename='code_login')

profile_router = routers.DefaultRouter()
profile_router.register(r'', ProfileViewSet, basename='profile'),


app_name = 'auth_api'
urlpatterns = [
    path('auth/', include(auth_router.urls)),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh_api'),
    path('profile/', include(profile_router.urls)),
]