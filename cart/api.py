from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from cart.managers import CartManager
from django.utils.translation import ugettext as _
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from nakhll_market.models import ProductManager
from cart.models import Cart, CartItem
from cart.serializers import (CartSerializer, CartItemSerializer,
                              CartWriteSerializer)
from cart.utils import get_user_or_guest
from cart.permissions import IsCartOwner, IsCartItemOwner
from payoff.exceptions import (NoAddressException, InvoiceExpiredException,
                            InvalidInvoiceStatusException, NoItemValidation,
                            OutOfPostRangeProductsException)
from logistic.interfaces import LogisticUnitInterface


class UserCartViewSet(viewsets.GenericViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsCartOwner,]

    def get_object(self):
        user, guid = get_user_or_guest(self.request)
        if user or guid:
            return CartManager.user_active_cart(user, guid)
        return None
        
    @action(detail=False, methods=['GET'], name='View current user active cart')
    def my(self, request):
        cart = self.get_object()
        serializer = self.get_serializer(cart)
        response = Response(serializer.data)
        self.delete_guid_cookie(response)
        return response

    def delete_guid_cookie(self, response):
        if self.request.user and self.request.user.is_authenticated:
            response.delete_cookie('guest_unique_id')
        return response

        
    @action(methods=['PATCH'], detail=False)
    def set_address(self, request):
        # TODO: do I raise error if address is not valid?
        # TODO: do I clear the cart if no address is available?
        cart = self.get_object()
        serializer = CartWriteSerializer(instance=cart, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        cart.logistic_details = self.get_logistic_details()
        cart.save()
        return Response(cart.logistic_details.as_dict(), status=status.HTTP_200_OK)


    def get_logistic_details(self):
        if not self.address:
            raise ValidationError(_('آدرس سفارش را وارد کنید'))
        lui = LogisticUnitInterface()
        return lui.create_logistic_unit_list(self)
        
        
    @action(methods=['PATCH'], detail=False)
    def set_coupon(self, request):
        ''' Verify and calculate user coupon and return discount amount
        
            ensure that user address is filled.
            Send this invoice with coupon to coupon app and get amount of 
            discount that should applied, or errors if there is any. Coupon
            should be applied and saved in invoice for future reference
        '''
        cart = self.get_object()
        serializer = CartWriteSerializer(instance=cart, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        coupon = serializer.validated_data.get('coupon')
        if coupon.is_valid(cart):
            serializer.save()
        return Response({'coupon': coupon.code, 'result': coupon.final_price, 'errors': coupon.errors}, status=status.HTTP_200_OK)

    @action(methods=['PATCH'], detail=False)
    def unset_coupon(self, request):
        ''' Unset coupon from cart'''
        cart = self.get_object()
        serializer = CartWriteSerializer(instance=cart, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        coupon = serializer.validated_data.get('coupon')
        if coupon not in cart.coupons.all():
            return Response({'result': 'چنین کوپنی برای این سبد خرید ثبت نشده است'}, status=status.HTTP_400_BAD_REQUEST)
        cart.coupons.delete(coupon)
        serializer.save()
        return Response({'result': 0}, status=status.HTTP_200_OK)

        
    @action(methods=['POST'], detail=False)
    def pay(self, request):
        ''' Convert cart to invoice and send to payment app '''
        cart = self.get_object()
        invoice = cart.convert_to_invoice()
        try:
            return invoice.send_to_payment()
        except NoItemValidation:
            return Response({'error': 'سبد خرید شما خالی است. لطفا سبد خرید خود را تکمیل کنید'}, status=status.HTTP_400_BAD_REQUEST)
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


class UserCartItemViewSet(viewsets.GenericViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [IsCartItemOwner, ]

    def get_object(self):
        try:
            cart_item = CartItem.objects.get(pk=self.kwargs['pk'])
            self.check_object_permissions(self.request, cart_item)
            return cart_item
        except CartItem.DoesNotExist:
            raise ValidationError({'error': ['محصول با این شناسه در سبد خرید شما وجود ندارد']})

    @action(detail=True, methods=['GET'], name='Add item to active cart', url_path='add')
    def add_item(self, request, pk):
        product = ProductManager.get_product(pk)
        active_cart = Cart.get_active_cart(request)
        active_cart.add_product(product)
        cart_serializer = CartSerializer(active_cart)
        response = Response(cart_serializer.data, status=status.HTTP_200_OK)
        return self.append_cookie(response, active_cart)

    @action(detail=True, methods=['GET'], name='Remove item from active cart', url_path='remove')
    def reduce_item(self, request, pk):
        cart_item = self.get_object()
        cart_item.reduce_count()
        cart_serializer = CartSerializer(cart_item.cart)
        return Response(cart_serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], name='Delete whole cart item', url_path='delete')
    def delete_item(self, request, pk):
        cart_item = self.get_object()
        cart_item.delete()
        cart_serializer = CartSerializer(cart_item.cart)
        return Response(cart_serializer.data, status=status.HTTP_200_OK)

    def append_cookie(self, response, cart):
        if not self.request.COOKIES.get('guest_unique_id'):
            response.set_cookie('guest_unique_id', cart.guest_unique_id, max_age=60*60*24*365)
        return response

