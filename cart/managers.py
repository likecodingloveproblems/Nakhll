import uuid
from django.db import models


class CartManager(models.Manager):
    def user_active_cart(user, guid=None):
        cart, created = \
            cart_models.Cart.objects.get_or_create(user=user) if user else \
            cart_models.Cart.objects.get_or_create(guest_unique_id=guid or CartManager.generate_guid())
        return cart

    def user_carts(self, user, guid=None):
        return \
            self.filter(user=user) \
            if user else \
            self.filter(guest_unique_id=guid or CartManager.generate_guid())

    @staticmethod
    def convert_guest_to_user_cart(user, guid):
        '''Check if there is a cart with guid and no user '''
        guest_cart = cart_models.Cart.objects.filter(user=None, guest_unique_id=guid).first()
        user_cart = cart_models.Cart.objects.filter(user=user).first()
        if guest_cart and user_cart:
            CartManager.merge_carts(user_cart, guest_cart)
        if guest_cart and not user_cart:
            guest_cart.user = user
            guest_cart.save()

    @staticmethod
    def merge_carts(base_cart, guest_cart):
        base_cart_product_ids = base_cart.items.all().values_list('product__ID', flat=True)
        for item in guest_cart.items.all():
            if item.product.ID in base_cart_product_ids:
                base_cart_item = base_cart.items.get(product=item.product)
                base_cart_item.count += item.count
                base_cart_item.save()
            else:
                base_cart.items.add(item)

    @staticmethod
    def generate_guid():
        return uuid.uuid4().hex
        

class CartItemManager(models.Manager):
    ''' Cart Item Manager '''
    
    
# Importing a module in the bottom of file prevents circular import error
from cart import models as cart_models