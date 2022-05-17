from rest_framework.permissions import BasePermission
from invoice.models import Invoice

class IsInvoiceOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Invoice):
            return obj.user == request.user
        return True