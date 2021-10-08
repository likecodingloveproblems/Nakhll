from rest_framework.permissions import BasePermission


class IsAddressOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        prev_result = super().has_object_permission(request, view, obj)
        result = obj.user == request.user
        return prev_result & result

