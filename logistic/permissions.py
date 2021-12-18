from rest_framework.permissions import BasePermission
from logistic.models import ShopLogisticUnit, ShopLogisticUnitConstraint


class IsAddressOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        prev_result = super().has_object_permission(request, view, obj)
        result = obj.user == request.user
        return prev_result & result


class IsShopOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        # return super().has_object_permission(request, view, obj)
        shop = None
        if isinstance(obj, ShopLogisticUnit):
            shop = obj.shop
        elif isinstance(obj, ShopLogisticUnitConstraint):
            shop = obj.shop_logistic_unit.shop

        return shop.FK_ShopManager == request.user
