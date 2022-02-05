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

    def __create_invoice(self, request):
        active_cart = CartManager.user_active_cart(request.user)
        if not active_cart.items.all():
            raise ValidationError('سبد خرید خالی است')
        invoice = active_cart.convert_to_invoice()
        return invoice

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


    @action(methods=['PATCH'], detail=True)
    def set_coupon(self, request, pk):
        ''' Verify and calculate user coupon and return discount amount
        
            Get invoice with pk as id, insure that invoice belogs to user
            that requested for it, and also insure the invoice status is
            'completing' and user address is filled.
            Send this invoice with coupon to coupon app and get amount of 
            discount that should applied, or errors if there is any. Coupon
            should be applied and saved in factor for future reference
        '''
        invoice = self.get_object()
        serializer = InvoiceWriteSerializer(instance=invoice, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        coupon = serializer.validated_data.get('coupon')
        if coupon.is_valid(invoice):
            serializer.save()
            coupon.apply(invoice)
        return Response({'coupon': coupon.code, 'result': coupon.final_price, 'errors': coupon.errors}, status=status.HTTP_200_OK)

    @action(methods=['PATCH'], detail=True)
    def unset_coupon(self, request, pk):
        ''' Unset coupon from invoice
        
            Get invoice with pk as id, insure that invoice belogs to user
            that requested for it, and also insure the invoice status is
            'completing' and user address is filled.
            Send this invoice with coupon to coupon app and get amount of 
            discount that should applied, or errors if there is any. Coupon
            should be applied and saved in factor for future reference
        '''
        invoice = self.get_object()
        serializer = InvoiceWriteSerializer(instance=invoice, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        coupon = serializer.validated_data.get('coupon')
        coupon_usage = invoice.coupon_usages.filter(coupon=coupon).first()
        if not coupon_usage:
            return Response({'result': 'چنین کوپنی برای این فاکتور ثبت نشده است'}, status=status.HTTP_400_BAD_REQUEST)
        coupon_usage.delete()
        serializer.save()
        return Response({'result': 0}, status=status.HTTP_200_OK)
    
    @action(methods=['PATCH'], detail=True)
    def set_address(self, request, pk):
        ''' Calculate logistic price from shops to user address 
        
            Get invoice and insure that it is for requested user. Also it 
            should check if invoice status is 'completing' or not.
            Send factor to logistic app, so logistic will calulate total
            amount for post_price. post_price should be saved in factor as
            a field. post_price can be 'None' which means user must pay it
            at the destination. invoice_id is received as pk which contain 
            everything needed in logistic app
        '''
        invoice = self.get_object()
        serializer = InvoiceWriteSerializer(instance=invoice, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        lui = LogisticUnitInterface()
        invoice.logistic_unit_details = lui.create_logistic_unit_list(invoice)
        invoice.logistic_price = lui.total_post_price
        invoice.save()
        return Response(invoice.logistic_unit_details, status=status.HTTP_200_OK)


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
        active_cart = CartManager.user_active_cart(request.user)
        invoice = self.get_object()
        for item in invoice.items.all():
            active_cart.add_product(item.product)
        return Response({'status': 'success'})
