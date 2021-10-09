from django.db import models

class AccountingManager(models.Manager):
    def completed_user_invoices(self, user):
        statuses = models.Invoice.Statuses
        return self.filter(items__product__FK_Shop__FK_ShopManager=user, status__in=[
            statuses.COMPLETED, statuses.CANCELED]).order_by('-created_datetime')
 
    def completed_user_shop_factors(self, user, shop_slug):
        statuses = models.Invoice.Statuses
        return self.filter(items__product__FK_Shop__FK_ShopManager=user,
            items__product__FK_Shop__Slug=shop_slug, status__in=[
            statuses.COMPLETED, statuses.CANCELED]).order_by('-created_datetime')

   
    def uncompleted_user_invoices(self, user):
        statuses = models.Invoice.Statuses
        return self.filter(items__product__FK_Shop__FK_ShopManager=user, status__in=[
            statuses.AWAIT_CUSTOMER_APPROVAL, statuses.AWAIT_SHOP_CHECKOUT,
            statuses.AWAIT_SHOP_APPROVAL,statuses.PREPATING_PRODUCT
            ]).order_by('-created_datetime')

    def uncompleted_user_shop_factors(self, user, shop_slug):
        statuses = models.Invoice.Statuses
        return self.filter(items__product__FK_Shop__FK_ShopManager=user,
            items__product__FK_Shop__Slug=shop_slug, status__in=[
            statuses.AWAIT_CUSTOMER_APPROVAL, statuses.AWAIT_SHOP_CHECKOUT,
            statuses.AWAIT_SHOP_APPROVAL,statuses.PREPATING_PRODUCT
            ]).order_by('-created_datetime')


import accounting_new.models as models