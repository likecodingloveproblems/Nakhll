from datetime import datetime
from nakhll_market.models import ProductManager
import uuid
from django.db import models
from rest_framework.generics import get_object_or_404


class CartManager(models.Manager):
    def user_active_cart(user, guid=None):
        cart, created = \
            cart_models.Cart.objects.get_or_create(user=user, status=cart_models.Cart.Statuses.IN_PROGRESS) \
            if user else \
            cart_models.Cart.objects.get_or_create(guest_unique_id=guid or uuid.uuid4(), status=cart_models.Cart.Statuses.IN_PROGRESS)
        return cart

    def user_carts(self, user, guid=None):
        ''' Does guest user can have multi carts at all? '''
        return \
            self.filter(user=user) \
            if user else \
            self.filter(guest_unique_id=guid or uuid.uuid4())


    @staticmethod
    def convert_guest_to_user_cart(user, guid):
        '''Check if there is a cart with guid and no user '''
        guest_cart = cart_models.Cart.objects.filter(user=None, guest_unique_id=guid).first()
        if guest_cart:
            guest_cart.user = user
            guest_cart.save()

    # May change
    def send_user_active_cart(self, user, guid=None):
        '''Send active cart to accounting app to handle that '''
        cart = self.user_active_cart(user, guid)

    def close_user_active_cart(self, user):
        ''' Set active cart status to finished so new cart with new items will generate next time 
            note that carts that received from accounting app is not belong to guest and only user
            should sent to this function 
        '''
        cart = self.user_active_cart(user)
        cart.status = cart_models.Cart.Statuses.CLOSED
        cart.change_status_datetime = datetime.now()
        cart.save()

    def check_cart_items(self, user, guid):
        cart = self.user_active_cart(user, guid)
        cart_items = [{'product': x.product, 'count': x.count} for x in cart.cart_items.all()]
        return ProductManager.is_product_list_valid(cart_items)


        

class CartItemManager(models.Manager):
    @staticmethod
    def user_cartitem(user, guid, item_id):
        user_carts = cart_models.Cart.objects.user_carts(user, guid)
        return get_object_or_404(cart_models.CartItem, id=item_id, cart__in=user_carts)

    @staticmethod
    def user_cartitems(user, guid):
        active_cart = CartManager.user_active_cart(user, guid)
        return active_cart.items.all()



# Importing a module in the bottom of file prevents circular import error
import cart.models as cart_models