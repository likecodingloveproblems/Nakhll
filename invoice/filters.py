from django.db.models import Q
from django_filters import rest_framework as filters
from .models import Invoice


class InvoiceFilter(filters.FilterSet):
    min_price = filters.NumberFilter(field_name="price", lookup_expr='gte')
    max_price = filters.NumberFilter(field_name="price", lookup_expr='lte')
    min_weight = filters.NumberFilter(field_name="weight", lookup_expr='gte')
    max_weight = filters.NumberFilter(field_name="weight", lookup_expr='lte')
    payed_before = filters.DateFilter(
        field_name="payment_datetime",
        lookup_expr='lte')
    payed_after = filters.DateFilter(
        field_name="payment_datetime",
        lookup_expr='gte')
    created_before = filters.DateFilter(
        field_name="created_datetime", lookup_expr='lte')
    created_after = filters.DateFilter(
        field_name="created_datetime", lookup_expr='gte')
    is_completed = filters.BooleanFilter(method='filter_completed')
    q = filters.CharFilter(method='filter_search')

    class Meta:
        # pylint: disable=missing-docstring
        model = Invoice
        fields = [
            'id',
            'user',
            'status',
            'payment_unique_id',
        ]

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(
                Q(id=value) |
                Q(items__product__Title__icontains=value) |
                Q(items__product__FK_Shop__Title__icontains=value) |
                Q(address_json__icontains=value) |
                Q(user__first_name__icontains=value) |
                Q(user__last_name__icontains=value) |
                Q(user__username__icontains=value) |
                Q(payment_unique_id__icontains=value)
            )
        )

    def filter_completed(self, queryset, name, is_completed):
        if is_completed is True:
            return queryset.filter(status=Invoice.Statuses.COMPLETED)
        if is_completed is False:
            return queryset.exclude(status__in=[Invoice.Statuses.COMPLETED,
                                                Invoice.Statuses.AWAIT_PAYMENT,
                                                Invoice.Statuses.CANCELED])
        return queryset

    def filter_address(self, queryset, name, value):
        return queryset.filter(address_json__icontains=value)

    def filter_min_price(self, queryset, name, value):
        return queryset.filter(Price__gte=value)

    def filter_ready(self, queryset, name, value):
        READY_IN_STOCK = '1'
        filter_queryset = {'Status': READY_IN_STOCK, 'Inventory__gt': 0}
        return queryset.filter(**filter_queryset) if value else queryset

    def filter_search(self, queryset, name, value):
        return queryset.filter(Title__icontains=value)

    def filter_available(self, queryset, name, value):
        if value:
            AVAILABLE_IDS = ['1', '2', '3', ]
            return queryset.filter(Status__in=AVAILABLE_IDS, Inventory__gt=0)
        return queryset

    def filter_category(self, queryset, name, value):
        return queryset.filter(
            FK_SubMarket__in=value.split(',')) if value else queryset
