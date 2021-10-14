from django.contrib import admin
from .models import TicketingMessage ,Ticketing

#-------------------------------------------------
#Ticketing admin panel
class TicketingMessageInline(admin.StackedInline):
    model=TicketingMessage
    extra=1

@admin.register(Ticketing)
class TicketingAdmin(admin.ModelAdmin):
    list_display=('ID','Title','FK_Importer','Date','SeenStatus')
    list_filter=('Date','SeenStatus')
    ordering=['Date','ID','SeenStatus']
    inlines=[TicketingMessageInline]
