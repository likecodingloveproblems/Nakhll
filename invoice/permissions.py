from rest_framework.permissions import BasePermission
from invoice.models import Invoice


class IsInvoiceOwner(BasePermission):
    """Check if the user is the owner of the invoice"""

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Invoice):
            return obj.user == request.user
        return True
