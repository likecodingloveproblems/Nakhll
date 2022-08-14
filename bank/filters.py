from urllib import request
from django_filters import rest_framework as filters


class AccountRequestFilter(filters.FilterSet):
    status = filters.NumberFilter(field_name='status')
    request_type = filters.NumberFilter(field_name='request_type')
