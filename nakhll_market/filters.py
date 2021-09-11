from django_filters import rest_framework as filters
from nakhll_market.models import Product

class ProductFilter(filters.FilterSet):
    min_price = filters.NumberFilter(field_name="Price", lookup_expr='gte')
    max_price = filters.NumberFilter(field_name="Price", lookup_expr='lte')
    ready = filters.BooleanFilter(method='filter_ready')
    search = filters.CharFilter(method='filter_search')
    available = filters.BooleanFilter(method='filter_available')
    category = filters.CharFilter(method='filter_category')
    city = filters.CharFilter(method='filter_city')
    big_city = filters.CharFilter(method='filter_big_city')
    state = filters.CharFilter(method='filter_state')
    discounted = filters.BooleanFilter(method='filter_discounted')

    class Meta:
        model = Product
        fields = ['search', 'min_price', 'max_price', 'ready', 'available', 'category', 'city', 'discounted']

    def filter_ready(self, queryset, name, value):
        READY_IN_STOCK = '1'
        filter_queryset = {'Status': READY_IN_STOCK, 'Inventory__gt': 0}
        return queryset.filter(**filter_queryset) if value else queryset
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(Title__icontains=value)

    def filter_available(self, queryset, name, value):
        AVAILABLE_IDS = ['1', '2', '3', ]
        return queryset.filter(Status__in=AVAILABLE_IDS, Inventory__gt=0)

    def filter_category(self, queryset, name, value):
        return queryset.filter(FK_SubMarket=value)

    def filter_state(self, queryset, name, value):
        return queryset.filter(FK_Shop__State__in=value.split(',')) if value else queryset

    def filter_big_city(self, queryset, name, value):
        return queryset.filter(FK_Shop__BigCity__in=value.split(',')) if value else queryset

    def filter_city(self, queryset, name, value):
        return queryset.filter(FK_Shop__City__in=value.split(',')) if value else queryset

    def filter_discounted(self, queryset, name, value):
        return queryset.filter(OldPrice__gt=0) if value else queryset
