import uuid
from django.db import models
from cart import models as cart_models


class CartManager(models.Manager):
    """Manager object for Cart model"""

    @staticmethod
    def convert_guest_to_user_cart(user, guid):
        """Convert guest cart to user cart after guest login

        For logged out users, we store the cart in a cookie with a unique key
        called guid, after successful login we convert the cart to a user cart
        If user already has a cart, we merge the guest cart with the user cart

        Args:
            user (User): User object
            guid (str): Unique id for guest cart
        """
        guest_cart = cart_models.Cart.objects.filter(
            user=None, guest_unique_id=guid).first()
        user_cart = cart_models.Cart.objects.filter(user=user).first()
        if guest_cart and user_cart:
            CartManager.merge_carts(user_cart, guest_cart)
        if guest_cart and not user_cart:
            guest_cart.user = user
            guest_cart.save()

    @staticmethod
    def merge_carts(base_cart, guest_cart):
        """Combine user cart with guest cart

        This merge is needed when we have a user that has a cart with some
        items in it, but now is logged out and fills his/her cart with items
        as a guest. so after login, we should combine the two carts.

        Args:
            base_cart (Cart): user's main cart
            guets_cart (Cart): user's guest cart

        Returns:
            None
        """
        base_cart_product_ids = base_cart.items.all().values_list(
            'product__ID', flat=True
        )
        for item in guest_cart.items.all():
            if item.product.ID in base_cart_product_ids:
                base_cart_item = base_cart.items.get(product=item.product)
                base_cart_item.count += item.count
                base_cart_item.save()
            else:
                base_cart.items.add(item)

    @staticmethod
    def generate_guid():
        """Generate an ID for guest carts

        Returns:
            str: UUID 4 in HEX
        """
        return uuid.uuid4().hex

    @staticmethod
    def _get_user_cart(user, guid=None):
        cart, created = \
            cart_models.Cart.objects.get_or_create(user=user) if user else \
            cart_models.Cart.objects.get_or_create(guest_unique_id=guid or CartManager.generate_guid())
        return cart


class CartItemManager(models.Manager):
    """Cart Item Manager"""
