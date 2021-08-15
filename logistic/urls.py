from rest_framework import routers
from django.urls import path, include
from logistic.api import AddressViewSet



logistic_router = routers.DefaultRouter()
logistic_router.register('address', AddressViewSet, basename='address')


app_name = 'logistic'
urlpatterns = [
    path('api/', include(logistic_router.urls)),
]


