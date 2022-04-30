from django.db import models

# Create your models here.
from invoice.models import InvoiceItem


class InvoiceItemReport(InvoiceItem):
    """
    This class is used to create a report for the invoice items.
    """
    class Meta:
        proxy = True
        verbose_name = 'گزارش محصولات فاکتور شده'
        verbose_name_plural = 'گزارش محصولات فاکتور شده'