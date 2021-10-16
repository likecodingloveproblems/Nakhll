from django.contrib import admin
from payoff.models import Transaction, TransactionConfirmation, TransactionResult, TransactionReverse

# Register your models here.

admin.site.register(Transaction)
admin.site.register(TransactionResult)
admin.site.register(TransactionReverse)
admin.site.register(TransactionConfirmation)