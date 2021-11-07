import accounting_new.models as models
from django.db import models


class AccountingManager(models.Manager):
    def completed_user_invoices(self, user):
        statuses = models.Invoice.Statuses
        types = models.Invoice.InvoiceTypes
        return self.filter(items__product__FK_Shop__FK_ShopManager=user,
                           invoice_type=types.HOJREH,
                           status__in=[statuses.COMPLETED, statuses.CANCELED]
                           ).order_by('-created_datetime')

    def completed_user_shop_factors(self, user, shop_slug):
        statuses = models.Invoice.Statuses
        types = models.Invoice.InvoiceTypes
        return self.filter(items__product__FK_Shop__FK_ShopManager=user,
                           invoice_type=types.HOJREH,
                           items__product__FK_Shop__Slug=shop_slug, status__in=[
                               statuses.COMPLETED, statuses.CANCELED]
                           ).order_by('-created_datetime')

    def uncompleted_user_invoices(self, user):
        statuses = models.Invoice.Statuses
        types = models.Invoice.InvoiceTypes
        return self.filter(items__product__FK_Shop__FK_ShopManager=user,
                           invoice_type=types.HOJREH,
                           status__in=[
                               statuses.AWAIT_CUSTOMER_APPROVAL, statuses.AWAIT_SHOP_CHECKOUT,
                               statuses.AWAIT_SHOP_APPROVAL, statuses.PREPATING_PRODUCT
                           ]).order_by('-created_datetime')

    def uncompleted_user_shop_factors(self, user, shop_slug):
        statuses = models.Invoice.Statuses
        types = models.Invoice.InvoiceTypes
        return self.filter(items__product__FK_Shop__FK_ShopManager=user,
                           invoice_type=types.HOJREH,
                           items__product__FK_Shop__Slug=shop_slug, status__in=[
                               statuses.AWAIT_CUSTOMER_APPROVAL, statuses.AWAIT_SHOP_CHECKOUT,
                               statuses.AWAIT_SHOP_APPROVAL, statuses.PREPATING_PRODUCT
                           ]).order_by('-created_datetime')

    def all_hojreh_invoices(self):
        statuses = models.Invoice.Statuses
        types = models.Invoice.InvoiceTypes
        return self.filter(invoice_type=types.HOJREH).order_by('-created_datetime')

class InvoiceItemManager(models.Manager):
    def uncompleted_user_shop_factors(self, user, shop_slug):
        statuses = models.InvoiceItem.ItemStatuses
        types = models.Invoice.InvoiceTypes
        return self.filter(product__FK_Shop__FK_ShopManager=user,
                           invoice__invoice_type=types.HOJREH,
                           product__FK_Shop__Slug=shop_slug, status__in=[
                               statuses.AWAIT_CUSTOMER_APPROVAL, statuses.AWAIT_SHOP_CHECKOUT,
                               statuses.AWAIT_SHOP_APPROVAL, statuses.PREPATING_PRODUCT
                           ]).order_by('-added_datetime')

    def completed_user_shop_factors(self, user, shop_slug):
        statuses = models.InvoiceItem.ItemStatuses
        types = models.Invoice.InvoiceTypes
        return self.filter(product__FK_Shop__FK_ShopManager=user,
                           invoice__invoice_type=types.HOJREH,
                           product__FK_Shop__Slug=shop_slug, status__in=[
                               statuses.COMPLETED, statuses.CANCELED, ]).order_by('-added_datetime')
