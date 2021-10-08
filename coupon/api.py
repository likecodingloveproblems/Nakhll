from django.utils.translation import ugettext as _
from rest_framework import permissions, viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from nakhll.authentications import CsrfExemptSessionAuthentication
from nakhll_market.models import ProductManager
from coupon.models import Coupon, CouponUsage
from coupon.serializers import CouponSerializer, CouponUsageSerializer
# from coupon.permissions import CouponOwner

