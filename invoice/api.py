from rest_framework.exceptions import ValidationError
from django.utils.translation import ugettext as _
from rest_framework import status, mixins, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from cart.managers import CartManager
from logistic.interfaces import LogisticUnitInterface
from .models import Invoice
from .exceptions import EmptyCartException
from .permissions import IsInvoiceOwner
from .serializers import InvoiceWriteSerializer, InvoiceRetrieveSerializer


class InvoiceViewSet(viewsets.GenericViewSet,
                    mixins.RetrieveModelMixin,
                    mixins.CreateModelMixin, mixins.ListModelMixin):
    permission_classes = [IsInvoiceOwner, permissions.IsAuthenticated, ]
    queryset = Invoice.objects.all()

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(user=self.request.user)
        return queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return InvoiceRetrieveSerializer
        elif self.action == 'retrieve':
            return InvoiceRetrieveSerializer
        else:
            return InvoiceWriteSerializer

    def create(self, request, *args, **kwargs):
        ''' each user can have many invoices '''
        invoice = self._create_invoice(request)
        serializer = InvoiceRetrieveSerializer(invoice)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK, headers=headers)

    def _create_invoice(self, request):
        active_cart = CartManager.user_active_cart(request.user)
        if not active_cart.items.all():
            raise EmptyCartException
        invoice = active_cart.convert_to_invoice()
        return invoice
   
    @action(methods=['POST'], detail=True)
    def pay(self, request, pk):
        ''' Get an invoice and send it to payment app
        
            Request for invoice should came from owner.
            Invoice should sent to payment to initiate payment
        '''
        invoice = self.get_object()
        return invoice.send_to_payment()

        

    @action(methods=['POST'], detail=True)
    def fill_cart(self, request, pk):
        invoice = self.get_object()
        invoice.fill_cart()
        return Response({'status': 'success'})
