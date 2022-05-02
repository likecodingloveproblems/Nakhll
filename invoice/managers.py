import jdatetime
from django.db import models
from django.db.models.aggregates import Sum
from django.db.models.expressions import Value, F
from django.db.models.fields import DecimalField
from django.db.models.functions.comparison import Coalesce
import invoice.models as invoice_models


class AccountingManager(models.Manager):
    """Manager class for Invoice model"""

    def completed_user_invoices(self, user):
        """All shop owner's invoices with status of completed or canceled"""
        statuses = invoice_models.Invoice.Statuses
        return self.filter(items__product__FK_Shop__FK_ShopManager=user,
                           status__in=[statuses.COMPLETED, statuses.CANCELED]
                           ).order_by('-created_datetime')

    def completed_user_shop_invoices(self, user, shop_slug):
        """All shop invoices with status of completed or canceled"""
        statuses = invoice_models.Invoice.Statuses
        return self.filter(items__product__FK_Shop__FK_ShopManager=user,
                           items__product__FK_Shop__Slug=shop_slug,
                           status__in=[
                               statuses.COMPLETED,
                               statuses.CANCELED
                           ]).order_by('-created_datetime')

    def uncompleted_user_invoices(self, user):
        """All shop owner's invoices that are not completed yet"""
        statuses = invoice_models.Invoice.Statuses
        return self.filter(items__product__FK_Shop__FK_ShopManager=user,
                           status__in=[
                               statuses.AWAIT_CUSTOMER_APPROVAL,
                               statuses.AWAIT_SHOP_CHECKOUT,
                               statuses.AWAIT_SHOP_APPROVAL,
                               statuses.PREPATING_PRODUCT
                           ]).order_by('-created_datetime')

    def uncompleted_user_shop_invoices(self, user, shop_slug):
        """All shop invoices that are not completed yet"""
        statuses = invoice_models.Invoice.Statuses
        return self.filter(items__product__FK_Shop__FK_ShopManager=user,
                           items__product__FK_Shop__Slug=shop_slug,
                           status__in=[
                               statuses.AWAIT_CUSTOMER_APPROVAL,
                               statuses.AWAIT_SHOP_CHECKOUT,
                               statuses.AWAIT_SHOP_APPROVAL,
                               statuses.PREPATING_PRODUCT
                           ]).order_by('-created_datetime')

    def unconfirmed_user_shop_invoices(self, user, shop_slug):
        """All shop invoices that are waiting for shop approval"""
        return self.filter(
            items__product__FK_Shop__FK_ShopManager=user,
            items__product__FK_Shop__Slug=shop_slug,
            items__status=invoice_models.InvoiceItem.ItemStatuses.
            AWAIT_SHOP_APPROVAL
        ).order_by('-created_datetime')

    def shop_invoices(self, shop_slug):
        """All shop invoices with details"""
        return self.annotate(
            coupon_price=Coalesce(
                Sum('coupon_usages__price_applied',
                    output_field=DecimalField()), Value(0)),
            price=F('invoice_price_with_discount') +
            F('logistic_price') -
            F('coupon_price'),
            weight=F('total_weight_gram'),
        ).filter(
            items__product__FK_Shop__Slug=shop_slug
        ).order_by('-created_datetime')


class InvoiceItemManager(models.Manager):
    """Manager class for InvoiceItem model"""

    def user_total_sell(self, user):
        """Shop owner's total sell

        This is the sum of all invoices with status of completed
        """
        return self.filter(
            product__FK_Shop__FK_ShopManager=user,
            invoice__status__in=[invoice_models.Invoice.Statuses.COMPLETED]
        ).aggregate(amont=Sum('product__Price'))

    def current_week_user_total_sell(self, user, shop_slug):
        """Shop owner's total sell in current week

        This is the sum of all invoices with status of completed
        """
        now = jdatetime.datetime.now()
        current_week_start_date = now - jdatetime.timedelta(days=now.weekday())
        return self.filter(
            product__FK_Shop__FK_ShopManager=user,
            invoice__status=invoice_models.Invoice.Statuses.COMPLETED,
            product__FK_Shop__Slug=shop_slug,
            invoice__created_datetime__gt=str(
                current_week_start_date.togregorian())).aggregate(
            amont=Sum('product__Price'))

    def last_week_user_total_sell(self, user, shop_slug):
        """Shop owner's total sell in last week

        This is the sum of all invoices with status of completed
        """
        now = jdatetime.datetime.now()
        current_week_start_date = now - jdatetime.timedelta(days=now.weekday())
        last_week_start_date = current_week_start_date - jdatetime.timedelta(
            days=7)
        return self.filter(
            product__FK_Shop__FK_ShopManager=user,
            invoice__status=invoice_models.Invoice.Statuses.COMPLETED,
            invoice__created_datetime__gt=str(
                last_week_start_date.togregorian()),
            invoice__created_datetime__lt=str(
                current_week_start_date.togregorian()),
            product__FK_Shop__Slug=shop_slug,).aggregate(
            amont=Sum('product__Price'))

    def last_month_user_total_sell(self, user, shop_slug):
        """Shop owner's total sell in last month

        This is the sum of all invoices with status of completed
        """
        now = jdatetime.datetime.now()
        current_month_start_date = now.replace(day=1)
        last_month_start_date = current_month_start_date - \
            jdatetime.timedelta(days=30)
        return self.filter(
            product__FK_Shop__FK_ShopManager=user,
            invoice__status=invoice_models.Invoice.Statuses.COMPLETED,
            product__FK_Shop__Slug=shop_slug,
            invoice__created_datetime__gt=str(
                last_month_start_date.togregorian()),
            invoice_created_datetime__lt=str(
                current_month_start_date.togregorian())
        ).aggregate(amont=Sum('product__Price'))
