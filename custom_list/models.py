from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _
from nakhll_market.models import Product

# Create your models here.

class Favorite(models.Model):
    ''' List of user favorite products '''
    product = models.ManyToManyField(Product, verbose_name=_('محصول'), related_name='user_favorites')
    user = models.OneToOneField(User, verbose_name=_('کاربر'), on_delete=models.CASCADE, related_name='favorite_list')