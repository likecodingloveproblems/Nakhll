from rest_framework import routers
from django.urls import path, include
from logistic.api import AddressViewSet, ShopLogisticUnitViewSet, ShopLogisticUnitConstraintViewSet



logistic_router = routers.DefaultRouter()
logistic_router.register('address', AddressViewSet, basename='address')
logistic_router.register('logistic-unit', ShopLogisticUnitViewSet, basename='logistic_unit')
logistic_router.register('logistic-unit-constrain', ShopLogisticUnitConstraintViewSet, basename='logistic_unit_constrain')

app_name = 'logistic'
urlpatterns = [
    path('api/', include(logistic_router.urls)),
]


