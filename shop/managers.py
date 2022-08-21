import shop.models as shop_models
from django.db import models


class ShopFeatureManager(models.Manager):
    def published(self):
        return self.filter(is_publish=True)


class ShopLandingManager(models.Manager):
    def published(self):
        return self.filter(is_publish=True)

    def deactivate_all_landing_for_shop(self, shop):
        """In order to activate a landing, all other landings must be deactivated"""
        statuses = shop_models.ShopLanding.Statuses
        self.filter(shop=shop).update(status=statuses.INACTIVE)

    def shop_active_landing(self, shop):
        """Return the active landing for a shop"""
        return self.filter(shop=shop, status=shop_models.ShopLanding.Statuses.ACTIVE).first()
