from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from cart.managers import CartManager
from django.utils.translation import ugettext as _
from rest_framework import viewsets
from nakhll_market.models import ProductManager
from cart.models import Cart, CartItem
from cart.serializers import CartSerializer, CartItemSerializer
from cart.utils import get_user_or_guest
from cart.permissions import IsCartOwner, IsCartItemOwner


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

