from django.db import models
from django.utils.translation import ugettext as _


class RequestStatuses(models.IntegerChoices):
    PENDING = 0, _('در انتظار')
    CONFIRMED = 1, _('تایید شده')
    REJECTED = 2, _('رد شده')


class RequestTypes(models.IntegerChoices):
    REFERRER_VISIT_REWARD = 1
    REFERRER_SIGNUP_REWARD = 2
    REFERRER_BUY_REWARD = 3
    REFERRED_BUY_REWARD = 4
    BUY_FROM_SHOP = 5
    WITHDRAW = 6
    DEPOSIT = 7


NAKHLL_ACCOUNT_ID = 1
CASHABLE_REQUESTS_TYPES = [
    RequestTypes.REFERRER_VISIT_REWARD,
    RequestTypes.REFERRER_SIGNUP_REWARD,
    RequestTypes.REFERRER_BUY_REWARD,
    RequestTypes.REFERRED_BUY_REWARD,
    RequestTypes.BUY_FROM_SHOP,
]
