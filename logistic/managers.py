from datetime import datetime
from nakhll_market.models import ProductManager
import uuid
from django.db import models
from rest_framework.generics import get_object_or_404


class AddressManager(models.Manager):
    pass