from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import ugettext_lazy as _
from nakhll_market.models import Product


User = get_user_model()


class Favorite(models.Model):
    """ List of user favorite products

    Attributes:
        user (User): User that owns the favorite list
        products (Product): Products that are in the favorite list
    """
    products = models.ManyToManyField(
        Product, verbose_name=_('محصول'),
        related_name='user_favorites')
    user = models.OneToOneField(
        User,
        verbose_name=_('کاربر'),
        on_delete=models.CASCADE,
        related_name='favorite_list')
