from django.db.models.manager import BaseManager
from rest_framework.permissions import BasePermission

from nakhll_market.models import Shop
from shop.models import ShopAdvertisement, ShopFeature, ShopFeatureInvoice

class IsShopOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        prev_result = super().has_object_permission(request, view, obj)
        user = request.user 
        if isinstance(obj, Shop):
            return prev_result and obj.FK_ShopManager == user
        if isinstance(obj, ShopFeatureInvoice) or isinstance(obj, ShopAdvertisement):
            return prev_result and obj.shop.FK_ShopManager == user
        return prev_result

class IsPinnedURLOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        prev_result = super().has_object_permission(request, view, obj)
        user = request.user 
        return prev_result and obj.user == user



class ShopLandingPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        prev_result = super().has_object_permission(request, view, obj)
        shop = obj if isinstance(obj, Shop) else obj.shop
        return prev_result and ShopFeature.has_shop_landing_access(shop)
