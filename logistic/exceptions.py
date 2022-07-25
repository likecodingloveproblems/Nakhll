from django.utils.translation import gettext as _
from rest_framework.exceptions import APIException


class NoLogisticUnitAvailableException(APIException):
    """Raised when no logistic unit is available for a shop for an specific Address"""
    default_detail = _('هیچ واحد ارسالی برای محصولات برای آدرس شما یافت نشد. لطفا با آدرسی دیگر تلاش کنید.')
    status_code = 400
