from rest_framework import serializers
from accounting_new.models import Invoice
from cart.serializers import CartItemReadSerializer


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = ('cart', 'address', )


