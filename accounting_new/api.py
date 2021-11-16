from rest_framework.exceptions import ValidationError
from datetime import datetime, timedelta
from logistic.models import PostPriceSetting
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from rest_framework import status, mixins, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from nakhll_market.serializers import ProductLastStateSerializer
from cart.managers import CartManager
from logistic.interfaces import PostPriceSettingInterface
from payoff.exceptions import NoAddressException, InvoiceExpiredException,\
            InvalidInvoiceStatusException, OutOfPostRangeProductsException
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

    # def get_object(self):
    #     active_cart = CartManager.user_active_cart(self.request.user)
    #     invoice = Invoice.objects.filter(cart=active_cart).first() or self.create_invoice(self.request)
    #     invoice.status = Invoice.Statuses.AWAIT_PAYMENT
    #     invoice.save()
    #     return invoice

    def create(self, request, *args, **kwargs):
        ''' each user can have many invoices '''
        try:
            invoice = self.__create_invoice(request)
            #TODO: Create alert
        except ValidationError as ex:
            return Response({'detail': f'خطا در ساخت فاکتور: {ex}'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = InvoiceRetrieveSerializer(invoice)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK, headers=headers)



    # @action(methods=['GET'], detail=False)
    # def active_invoice(self, request):
    #     invoice = self.get_object()
    #     serializer = InvoiceReadSerializer(invoice)
    #     return Response(serializer.data, status=status.HTTP_200_OK)

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
        logistic, is_created = PostPriceSetting.objects.get_or_create()
        out_of_range_products = logistic.get_out_of_range_products(invoice)
        post_price = logistic.get_post_price(invoice)
        invoice.logistic_price = post_price
        invoice.save()
        return Response({'post_price': post_price, 'out_of_range': out_of_range_products}, status=status.HTTP_200_OK)


    @action(methods=['GET'], detail=True)
    def pay(self, request, pk):
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
        invoice = self.get_object()
        # is_differ = invoice.cart.get_diffrences
        # if is_differ:
            # return Response({'error': 'تغییراتی در سبد خرید شما به وجود آمده است. لطفا سبد خرید را بررسی کنید'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            return invoice.send_to_payment()
        except NoAddressException:
            return Response({'error': 'آدرس خریدار را تکمیل کنید'}, status=status.HTTP_400_BAD_REQUEST)
        except InvoiceExpiredException:
            return Response({'error': 'فاکتور منقضی شده است'}, status=status.HTTP_400_BAD_REQUEST)
        except InvalidInvoiceStatusException:
            return Response({'error': 'فاکتور در حال حاضر قابل پرداخت نیست'}, status=status.HTTP_400_BAD_REQUEST)
        except OutOfPostRangeProductsException as ex:
            return Response({'error': f'این محصولات خارج از محدوده ارسال شما هستند: {ex}'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            return Response({'error': str(ex)}, status=status.HTTP_400_BAD_REQUEST)
        

    @action(methods=['POST'], detail=True)
    def to_cart(self, request, pk):
        #TODO: Need clean up and also all adding products to cart should be done here, so 
        #TODO: it can be validated just in one place
        active_cart = CartManager.user_active_cart(request.user)
        invoice = self.get_object()
        for item in invoice.items.all():
            active_cart.add_product(item.product)
        return Response({'status': 'success'})



    # @action(methods=['GET'], detail=False)
    # def confirm_changes(self, request):
    #     ''' User confirms for changes made to product and update product_last_state '''
    #     invoice = self.get_object()
    #     cart = invoice.cart
    #     for item in cart.items.all():
    #         item.product_last_state = ProductLastStateSerializer(item.product).data
    #         item.save()
    #     return Response({'result': 'success'}, status=status.HTTP_200_OK)



