from django.db import models
from django.db.models import Count


class BaseReferrerEventManager(models.Manager):
    def event_report(self, referrer):
        queryset = self.get_queryset().filter(
            referrer=referrer).values('status').annotate(
            count=Count('pk'))
        self._update_status_to_labels(queryset)
        return queryset

    def _update_status_to_labels(self, queryset):
        from refer.models import ReferrerEventStatuses
        list(map(lambda row: row.update(
            {
                'status': ReferrerEventStatuses(row['status']).label,
            }
        ), queryset))
