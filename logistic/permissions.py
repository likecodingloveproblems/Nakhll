from rest_framework.permissions import BasePermission
from logistic.models import LogisticUnitConstraintParameter, ShopLogisticUnit, ShopLogisticUnitConstraint


class IsAddressOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        prev_result = super().has_object_permission(request, view, obj)
        result = obj.user == request.user
        return prev_result & result


class IsShopOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        # return super().has_object_permission(request, view, obj)
        if isinstance(obj, ShopLogisticUnit):
            shop = obj.shop
        elif isinstance(obj, ShopLogisticUnitConstraint):
            shop = obj.shop_logistic_unit.shop
        elif isinstance(obj, LogisticUnitConstraintParameter):
            shop = obj.shop_logistic_unit_constraint.shop_logistic_unit.shop
        else:
            return False

        return shop.FK_ShopManager == request.user
