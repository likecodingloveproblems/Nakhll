from rest_framework.permissions import BasePermission

class IsShopOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        prev_result = super().has_object_permission(request, view, obj)
        user = request.user 
        return prev_result and obj.shop.FK_ShopManager == user

class IsPinnedURLOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        prev_result = super().has_object_permission(request, view, obj)
        user = request.user 
        return prev_result and obj.user == user

