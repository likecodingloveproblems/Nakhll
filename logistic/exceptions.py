from django.utils.translation import gettext as _
from rest_framework.exceptions import APIException

class NoLogisticUnitAvailableException(APIException):
    default_detail = _('هیچ واحد ارسالی برای محصولات برای آدرس شما یافت نشد. لطفا با آدرسی دیگر تلاش کنید.')
    status_code = 400
    