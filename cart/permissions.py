from cart.models import Cart
from rest_framework.permissions import BasePermission
from cart.utils import get_user_or_guest


class IsCartOwner(BasePermission):
    """Check if user is the owner of the cart"""

    def has_object_permission(self, request, view, obj):
        prev_result = super().has_object_permission(request, view, obj)
        user, guid = get_user_or_guest(request)
        if user:
            result = obj.user == user
        else:
            result = obj.guest_unique_id == guid
        return prev_result & result


class IsCartItemOwner(BasePermission):
    """Check if user is the owner of the cart item"""

    def has_object_permission(self, request, view, obj):
        prev_result = super().has_object_permission(request, view, obj)
        user, guid = get_user_or_guest(request)
        cart = obj if type(obj) == Cart else obj.cart
        if user:
            result = cart.user == user
        else:
            result = cart.guest_unique_id == guid
        return prev_result & result
