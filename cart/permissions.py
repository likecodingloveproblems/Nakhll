from rest_framework.permissions import BasePermission
from cart.utils import get_user_or_guest


class IsCartOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        prev_result = super().has_object_permission(request, view, obj)
        user, guid = get_user_or_guest(request)
        if user:
            result = obj.user == user
        else:
            result = obj.guest_unique_id == guid
        return prev_result & result

class IsCartItemOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        prev_result = super().has_object_permission(request, view, obj)
        user, guid = get_user_or_guest(request)
        if user:
            result = obj.cart.user == user
        else:
            result = obj.cart.guest_unique_id == guid
        return prev_result & result

