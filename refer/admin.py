from django.contrib import admin
from nakhll.admin_utils import ReadOnlyModelAdmin

from refer.models import (
    ReferrerVisitEvent,
    ReferrerSignupEvent,
    ReferrerPurchaseEvent)


@admin.register(ReferrerVisitEvent)
class ReferrerVisitEventAdmin(ReadOnlyModelAdmin):
    pass


@admin.register(ReferrerSignupEvent)
class ReferrerSignupEventAdmin(ReadOnlyModelAdmin):
    pass


@admin.register(ReferrerPurchaseEvent)
class ReferrerPurchaseEventAdmin(ReadOnlyModelAdmin):
    pass
