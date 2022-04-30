from django.contrib import admin
from panel_admins.reports import ReportsAdminSite
# Register your models here.
from invoice.models import InvoiceItem


@admin.register(InvoiceItem, site=ReportsAdminSite)
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'invoice', 'product',)
    list_filter = ('invoice', 'product')
    search_fields = ('invoice', 'product')
    ordering = ('id',)
    readonly_fields = ('id',)
    def has_add_permission(self, request):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
    def has_change_permission(self, request, obj=None):
        return False
