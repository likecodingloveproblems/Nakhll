from rest_framework import routers
from django.urls import path, include
from logistic.api import AddressViewSet, ShopLogisticUnitViewSet



logistic_router = routers.DefaultRouter()
logistic_router.register('address', AddressViewSet, basename='address')
logistic_router.register('logistic-unit', ShopLogisticUnitViewSet, basename='logistic_unit')


app_name = 'logistic'
urlpatterns = [
    path('api/', include(logistic_router.urls)),
]


