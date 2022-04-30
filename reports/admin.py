from django.contrib import admin
from panel_admins.reports import reports_admin_site
# Register your models here.
from .models import InvoiceItemReport


@admin.register(InvoiceItemReport, site=reports_admin_site)
class InvoiceItemReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'invoice', 'product',)
    list_filter = ('invoice', 'product')
    search_fields = ('invoice', 'product')
    ordering = ('-id',)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False
