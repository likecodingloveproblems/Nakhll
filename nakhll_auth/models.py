"""Authentication system in nakhll

There are 3 type of endpoints in nakhll web application for end users (not staff):
 - endpoints that doesn't need any type of authentication
 - endpoints that only require a logged in user
 - endpoints that a logged in user should re-authenticate before accessing
 
 The authentication method in nakhll apis is JWT. It means users should have access token
 in order to visit endpoints of secend type, and a refresh token to get new access token
 when their access token get expired. Referesh tokens will expire as well. The time of
 expiration can be set in :attr:`nakhll.settings.ACCESS_TOKEN_EXPIRE_MINUTES` and
 :attr:`nakhll.settings.REFRESH_TOKEN_EXPIRE_MINUTES`.
 
 To get access to endpoints of type 3, users should send 3 requests. The 2 requests are
 simillar for all type of endpoints, but the 3rd request is specific to each endpoint.
 Here is the flow of these 3 requests in general:
    1. This step called BeginAuth. In this step, user should begin authentication with two
        parameters, mobile number and request type for example, if you want to get access
        and refresh token, your request type is 
        :attr:`nakhll_auth.models.AuthRequest.RequestTypes.LOGIN/REGISTER`, or if you want
        to change your password, your request type is
        :attr:`nakhll_auth.models.AuthRequest.RequestTypes.FORGOT_PASSWORD`.
        In return, you will get a one-time key called auth_key, which means your request is
        saved to database and you can proceed to next step.
    2. This step called CompleteAuth. In this step, you should either send your password or 
        your SMS code which is sent to your mobile (depends on user) which is called user_key,
        and the auth_key which you get from step 1. This step will check your credentials and
        if your credentials are valid, you will get another one-time key called secret_key.
        Getting secret_key means you have successfully authenticated and you can proceed to next
        step. With this secret_key, you can send a request to your endpoint which you wanted to
        access which you began your request from step 1. Note that this key only works for
        your requested endpoint. Also this key will expire after 5 minutes or after you
        use it in step 3.
    3. This step is completely dependes on the endpoint you want to access. For example, if
        you want to get access and refresh token, you just need to send your secret_key to
        the right endpoint and you will get access and refresh token. If you want to change
        your password, you should send your secret_key and your new password to the right endpoint
        and you will get a proper response. But in all these endpoits, you have to send secret_key
        as a parameter.
"""

import uuid
from datetime import datetime, timedelta
from django.db import models
from django.utils import timezone
from .validators import mobile_number_validator


def fivemin_from_now():
    return timezone.now() + timedelta(minutes=5)


def generate_uuid_code():
    return uuid.uuid4().hex


class AuthRequestManager(models.Manager):
    """Manager for AuthRequest Model"""

    def get_by_secret(self, secret):
        """Try to get AuthRequest object by secret key or return None"""
        try:
            return self.get(auth_secret=secret, request_status=AuthRequest.RequestStatuses.PENDING)
        except AuthRequest.DoesNotExist:
            return None


class AuthRequest(models.Model):
    """Data of each authentication request

    Attributes:
        mobile: mobile number of user
        sms_code: SMS code sent to user's mobile (only of user doesn't have a password
            or if user wanted to change his password)
        auth_key: one-time key used to begin authentication
        secret_key: one-time key used to complete request
        expire_datetime: datetime when request will expire
        mobile_status: indicates if user is registered or not
        request_status: indicates if request is pending or completed
        request_type: indicates the type of request that user wants to do
        created_at: datetime when request was created
        updated_at: datetime when request was updated 
    """
    class Meta:
        verbose_name = 'درخواست احراز هویت'
        verbose_name_plural = 'درخواست احراز هویت'

    class MobileStatuses(models.TextChoices):
        NOT_REGISTERED = 'not_reg', 'شماره موبایل ثبت نشده است'
        LOGIN_WITH_CODE = 'login_code', 'ورود با کد'
        LOGIN_WITH_PASSWORD = 'login_pass', 'ورود با کلمه عبور'

    class RequestStatuses(models.TextChoices):
        PENDING = 'pending', 'در انتظار'
        COMPLETED = 'completed', 'پایان یافته'

    class RequestTypes(models.TextChoices):
        LOGIN_REGISTER = 'signin/up', 'ورود/ثبت‌نام'
        FORGOT_PASSWORD = 'forgotpass', 'فراموشی کلمه عبور'

    mobile = models.CharField(max_length=11, validators=[mobile_number_validator])
    referral_code = models.CharField(max_length=6, null=True)
    sms_code = models.CharField(max_length=6, null=True, blank=True)
    auth_key = models.CharField(max_length=32, default=generate_uuid_code)
    auth_secret = models.CharField(max_length=32, null=True, blank=True)
    expire_datetime = models.DateTimeField(default=fivemin_from_now)
    mobile_status = models.CharField(max_length=10, choices=MobileStatuses.choices)
    request_status = models.CharField(max_length=10, choices=RequestStatuses.choices, default=RequestStatuses.PENDING)
    request_type = models.CharField(max_length=10, choices=RequestTypes.choices, default=RequestTypes.LOGIN_REGISTER)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = AuthRequestManager()

    def __str__(self):
        return self.mobile + ' - ' + str(self.created_at)

    def is_expired(self):
        return timezone.now() > self.expire_datetime

    def close_request(self):
        self.request_status = self.RequestStatuses.COMPLETED
        self.save()
