from django.db import models
from django.utils.translation import ugettext as _


class RequestStatuses(models.IntegerChoices):
    PENDING = 0, _('در انتظار')
    CONFIRMED = 1, _('تایید شده')
    REJECTED = 2, _('رد شده')


class RequestTypes(models.IntegerChoices):
    REFERRER_VISIT_REWARD = 0, _('پاداش بازدید')
    REFERRER_SIGNUP_REWARD = 1, _('پاداش ثبت نام')
    REFERRER_PURCHASE_REWARD = 2, _('پاداش خرید بازار یاب')
    PURCHASE_REWARD = 3, _('پاداش خرید خریدار')
    BUY_FROM_NAKHLL = 4, _('خرید از نخل')
    WITHDRAW = 5, _('تسویه حساب')
    DEPOSIT = 6, _('واریز')
    FINANCIAL_TO_FUND = 7, _('از حساب مالی به صندوق')


COIN_RIAL_RATIO = 100_000
WITHDRAW_BALANCE_LIMIT = 21
SYSTEMIC_ACCOUNTS_ID_UPPER_LIMIT = 0
FUND_ACCOUNT_ID = -1
FINANCIAL_ACCOUNT_ID = -2
CASHABLE_REQUEST_TYPES = [
    RequestTypes.REFERRER_VISIT_REWARD,
    RequestTypes.REFERRER_SIGNUP_REWARD,
    RequestTypes.REFERRER_PURCHASE_REWARD,
]
AUTOMATIC_CONFIRM_REQUEST_TYPES = [
    RequestTypes.REFERRER_VISIT_REWARD,
    RequestTypes.REFERRER_SIGNUP_REWARD,
    RequestTypes.REFERRER_PURCHASE_REWARD,
    RequestTypes.PURCHASE_REWARD,
]
