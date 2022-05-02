from rest_framework import routers
from django.urls import path, include
from logistic.api import (
    AddressViewSet, ShopLogisticUnitCalculationMetricViewSet,
    ShopLogisticUnitViewSet, ShopLogisticUnitConstraintViewSet
)


logistic_router = routers.DefaultRouter()
logistic_router.register('addresses', AddressViewSet, basename='addresses')
logistic_router.register('shop-logistic-unit', ShopLogisticUnitViewSet,
                         basename='shop_logistic_unit')
logistic_router.register('shop-logistic-unit-constraint',
                         ShopLogisticUnitConstraintViewSet,
                         basename='shop_logistic_unit_constraint')
logistic_router.register('shop-logistic-unit-metric',
                         ShopLogisticUnitCalculationMetricViewSet,
                         basename='shop_logistic_unit_constraint_parameter')

urlpatterns = [
    path('', include(logistic_router.urls)),
]
