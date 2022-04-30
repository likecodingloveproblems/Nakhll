from django.contrib import admin
from panel_admins.reports import reports_admin_site
# Register your models here.
from .models import InvoiceItemReport, InoviceProxy


@admin.register(InvoiceItemReport, site=reports_admin_site)
class InvoiceItemReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'invoice', 'invoice_status', 'product_name', 'product_shop')
    list_filter = ('invoice', 'product')
    search_fields = ('invoice', 'product')
    ordering = ('-id',)

    # product items
    @staticmethod
    def product_name(obj):
        return obj.product.Title
    product_name.short_description = 'اسم محصول'

    @staticmethod
    def product_shop(obj):
        return obj.product.FK_Shop.Title



    # invoice items
    @staticmethod
    def invoice_status(obj):
        return obj.invoice.status

    def get_queryset(self, request):
        qs = super(InvoiceItemReportAdmin, self).get_queryset(request)
        qs = qs.filter(invoice__status=InoviceProxy.Statuses.COMPLETED)
        return qs.select_related('invoice', 'product')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False
