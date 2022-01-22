from django.shortcuts import get_object_or_404 
from django.http import HttpResponse, JsonResponse
from django.utils.datastructures import MultiValueDictKeyError
from django.views.decorators.http import require_POST 
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib.auth.models import User
import json

from nakhll_market.models import (
    Profile, 
    Product, 
    Shop, 
    ProductBanner, 
    Alert, 
    State,
    BigCity,
    City
    )

from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.generics import (
    ListAPIView, 
    RetrieveAPIView,
    DestroyAPIView,
    UpdateAPIView,
    CreateAPIView,
)
from .serializers import *
from django.core import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from oauth2_provider.views.generic import ProtectedResourceView
from django.http import HttpResponse
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_403_FORBIDDEN,
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_202_ACCEPTED,
    HTTP_500_INTERNAL_SERVER_ERROR
)
from rest_framework.response import Response






