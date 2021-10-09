from django.db import models

class AccountingManager(models.Manager):
    pass
class InvoiceItemManager(models.Manager):
    def uncompleted_user_shop_factors(self, user, shop_slug):
        statuses = models.InvoiceItem.ItemStatuses
        return self.filter(product__FK_Shop__FK_ShopManager=user,
            product__FK_Shop__Slug=shop_slug, status__in=[
            statuses.AWAIT_CUSTOMER_APPROVAL, statuses.AWAIT_SHOP_CHECKOUT,
            statuses.AWAIT_SHOP_APPROVAL,statuses.PREPATING_PRODUCT
            ]).order_by('-added_datetime')

    def completed_user_shop_factors(self, user, shop_slug):
        statuses = models.InvoiceItem.ItemStatuses
        return self.filter(product__FK_Shop__FK_ShopManager=user,
            product__FK_Shop__Slug=shop_slug, status__in=[
            statuses.COMPLETED, statuses.CANCELED,]).order_by('-added_datetime')

import accounting_new.models as models