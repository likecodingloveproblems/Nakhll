from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django_jalali.db import models as jmodels
from refer.constants import (
    PURCHASE_LIMIT,
    PURCHASE_REWARD,
    REFERRER_PURCHASE_LIMIT,
    REFERRER_PURCHASE_REWARD,
    REFERRER_SIGNUP_LIMIT,
    REFERRER_SIGNUP_REWARD,
    REFERRER_VISIT_LIMIT,
    REFERRER_VISIT_REWARD,
)

from refer.managers import BaseEventManager
from invoice.models import Invoice


class BaseReferrerEventModel(models.Model):
    class Statuses(models.IntegerChoices):
        NEW = 0
        PROCESSED = 1
        INACTIVE = 2
    status = models.IntegerField(choices=Statuses.choices, default=Statuses.NEW)
    referrer = models.ForeignKey(User, on_delete=models.PROTECT)
    user_agent = models.TextField()
    ip_address = models.CharField(max_length=50)
    platform = models.CharField(max_length=50)
    date_created = jmodels.jDateTimeField(auto_now_add=True)
    objects = BaseEventManager()

    class Meta:
        abstract = True


class ReferrerVisitEvent(models.Model):
    limit = REFERRER_VISIT_LIMIT
    reward = REFERRER_VISIT_REWARD

    class Meta(BaseReferrerEventModel.Meta):
        verbose_name = _("ReferrerVisitEvent")
        verbose_name_plural = _("ReferrerVisitEvent")


class ReferrerSignupEvent(BaseReferrerEventModel):
    limit = REFERRER_SIGNUP_LIMIT
    reward = REFERRER_SIGNUP_REWARD
    referred = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='referred_signup_events')

    class Meta(BaseReferrerEventModel.Meta):
        verbose_name = _("ReferrerSignupEvent")
        verbose_name_plural = _("ReferrerSignupEvents")


class ReferrerPurchaseEvent(BaseReferrerEventModel):
    limit = REFERRER_PURCHASE_LIMIT
    reward = REFERRER_PURCHASE_REWARD
    invoice = models.ForeignKey(Invoice, on_delete=models.PROTECT)

    class Meta(BaseReferrerEventModel.Meta):
        verbose_name = _("ReferrerPurchaseEvent")
        verbose_name_plural = _("ReferrerPurchaseEvents")


class PurchaseEvent(BaseReferrerEventModel):
    limit = PURCHASE_LIMIT
    reward = PURCHASE_REWARD
    invoice = models.ForeignKey(Invoice, on_delete=models.PROTECT)

    class Meta(BaseReferrerEventModel.Meta):
        verbose_name = _("PurchaseEvent")
        verbose_name_plural = _("PurchaseEvents")
