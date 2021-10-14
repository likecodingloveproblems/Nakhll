from Payment.models import FactorPost
from rest_framework import permissions

class IsShopOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        prev_result = super().has_object_permission(request, view, obj)
        result = obj.FK_ShopManager == request.user
        return prev_result & result


class IsFactorOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        prev_result = super().has_object_permission(request, view, obj)
        user = request.user
        result = FactorPost.objects.filter(Factor_Products=obj, FK_Product__FK_Shop__FK_ShopManager=user).exists()
        return prev_result & result

class IsProductOwner(permissions.BasePermission):
    # TODO: Check permission class
    def has_object_permission(self, request, view, obj):
        prev_result = super().has_object_permission(request, view, obj)
        result = obj.FK_Shop.FK_ShopManager == request.user
        return prev_result & result

class IsProductBannerOwner(permissions.BasePermission):
    # TODO: Check permission class
    def has_object_permission(self, request, view, obj):
        prev_result = super().has_object_permission(request, view, obj)
        result = obj.FK_Product.FK_Shop.FK_ShopManager == request.user
        return prev_result & result

