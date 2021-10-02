from rest_framework.exceptions import ValidationError
from cart.serializers import ProductLastStateSerializer
from datetime import datetime, timedelta
from logistic.models import PostPriceSetting
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from rest_framework import status, mixins, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from nakhll.authentications import CsrfExemptSessionAuthentication
from cart.managers import CartManager
from logistic.interfaces import PostPriceSettingInterface
from .models import Invoice
from .serializers import InvoiceWriteSerializer, InvoiceReadSerializer
from .permissions import IsInvoiceOwner


class InvoiceViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin, 
                    mixins.UpdateModelMixin, mixins.RetrieveModelMixin,
                    mixins.DestroyModelMixin):
    permission_classes = [IsInvoiceOwner, permissions.IsAuthenticated, ]
    authentication_classes = [CsrfExemptSessionAuthentication, ]
    queryset = Invoice.objects.all()


    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return InvoiceReadSerializer
        else:
            return InvoiceWriteSerializer

    def create_invoice(self, request):
        active_cart = CartManager.user_active_cart(request.user)
        data = {'cart': active_cart.id }
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        return self.perform_create(serializer)



    def get_object(self):
        # TODO: System must support multi invoice per user (more on clickup#1fu8awk)
        active_cart = CartManager.user_active_cart(self.request.user)
        invoice = Invoice.objects.filter(cart=active_cart).first() or self.create_invoice(self.request)
        # if invoice.status == Invoice.Statuses.PAYING:
            # raise ValidationError('فاکتور شما در حال پرداخت می‌باشد و امکان دسترسی به آن وجود ندارد')
        invoice.status = Invoice.Statuses.AWAIT_PAYING
        invoice.save()
        return invoice

    def create(self, request, *args, **kwargs):
        ''' each user can only have one invoice with status of completing '''
        invoice = self.get_object()
        serializer = InvoiceReadSerializer(invoice)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK, headers=headers)

    def perform_create(self, serializer):
        invoice = serializer.save()
        #TODO: Create alert
        return invoice


    @action(methods=['GET'], detail=False)
    def active_invoice(self, request):
        invoice = self.get_object()
        serializer = InvoiceReadSerializer(invoice)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['PATCH'], detail=False)
    def set_coupon(self, request):
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

    @action(methods=['PATCH'], detail=False)
    def unset_coupon(self, request):
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
        coupon_usage.delete()
        serializer.save()
        return Response({'result': 0}, status=status.HTTP_200_OK)
    
    @action(methods=['PATCH'], detail=False)
    def set_address(self, request):
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
        serializer.save(cart=invoice.cart)
        logistic, is_created = PostPriceSetting.objects.get_or_create()
        out_of_range_shops = logistic.get_out_of_range_products(invoice)
        post_price = logistic.get_post_price(invoice)
        return Response({'post_price': post_price, 'out_of_range': out_of_range_shops}, status=status.HTTP_200_OK)


    @action(methods=['GET'], detail=False)
    def pay(self, request):
        ''' Get an invoice and send it to payment app
        
            Request for invoice should came from owner.
            Invoice status should change to paying, which other apps should 
            check for this status and prevnet changing in their apps until 
            this status change to something else; apps like:
            1- Cart: prevent from adding to it
            2- Coupon: prevent same coupon from calculating (also accouting
                should check if the coupon itself is not in another invoice 
                with paing status
            A celery should check for invocies with paying status every hour.
            Invoice should sent to payment status to initiate payment
        '''
        # TODO: editing items in active cart when cart sent to accounting should be denied
        # TODO: gettings diffrences is not implemented completely
        invoice = self.get_object()
        is_differ = invoice.cart.get_diffrences
        if is_differ:
            
            return Response({'error': 'تغییراتی در سبد خرید شما به وجود آمده است. لطفا سبد خرید را بررسی کنید'}, status=status.HTTP_400_BAD_REQUEST)
        invoice.send_to_payment()

    @action(methods=['GET'], detail=False)
    def confirm_changes(self, request):
        ''' User confirms for changes made to product and update product_last_state '''
        invoice = self.get_object()
        cart = invoice.cart
        for item in cart.items.all():
            item.product_last_state = ProductLastStateSerializer(item.product).data
            item.save()
        return Response({'result': 'success'}, status=status.HTTP_200_OK)



