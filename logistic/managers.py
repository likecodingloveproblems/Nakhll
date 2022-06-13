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
  
        slu = self.create(shop=shop, name='پسکرایه', is_active=False,
                          logo_type=models.ShopLogisticUnit.LogoType.PAD)
        sluc = models.ShopLogisticUnitConstraint.objects.create(
            shop_logistic_unit=slu
        )
        slum = models.ShopLogisticUnitCalculationMetric.objects.create(
            shop_logistic_unit=slu, price_per_kilogram=0, price_per_extra_kilogram=0
        )
        try:
            default_post_metrics = self.get_default_post_metrics()
            slu = self.create(
                shop=shop,
                name=default_post_metrics['PPOST'].get_name_display(),
                is_active=True,
                logo_type=models.ShopLogisticUnit.LogoType.PPOST)
            sluc = models.ShopLogisticUnitConstraint.objects.create(
                shop_logistic_unit=slu, max_weight=40
            )
            slum = models.ShopLogisticUnitCalculationMetric.objects.create(
                shop_logistic_unit=slu,
                price_per_kilogram=default_post_metrics['PPOST'].default_price_per_kilogram,
                price_per_extra_kilogram=default_post_metrics['PPOST'].default_price_per_extra_kilogram)

            slu = self.create(
                shop=shop,
                name=default_post_metrics['SPOST'].get_name_display(),
                is_active=True,
                logo_type=models.ShopLogisticUnit.LogoType.SPOST)
            sluc = models.ShopLogisticUnitConstraint.objects.create(
                shop_logistic_unit=slu, max_weight=40
            )
            slum = models.ShopLogisticUnitCalculationMetric.objects.create(
                shop_logistic_unit=slu,
                price_per_kilogram=default_post_metrics['SPOST'].default_price_per_kilogram,
                price_per_extra_kilogram=default_post_metrics['SPOST'].default_price_per_extra_kilogram)
        except (
            models.LogisticUnitGeneralSetting.DoesNotExist, 
            models.LogisticUnitGeneralSetting.MultipleObjectsReturned
            ):
            '''If we don't have post pishtaz and sefareshi in LogisticUnitGeneralSetting,
            then we don't have to create post pishtaz and sefareshi in ShopLogisticUnit 
            as default shop logistic units, but logistic team must be aware of this!'''

    def get_default_post_metrics(self):
        return {
            'PPOST': models.LogisticUnitGeneralSetting.objects.get(
                name=models.LogisticUnitGeneralSetting.Name.PISHTAZ),
            'SPOST': models.LogisticUnitGeneralSetting.objects.get(
                name=models.LogisticUnitGeneralSetting.Name.SEFARESHI)
        }



        

from logistic import models