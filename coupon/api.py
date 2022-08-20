from django.contrib.auth.models import User
from rest_framework.viewsets import GenericViewSet
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action
from coupon.models import Coupon
from sms.services import Kavenegar
from .serializers import GiftCouponSerializer
from rest_framework.permissions import AllowAny


class CouponViewset(GenericViewSet):
    serializer_class = GiftCouponSerializer
    permission_classes = [AllowAny]

    def get_coupon(self, request):
        code = request.POST.get('code')
        try:
            return Coupon.objects.get(code=code)
        except Coupon.DoesNotExist:
            raise ValidationError({"code": "Invalid coupon code"})

    def get_user(self, request):
        if request.user:
            return request.user
        mobile = request.POST.get('mobile')
        try:
            return User.objects.get(username=mobile)
        except User.DoesNotExist:
            raise ValidationError({"mobile": "Invalid mobile number"})

    @action(methods=['post'], detail=False, description='ارسال کد تخفیف')
    def gift_user(self, request, *args, **kwargs):
        coupon = self.get_coupon(request)
        user = self.selfget_user(request)
        coupon.add_user(user)
        Kavenegar.send_gift_coupon(user, coupon)
