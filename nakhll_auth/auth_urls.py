from django.urls import path
from django.urls.conf import include
from rest_framework import routers
from rest_framework_simplejwt.views import TokenRefreshView
from .api import BeginAuthViewSet, CompeleteAuthViewSet, GetAccessTokenView

auth_router = routers.DefaultRouter()
auth_router.register(r'begin', BeginAuthViewSet, basename='begin')
auth_router.register(r'complete', CompeleteAuthViewSet, basename='code_login')


urlpatterns = [
    path('', include(auth_router.urls)),
    path('token/', GetAccessTokenView.as_view(), name='get_token_api'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh_api'),
]