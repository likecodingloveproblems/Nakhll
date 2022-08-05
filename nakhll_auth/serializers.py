from django.contrib.auth import authenticate
from django.contrib.auth.models import User, update_last_login
from django.utils import timezone
from rest_framework import serializers, status, validators
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken
from .models import AuthRequest


class BeginAuthSerializer(serializers.ModelSerializer):
    """This serializer only get mobile and return mobile_status and auth_key

    Returns:
        mobile_status: indicades that user is logged in or not
        auth_key: this is a key which user should send as a parameter to
            next request with other data
    """
    class Meta:
        model = AuthRequest
        fields = ('mobile', 'auth_key', 'mobile_status', 'referral_code')
        read_only_fields = ('auth_key', 'mobile_status', )

    def to_representation(self, obj):
        """Remove mobile number from output of serializer data"""
        ret = super(BeginAuthSerializer, self).to_representation(obj)
        ret.pop('mobile')
        ret.pop('referral_code')
        return ret


class CompleteAuthSerializer(serializers.ModelSerializer):
    """Serializer data to complete authentication

    Args:
        auth_key (str): key from AuthBegin step
        user_key (str): depends on user, this key can be password or SMS code

    Returns:
        str: secret_auth is the key to submit your request
    """
    user_key = serializers.CharField(max_length=32)

    class Meta:
        model = AuthRequest
        fields = ('auth_secret', 'auth_key', 'user_key')
        write_only_fields = ('auth_secret', )

    def validate(self, data):
        auth_key = data.get('auth_key')
        user_key = data.get('user_key')
        self.instance = self._get_auth_request(auth_key)
        if not self.auth_is_valid(self.instance, user_key):
            raise serializers.ValidationError(
                {'password': 'اطلاعات برای احراز هویت معتبر نیست'}, code=status.HTTP_401_UNAUTHORIZED)
        return data

    def auth_is_valid(self, auth_request, user_key):
        """Validate user_key which can be password or code"""
        if auth_request.mobile_status == AuthRequest.MobileStatuses.LOGIN_WITH_PASSWORD\
                and auth_request.request_type != AuthRequest.RequestTypes.FORGOT_PASSWORD:
            return self.__validate_password(auth_request, user_key)
        return self.__validate_code(auth_request, user_key)

    def _get_auth_request(self, auth_key):
        """Using auth_key try to get the initial request of user"""
        try:
            return AuthRequest.objects.get(auth_key=auth_key, request_status=AuthRequest.RequestStatuses.PENDING)
        except AuthRequest.DoesNotExist:
            raise serializers.ValidationError('درخواستی برای احراز هویت وجود ندارد', code=status.HTTP_400_BAD_REQUEST)

    def __validate_password(self, auth_request, user_key):
        return bool(authenticate(username=auth_request.mobile, password=user_key))

    def __validate_code(self, auth_request, user_key):
        if timezone.now() > auth_request.expire_datetime:
            raise serializers.ValidationError('کد منقضی شده است', code=status.HTTP_401_UNAUTHORIZED)
        return bool(user_key == auth_request.sms_code)

    def to_representation(self, obj):
        """Remove user_key and auth_key from serializer return data"""
        ret = super(CompleteAuthSerializer, self).to_representation(obj)
        ret.pop('user_key')
        ret.pop('auth_key')
        return ret


class PasswordSerializer(serializers.Serializer):
    """Serializer to get new password from user and set as user's password

    This action needs authentication, so user should first get secret_key in order
    to perform this action. After that, user can send his/her new password with
    secret_key to change his/her password.

    Args:
        password (str): new password that user wants to set
        secret_key (str): one-time key that user gets from BeginAuth and CompleteAuth steps

    Returns:
        str: new password will return as result
    """
    auth_secret = serializers.CharField(max_length=32)
    password = serializers.CharField(max_length=128, write_only=True)

    def __init__(self, instance=None, data=..., **kwargs):
        self.request_type = kwargs.pop('request_type')
        super().__init__(instance=instance, data=data, **kwargs)

    def save(self):
        password = self.validated_data['password']
        self.user.set_password(password)
        self.user.save()
        self.auth.close_request()
        return self.auth

    def validate_auth_secret(self, value):
        self.auth = AuthRequest.objects.get_by_secret(value)
        if not self.auth:
            raise serializers.ValidationError('هیچ درخواست احراز هویتی برای درخواست شما یافت نشد. لطفا مجددا تلاش کنید')
        if self.auth.is_expired():
            raise serializers.ValidationError('درخواست احراز هویت منقضی شده است', code=status.HTTP_403_FORBIDDEN)
        self.user = self._get_user(self.auth)
        return value

    def _get_user(self, auth):
        try:
            return User.objects.get(username=auth.mobile)
        except User.DoesNotExist:
            raise serializers.ValidationError('برای این درخواست هیچ کاربری پیدا نشد', code=status.HTTP_400_BAD_REQUEST)

    def to_representation(self, obj):
        ret = super(GetTokenSerializer, self).to_representation(obj)
        ret.pop('auth_secret')
        return ret


class GetTokenSerializer(serializers.Serializer):
    """Get authentication tokens (access and refresh) which user can login with

    This action needs authentication, so user should first get secret_key in order to perform
    this action. After that, user will get a pair of access and refresh token which is valid 
    for a period of time (adjustable in :attr:`nakhll.settings.ACCESS_TOKEN_EXPIRE_MINUTES`
    and :attr:`nakhll.settings.REFRESH_TOKEN_EXPIRE_MINUTES`)

    Args:
        secret_key (str): one-time key that user gets from BeginAuth and CompleteAuth steps

    Returns:
        str: access token
        str: refresh token
    """
    auth_secret = serializers.CharField(max_length=32)

    def validate(self, data):
        self.auth = self._get_auth_request(data.get('auth_secret'))
        self._validate_auth_request()
        self.user = self._get_user(self.auth)

        refresh = self.get_token(self.user)
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)

        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, self.user)
        self.auth.close_request()
        return data

    def get_token(self, user):
        return RefreshToken.for_user(user)

    def _get_user(self, auth):
        try:
            return User.objects.get(username=auth.mobile)
        except User.DoesNotExist:
            raise serializers.ValidationError('برای این درخواست هیچ کاربری پیدا نشد', code=status.HTTP_400_BAD_REQUEST)

    def _get_auth_request(self, auth_secret):
        try:
            return AuthRequest.objects.get(auth_secret=auth_secret, request_status=AuthRequest.RequestStatuses.PENDING)
        except:
            raise serializers.ValidationError('درخواستی برای احراز هویت وجود ندارد', code=status.HTTP_400_BAD_REQUEST)

    def _validate_auth_request(self):
        if not self.auth:
            raise serializers.ValidationError('هیچ درخواست احراز هویتی برای درخواست شما یافت نشد. لطفا مجددا تلاش کنید')
        if self.auth.is_expired():
            raise serializers.ValidationError('درخواست احراز هویت منقضی شده است', code=status.HTTP_403_FORBIDDEN)
