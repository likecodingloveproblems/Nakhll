from rest_framework.exceptions import ValidationError
from django.utils.translation import ugettext as _
from rest_framework import status, mixins, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from cart.managers import CartManager
from .models import Invoice
from .serializers import InvoiceWriteSerializer, InvoiceRetrieveSerializer
from .permissions import IsInvoiceOwner


class InvoiceViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin, 
                    mixins.UpdateModelMixin, mixins.RetrieveModelMixin,
                    mixins.DestroyModelMixin, mixins.ListModelMixin):
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

    def __create_invoice(self, request):
        active_cart = CartManager.user_active_cart(request.user)
        if not active_cart.items.all():
            raise ValidationError('سبد خرید خالی است')
        invoice = active_cart.convert_to_invoice()
        return invoice

    def create(self, request, *args, **kwargs):
        ''' each user can have many invoices '''
        try:
            invoice = self.__create_invoice(request)
        except ValidationError as ex:
            return Response({'detail': f'خطا در ساخت فاکتور: {ex}'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = InvoiceRetrieveSerializer(invoice)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK, headers=headers)


    @action(methods=['POST'], detail=True)
    def to_cart(self, request, pk):
        #TODO: Need clean up and also all adding products to cart should be done here, so 
        #TODO: it can be validated just in one place
        active_cart = CartManager.user_active_cart(request.user)
        invoice = self.get_object()
        for item in invoice.items.all():
            active_cart.add_product(item.product)
        return Response({'status': 'success'})
