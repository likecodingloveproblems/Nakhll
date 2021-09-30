from accounting_new.models import Invoice
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from cart.managers import CartManager
from django.utils.translation import ugettext as _
from rest_framework import permissions, viewsets, mixins
from nakhll.authentications import CsrfExemptSessionAuthentication
from nakhll_market.models import ProductManager
from cart.models import Cart, CartItem
from cart.serializers import CartSerializer, CartItemSerializer, ProductLastStateSerializer
from cart.utils import get_user_or_guest
from cart.permissions import IsCartOwner, IsCartItemOwner


class UserCartViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin):
    serializer_class = CartSerializer
    authentication_classes = [CsrfExemptSessionAuthentication, ]
    permission_classes = [IsCartOwner, ]

    def get_queryset(self):
        user, guid = get_user_or_guest(self.request)
        return CartManager.user_active_cart(user, guid)

    def get_object(self):
        user, guid = get_user_or_guest(self.request)
        return CartManager.user_active_cart(user, guid)

        
    @action(detail=False, methods=['GET'], name='View current user active cart')
    def my(self, request):
        cart = self.get_object()
        serializer = self.get_serializer(cart)
        return Response(serializer.data)
        



class UserCartItemViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        user, guid = get_user_or_guest(self.request)
        return CartItem.objects.user_cartitems(user, guid)

    def destroy(self, request, *args, **kwargs):
        self.__prevent_if_paying()
        instance = self.get_object()
        self.perform_destroy(instance)
        user, guid = get_user_or_guest(self.request)
        cart_serializer = CartSerializer(CartManager.user_active_cart(user, guid))
        headers = self.get_success_headers(cart_serializer.data)
        self.__clear_invoice()
        return Response(cart_serializer.data, status=status.HTTP_200_OK, headers=headers)

    @action(detail=True, methods=['GET'], name='Delete whole cart item')
    def delete(self, request, pk):
        self.__prevent_if_paying()
        instance = self.get_object()
        self.perform_destroy(instance)
        user, guid = get_user_or_guest(self.request)
        cart_serializer = CartSerializer(CartManager.user_active_cart(user, guid))
        headers = self.get_success_headers(cart_serializer.data)
        self.__clear_invoice()
        return Response(cart_serializer.data, status=status.HTTP_200_OK, headers=headers)

    @action(detail=True, methods=['GET'], name='Add item to active cart')
    def add(self, request, pk):
        self.__prevent_if_paying()
        # TODO: adding item that already in active cart should be validated with older count
        data = {
            'product': pk,
            'count': 1
        } 
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        user, guid = get_user_or_guest(self.request)
        cart_serializer = CartSerializer(CartManager.user_active_cart(user, guid))
        headers = self.get_success_headers(cart_serializer.data)
        return Response(cart_serializer.data, status=status.HTTP_201_CREATED, headers=headers)


    @action(detail=True, methods=['GET'], name='Remove item from active cart')
    def remove(self, request, pk):
        self.__prevent_if_paying()
        item = self.get_object()

        if item.count == 1:
            item.delete()
        else:
            item.count = item.count - 1
            item.save()


        user, guid = get_user_or_guest(self.request)
        cart_serializer = CartSerializer(CartManager.user_active_cart(user, guid))
        headers = self.get_success_headers(cart_serializer.data)
        self.__clear_invoice()
        return Response(cart_serializer.data, status=status.HTTP_200_OK, headers=headers)


    def perform_create(self, serializer):
        ''' Add selected product to user active cart

            Get user active cart, check if product is already in cart or not,
            if not, create cart_item, else update that cart_item

            Check if item exists or not, if exists, add count of that item to requested
            count and do the validation over the product, if not procceed vaidation only
            with requested count. It should create product in case of non-existance or
            update in in case that is exists
        '''
        user, guid = get_user_or_guest(self.request)
        active_cart = CartManager.user_active_cart(user, guid)
        product = serializer.validated_data.get('product')
        count = serializer.validated_data.get('count')

        cart_item = CartItem.objects.filter(product=product, cart=active_cart).first()
        if cart_item:
            count = count + cart_item.count

        if not ProductManager.is_product_available(product, count):
            raise ValidationError(_('محصول در دسترس نیست'))

        if not ProductManager.has_enough_items_in_stock(product, count):
            raise ValidationError(_('فروشنده قادر به تامین کالا به میزان درخواستی شما نمی‌باشد'))

        # Make product jsonify take some time, so it should be after validation
        product_jsonify = ProductLastStateSerializer(product)

        if cart_item:
            cart_item.count = count
            cart_item.product_last_state = product_jsonify.data
            cart_item.save()
        else:
            serializer.save(cart=active_cart, product_last_state=product_jsonify.data)
        self.__clear_invoice()

    def __clear_invoice(self):
        ''' Unset coupons and address related to this cart invoice '''
        cart = self.get_active_cart()
        invoice = cart.invoice
        invoice.address = None
        for usage in invoice.coupon_usages.all():
            usage.delete()
        invoice.save()

    def get_active_cart(self):
        user, guid = get_user_or_guest(self.request)
        active_cart = CartManager.user_active_cart(user, guid)
        return active_cart

    def perform_update(self, serializer):
        self.__prevent_if_paying()
        # TODO: check if permissions are correct
        user, guid = get_user_or_guest(self.request)
        cart_item = self.get_object()
        count = serializer.validated_data.get('count')
        if not ProductManager.is_product_available(cart_item.product, count):
            raise ValidationError(_('محصول در دسترس نیست و یا به تعداد کافی از این محصول در انبار وجود ندارد'))
        product_jsonify = ProductLastStateSerializer(cart_item.product)
        serializer.save(product_last_state=product_jsonify.data)
        self.__clear_invoice()

    def __prevent_if_paying(self):
        ''' Prevent user from modifying cart when invoice is in payment gateway'''
        cart = self.get_active_cart()
        if hasattr(cart, 'invoice') and cart.invoice.status == Invoice.Statuses.PAYING:
            raise ValidationError('شما در حال پرداخت فاکتور هستید و نمی‌توانید سبد خرید را تغییر دهید. در صورتی که تا دقایقی دیگر مشکل شما برطرف نشد با پشتیبانی تماس بگیرید')

    serializer_class = CartItemSerializer
    authentication_classes = [CsrfExemptSessionAuthentication, ]
    permission_classes = [IsCartItemOwner, ]
