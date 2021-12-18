from rest_framework import routers
from django.urls import path, include
from logistic.api import AddressViewSet, ShopLogisticUnitViewSet, ShopLogisticUnitConstraintViewSet



old_logistic_router = routers.DefaultRouter()
old_logistic_router.register('address', AddressViewSet, basename='address')

logistic_router = routers.DefaultRouter()
logistic_router.register('shop-logistic-unit', ShopLogisticUnitViewSet, basename='shop_logistic_unit')
logistic_router.register('shop-logistic-unit-constraint', ShopLogisticUnitConstraintViewSet, basename='shop_logistic_unit_constraint')

app_name = 'logistic'
urlpatterns = [
    path('api/v1/logistic/', include(logistic_router.urls)),
    path('logistic/api/', include(old_logistic_router.urls)), #TODO: fix later
]


