from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import serializers, status, validators
from .models import AuthRequest

class BeginAuthSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthRequest
        fields = ('mobile', 'auth_key', 'mobile_status', )
        read_only_fields = ('auth_key', 'mobile_status', )

class CompleteAuthSerializer(serializers.ModelSerializer):
    user_key = serializers.CharField(max_length=32)
    class Meta:
        model = AuthRequest
        fields = ('auth_secret', 'auth_key', 'user_key')
        write_only_fields = ('auth_secret', )

    def __init__(self, instance=None, data=..., **kwargs):
        self.auth_without_password = kwargs.pop('auth_without_password', False)
        super().__init__(instance=instance, data=data, **kwargs)

    def validate(self, data):
        auth_key = data.get('auth_key')
        user_key = data.get('user_key')
        self.instance = self._get_auth_request(auth_key)
        if not self.auth_is_valid(self.instance, user_key):
            raise serializers.ValidationError('اطلاعات برای احراز هویت معتبر نیست', code=status.HTTP_401_UNAUTHORIZED)
        return data

    def auth_is_valid(self, auth_request, user_key):
        if  auth_request.mobile_status == AuthRequest.MobileStatuses.LOGIN_WITH_PASSWORD\
                and not self.auth_without_password:
            return self.__validate_password(auth_request, user_key)
        return self.__validate_code(auth_request, user_key)
     
    def _get_auth_request(self, auth_key):
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


class PasswordSerializer(serializers.Serializer):
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

        
