from django.utils import timezone
from django.db import models, transaction
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django_jalali.db import models as jmodels
import pgtrigger
from bank.views import deposit_user

from refer.constants import (
    REFERRER_PURCHASE_LIMIT,
    REFERRER_PURCHASE_REWARD,
    REFERRER_SIGNUP_LIMIT,
    REFERRER_SIGNUP_REWARD,
    REFERRER_VISIT_LIMIT,
    REFERRER_VISIT_REWARD,
)
from bank.constants import RequestTypes


class RequestData(models.Model):
    user_agent = models.TextField()
    ip_address = models.CharField(max_length=50)
    platform = models.CharField(max_length=50)

    class Meta:
        abstract = True

    @property
    def request(self):
        return f'user agent:{self.user_agent} - ip address:{self.ip_address} - platform:{self.platform}'

    @request.setter
    def request(self, request):
        self.user_agent = request.META.get('HTTP_USER_AGENT'),
        self.ip_address = request.META.get('REMOTE_ADDR'),
        self.platform = request.META.get('HTTP_SEC_CH_UA_PLATFORM'),


class ReferrerEventStatuses(models.IntegerChoices):
    NEW = 0
    PROCESSED = 1
    INACTIVE = 2


class BaseReferrerEventModel(models.Model):
    status = models.IntegerField(
        choices=ReferrerEventStatuses.choices,
        default=ReferrerEventStatuses.NEW)
    referrer = models.ForeignKey(User, on_delete=models.PROTECT)
    date_created = jmodels.jDateTimeField(auto_now_add=True)
    date_updated = jmodels.jDateTimeField(auto_now=True)

    class Meta:
        abstract = True
        triggers = [
            pgtrigger.Protect(
                name='protect_from_deletes',
                operation=(pgtrigger.Delete)),
            pgtrigger.Protect(
                name='protect_not_new_events_from_update',
                operation=(pgtrigger.Update),
                condition=pgtrigger.Q(old__status__in=[
                    ReferrerEventStatuses.PROCESSED,
                    ReferrerEventStatuses.INACTIVE
                ])
            )
        ]

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self._update_status_from_link_status()
        super().save(force_insert, force_update, using, update_fields)
        self._give_reward()

    def _give_reward(self):
        events = self._get_referrer_new_events(self.referrer)
        count = events.count()
        blocks = count // self.LIMIT
        coins = blocks * self.REWARD
        if coins:
            self._update_events_status(events, blocks * self.LIMIT)
            deposit_user(
                user=self.referrer,
                request_type=self.REQUEST_TYPE,
                amount=coins,
                description=self._get_description())

    @classmethod
    def _get_referrer_new_events(cls, referrer):
        return cls.objects.get_queryset().filter(
            referrer=referrer, status=ReferrerEventStatuses.NEW
        )

    @classmethod
    def _update_events_status(cls, events, count):
        cls.objects.filter(pk__in=events[:count].values('pk')).update(
            status=ReferrerEventStatuses.PROCESSED)


    def _update_status_from_link_status(self):
        """Update event status based on the user referral link status
        if referrer link is expired, then event is not active
        so referrer won't get any coin rewarded"""
        if not self.referrer.User_Profile.is_referral_link_active():
            self.status = ReferrerEventStatuses.INACTIVE

    def _get_description(self):
        '''we can customize description for each model
        we can put constants in the description, so we have constants history.'''
        return f'referrer:{self.referrer} - type:{self.REQUEST_TYPE.label} - limit:{self.LIMIT} - reward:{self.REWARD} - date created:{timezone.now()}'


class ReferrerVisitEvent(BaseReferrerEventModel, RequestData):
    REQUEST_TYPE = RequestTypes.REFERRER_VISIT_REWARD
    LIMIT = REFERRER_VISIT_LIMIT
    REWARD = REFERRER_VISIT_REWARD

    class Meta(BaseReferrerEventModel.Meta):
        verbose_name = _("ReferrerVisitEvent")
        verbose_name_plural = _("ReferrerVisitEvent")


class ReferrerSignupEvent(BaseReferrerEventModel, RequestData):
    REQUEST_TYPE = RequestTypes.REFERRER_SIGNUP_REWARD
    LIMIT = REFERRER_SIGNUP_LIMIT
    REWARD = REFERRER_SIGNUP_REWARD
    referred = models.ForeignKey(
        User,
        unique=True,
        on_delete=models.PROTECT,
        related_name='referred_signup_events')

    class Meta(BaseReferrerEventModel.Meta):
        verbose_name = _("ReferrerSignupEvent")
        verbose_name_plural = _("ReferrerSignupEvents")


class ReferrerPurchaseEvent(BaseReferrerEventModel):
    REQUEST_TYPE = RequestTypes.REFERRER_PURCHASE_REWARD
    LIMIT = REFERRER_PURCHASE_LIMIT
    REWARD = REFERRER_PURCHASE_REWARD
    invoice = models.ForeignKey("invoice.Invoice", on_delete=models.PROTECT)

    class Meta(BaseReferrerEventModel.Meta):
        verbose_name = _("ReferrerPurchaseEvent")
        verbose_name_plural = _("ReferrerPurchaseEvents")
