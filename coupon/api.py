from rest_framework.viewsets import GenericViewSet
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action
from coupon.models import Coupon
from sms.services import Kavenegar


class CouponViewset(GenericViewSet):

    def get_coupon(self, request):
        code = request.POST.get('code')
        try:
            return Coupon.objects.get(code=code)
        except Coupon.DoesNotExist:
            raise ValidationError()

    def get_user(self, request):
        if request.user:
            return request.user
        mobile = request.POST.get('mobile')
        try:
            return User.objects.get(username=mobile)
        except User.DoesNotExist:
            raise ValidationError()

    @action(methods=['post'], detail=False, description='ارسال کد تخفیف')
    def gift_user(self, request, *args, **kwargs):
        coupon = self.get_coupon(request)
        user = self.get_user(request)
        coupon.add_user(user)
        kavenegar.send_gift_coupon(user, coupon)
