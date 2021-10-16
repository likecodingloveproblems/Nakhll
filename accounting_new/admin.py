from django.contrib import admin
from accounting_new.models import Invoice, InvoiceItem

# Register your models here.
admin.site.register(Invoice)
admin.site.register(InvoiceItem)
