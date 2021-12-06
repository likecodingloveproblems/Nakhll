import random, datetime
from django.contrib.auth.models import User
from django.http.response import Http404
from rest_framework import serializers, viewsets, mixins, status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenViewBase
from rest_framework.decorators import action, permission_classes
from rest_framework.response import Response
from rest_framework.validators import ValidationError

from sms.services import Kavenegar
from .serializers import BeginAuthSerializer, CompleteAuthSerializer, PasswordSerializer, GetTokenSerializer
from .models import AuthRequest, generate_uuid_code


class BeginAuthViewSet(viewsets.GenericViewSet):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    @action(methods=['post'], detail=False)
    def login_register(self, request):
        serializer = BeginAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        mobile = serializer.validated_data.get('mobile')
        mobile_status = self._get_mobile_status(mobile)
        sms_code = None if mobile_status == AuthRequest.MobileStatuses.LOGIN_WITH_PASSWORD\
                    else self._generate_and_send_sms_code(mobile)
        serializer.save(request_type=AuthRequest.RequestTypes.LOGIN_REGISTER,
                        sms_code=sms_code, mobile_status=mobile_status)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(methods=['post'], detail=False)
    def forgot_password(self, request):
        serializer = BeginAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        mobile = serializer.validated_data.get('mobile')
        mobile_status = self._get_mobile_status(mobile)
        if mobile_status == AuthRequest.MobileStatuses.NOT_REGISTERED:
            raise ValidationError({'error': 'این شماره در سایت ثبت نشده است'},
                                  code=status.HTTP_400_BAD_REQUEST)
        sms_code = self._generate_and_send_sms_code(mobile)
        serializer.save(request_type=AuthRequest.RequestTypes.FORGOT_PASSWORD,
                        sms_code=sms_code, mobile_status=mobile_status)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
   
    def _generate_and_send_sms_code(self, mobile):
        code = str(random.randint(100000, 999999))
        Kavenegar.send_auth_code(mobile, code)     
        return code
    
    def _get_mobile_status(self, mobile):
        user = self._get_user(mobile)
        if not user:
            return AuthRequest.MobileStatuses.NOT_REGISTERED
        if user and user.password:
            return AuthRequest.MobileStatuses.LOGIN_WITH_PASSWORD
        else:
            return AuthRequest.MobileStatuses.LOGIN_WITH_CODE

    def _get_user(self, mobile):
        try:
            return User.objects.get(username=mobile)
        except User.DoesNotExist:
            return None

class CompeleteAuthViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = CompleteAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(auth_secret=generate_uuid_code())
        return Response(serializer.data, status=status.HTTP_200_OK)
   
class ProfileViewSet(viewsets.GenericViewSet):
    serializer_class = PasswordSerializer
    permission_classes = [permissions.AllowAny, ]

    @action(methods=['post'], detail=False, url_path='set_password')
    def set_password(self, request, *args, **kwargs):
        serializer = PasswordSerializer(data=request.data, partial=True,
                                request_type=AuthRequest.RequestTypes.FORGOT_PASSWORD)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        refresh = RefreshToken.for_user(serializer.user)
        data = dict()
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        return Response(data, status=status.HTTP_200_OK)

class GetAccessTokenView(TokenViewBase):
    serializer_class = GetTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = super().post(request, *args, **kwargs)
        serializer.data.pop('auth_secret')
        return serializer
