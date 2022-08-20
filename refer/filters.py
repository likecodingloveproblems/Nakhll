from django_filters import rest_framework as filters


class ReferrerEventFilter(filters.FilterSet):
    status = filters.NumberFilter(field_name='status')
