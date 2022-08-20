from django.db import models
from django.db.models import Count


class BaseReferrerEventQuerySet(models.QuerySet):
    def filter_new_events(self):
        from refer.models import ReferrerEventStatuses
        return self.filter(
            status=ReferrerEventStatuses.NEW)

    def count_events(self):
        return self.aggregate(
            count=Count('pk'))

    def event_report(self,):
        queryset = self.values('status').annotate(
            count=Count('pk'))
        self._update_status_to_labels(queryset)
        return queryset

    def _update_status_to_labels(self, queryset):
        from refer.models import ReferrerEventStatuses
        list(map(lambda row: row.update(
            {
                'status_label': ReferrerEventStatuses(row['status']).label,
            }
        ), queryset))


class BaseReferrerEventManager(models.Manager):
    def get_queryset(self):
        return BaseReferrerEventQuerySet(self.model, using=self._db)

    def new_events_count(self, referrer):
        queryset = self.get_queryset().filter(
            referrer=referrer).filter_new_events().count()
