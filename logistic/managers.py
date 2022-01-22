from django.core.files import File
from datetime import datetime
from nakhll_market.models import City, ProductManager
import uuid
from django.db import models
from rest_framework.generics import get_object_or_404


class AddressManager(models.Manager):
    pass


class ShopLogisticUnitManager(models.Manager):
    
    def generate_shop_logistic_units(self, shop):
        slu = self.create(shop=shop, name='ارسال رایگان', is_active=False,
                          logo_type=models.ShopLogisticUnit.LogoType.FREE)
        sluc = models.ShopLogisticUnitConstraint.objects.create(
            shop_logistic_unit=slu
        )
        slum = models.ShopLogisticUnitCalculationMetric.objects.create(
            shop_logistic_unit=slu, price_per_kilogram=0, price_per_extra_kilogram=0
        )

        slu = self.create(shop=shop, name='پیک', is_active=False,
                          logo_type=models.ShopLogisticUnit.LogoType.DELIVERY)
        sluc = models.ShopLogisticUnitConstraint.objects.create(
            shop_logistic_unit=slu,
        )
        try:
            sluc.cities.add(City.objects.get(name=shop.City))
        except:
            pass
        slum = models.ShopLogisticUnitCalculationMetric.objects.create(
            shop_logistic_unit=slu, price_per_kilogram=0, price_per_extra_kilogram=0
        )
  
        slu = self.create(shop=shop, name='پسکرایه', is_active=True,
                          logo_type=models.ShopLogisticUnit.LogoType.PAD)
        sluc = models.ShopLogisticUnitConstraint.objects.create(
            shop_logistic_unit=slu
        )
        slum = models.ShopLogisticUnitCalculationMetric.objects.create(
            shop_logistic_unit=slu, price_per_kilogram=0, price_per_extra_kilogram=0
        )

        slu = self.create(shop=shop, name='پست پیشتاز', is_active=True,
                          logo_type=models.ShopLogisticUnit.LogoType.PPOST)
        sluc = models.ShopLogisticUnitConstraint.objects.create(
            shop_logistic_unit=slu, max_weight=40
        )
        slum = models.ShopLogisticUnitCalculationMetric.objects.create(
            shop_logistic_unit=slu, price_per_kilogram=150000, price_per_extra_kilogram=25000
        )
        
        slu = self.create(shop=shop, name='پست سفارشی', is_active=True,
                          logo_type=models.ShopLogisticUnit.LogoType.SPOST)
        sluc = models.ShopLogisticUnitConstraint.objects.create(
            shop_logistic_unit=slu, max_weight=40
        )
        slum = models.ShopLogisticUnitCalculationMetric.objects.create(
            shop_logistic_unit=slu, price_per_kilogram=140000, price_per_extra_kilogram=20000
        )

        

from logistic import models