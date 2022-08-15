from django.contrib import admin
from nakhll.admin_utils import ReadOnlyModelAdmin

from refer.models import (
    ReferrerVisitEvent,
    ReferrerSignupEvent,
    ReferrerPurchaseEvent)


@admin.register(ReferrerVisitEvent)
class ReferrerVisitEventAdmin(ReadOnlyModelAdmin):
    list_display = [
        'referrer',
        'status',
        'date_created',
        'date_updated', ]


@admin.register(ReferrerSignupEvent)
class ReferrerSignupEventAdmin(ReadOnlyModelAdmin):
    list_display = [
        'referrer',
        'referred',
        'status',
        'date_created',
        'date_updated', ]


@admin.register(ReferrerPurchaseEvent)
class ReferrerPurchaseEventAdmin(ReadOnlyModelAdmin):
    list_display = [
        'referrer',
        'invoice',
        'status',
        'date_created',
        'date_updated', ]
