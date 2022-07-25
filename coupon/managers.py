from django.db import models
from django.db.models import Q, F, Sum, Count
from django.utils import timezone


class CouponManager(models.Manager):
    """Manager class for Coupon model"""

    def active_coupons(self):
        """Get all coupons that are active and user can use it.

        NOTE: this function is not working properly.
        """
        now = timezone.now()
        return self.annotate(
            total_usages_price=Sum('usages__price_applied'),
            total_usages_count=Count('usages'),
        ).filter(
            Q(available=True) &
            Q(constraint__users__isnull=True) &
            Q(constraint__shops__isnull=True) &
            Q(constraint__products__isnull=True) &
            Q(Q(constraint__valid_from__lt=now) | Q(constraint__valid_from__isnull=True)) &
            Q(Q(constraint__valid_to__gt=now) | Q(constraint__valid_to__isnull=True)) &
            Q(Q(constraint__budget__gt=F('total_usages_price')) | Q(constraint__budget__isnull=True)) &
            Q(Q(constraint__max_usage__gt=F('total_usages_count')) | Q(constraint__max_usage__isnull=True))
        )


class CouponUsageManager(models.Manager):
    """Manager for CouponUsage model"""
