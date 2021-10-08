from django.db import models


class ProductManager(models.Manager):
    def all_products(self):
        return self.all()