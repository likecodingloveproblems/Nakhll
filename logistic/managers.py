from django.db import models
from logistic import models
from nakhll_market.models import City


class AddressManager(models.Manager):
    """Manager class for :attr:`logistic.models.Address` model"""
    pass


class ShopLogisticUnitManager(models.Manager):
    """Manager class for :attr:`logistic.models.ShopLogisticUnit` model"""

    def generate_shop_logistic_units(self, shop):
        """For each shop, create 5 default logistic units

        Default logistic units for each shop are:
            - Free
            - Delivery
            - PAD(Pay at delivery)
            - Express Mail Service
            - Mail Service
        """
        slu = self.create(shop=shop, name='ارسال رایگان', is_active=False,
                          logo_type=models.ShopLogisticUnit.LogoType.FREE)
        sluc = models.ShopLogisticUnitConstraint.objects.create(
            shop_logistic_unit=slu
        )
        slum = models.ShopLogisticUnitCalculationMetric.objects.create(
            shop_logistic_unit=slu,
            price_per_kilogram=0,
            price_per_extra_kilogram=0
        )

        slu = self.create(shop=shop, name='پیک', is_active=False,
                          logo_type=models.ShopLogisticUnit.LogoType.DELIVERY)
        sluc = models.ShopLogisticUnitConstraint.objects.create(
            shop_logistic_unit=slu,
        )
        try:
            sluc.cities.add(City.objects.get(name=shop.City))
        except BaseException:
            pass
        slum = models.ShopLogisticUnitCalculationMetric.objects.create(
            shop_logistic_unit=slu,
            price_per_kilogram=0,
            price_per_extra_kilogram=0
        )

        slu = self.create(shop=shop, name='پسکرایه', is_active=False,
                          logo_type=models.ShopLogisticUnit.LogoType.PAD)
        sluc = models.ShopLogisticUnitConstraint.objects.create(
            shop_logistic_unit=slu
        )
        slum = models.ShopLogisticUnitCalculationMetric.objects.create(
            shop_logistic_unit=slu,
            price_per_kilogram=0,
            price_per_extra_kilogram=0
        )

        slu = self.create(shop=shop, name='پست پیشتاز', is_active=True,
                          logo_type=models.ShopLogisticUnit.LogoType.PPOST)
        sluc = models.ShopLogisticUnitConstraint.objects.create(
            shop_logistic_unit=slu, max_weight=40
        )
        slum = models.ShopLogisticUnitCalculationMetric.objects.create(
            shop_logistic_unit=slu, price_per_kilogram=150000,
            price_per_extra_kilogram=25000)

        slu = self.create(shop=shop, name='پست سفارشی', is_active=True,
                          logo_type=models.ShopLogisticUnit.LogoType.SPOST)
        sluc = models.ShopLogisticUnitConstraint.objects.create(
            shop_logistic_unit=slu, max_weight=40
        )
        slum = models.ShopLogisticUnitCalculationMetric.objects.create(
            shop_logistic_unit=slu, price_per_kilogram=140000,
            price_per_extra_kilogram=20000)
