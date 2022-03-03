from django.utils.translation import gettext as _
from django.db.models.manager import BaseManager
from rest_framework.permissions import BasePermission

from nakhll_market.models import Shop
from invoice.models import Invoice
from shop.models import ShopAdvertisement, ShopFeature, ShopFeatureInvoice


class IsShopOwner(BasePermission):
    message = _('شما مالک این فروشگاه نیستید و دسترسی لازم را ندارید.')

    def has_object_permission(self, request, view, obj):
        user = request.user
        if isinstance(obj, Shop):
            return obj.FK_ShopManager == user
        if isinstance(
                obj, ShopFeatureInvoice) or isinstance(
                obj, ShopAdvertisement):
            return obj.shop.FK_ShopManager == user
        return True


class IsPinnedURLOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        return obj.user == user


class ShopLandingPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        shop = obj if isinstance(obj, Shop) else obj.shop
        return ShopFeature.has_shop_landing_access(shop)


class IsInvoiceProvider(BasePermission):
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Invoice):
            invoice_shops = obj.shop.all()
            user_shops = Shop.objects.filter(FK_ShopManager=request.user)
            return any(shop in user_shops for shop in invoice_shops)
        return True
