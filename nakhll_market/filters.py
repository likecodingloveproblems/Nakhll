from django_filters import rest_framework as filters
from nakhll_market.models import BigCity, City, NewCategory, Product, State

class ProductFilter(filters.FilterSet):
    min_price = filters.NumberFilter(field_name="Price", lookup_expr='gte')
    # max_price = filters.NumberFilter(field_name="Price", lookup_expr='lte')
    ready = filters.BooleanFilter(method='filter_ready')
    search = filters.CharFilter(method='filter_search')
    available = filters.BooleanFilter(method='filter_available')
    category = filters.CharFilter(method='filter_category')
    new_category = filters.CharFilter(method='filter_new_category')
    city = filters.CharFilter(method='filter_city')
    big_city = filters.CharFilter(method='filter_big_city')
    state = filters.CharFilter(method='filter_state')
    discounted = filters.BooleanFilter(method='filter_discounted')
    shop = filters.CharFilter(method='filter_shop')
    in_campaign = filters.BooleanFilter(method='filter_in_campaign')

    class Meta:
        model = Product
        fields = ['search', 'min_price', 'ready', 'available', 'category', 'in_campaign',
        # fields = ['search', 'min_price', 'max_price', 'ready', 'available', 'category',
                    'new_category', 'city', 'discounted', 'is_advertisement', 'shop']

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
        return queryset.filter(FK_SubMarket__in=value.split(',')) if value else queryset

    def filter_new_category(self, queryset, name, value):
        category_ids = value.split(',')
        categories = NewCategory.objects.filter(id__in=category_ids)
        subcategories = NewCategory.objects.all_subcategories(categories)
        return queryset.filter(new_category__in=subcategories)

    def filter_state(self, queryset, name, value):
        states = State.objects.filter(id__in=value.split(',')).values_list('name', flat=True)
        return queryset.filter(FK_Shop__State__in=states)

    def filter_big_city(self, queryset, name, value):
        big_cities = BigCity.objects.filter(id__in=value.split(',')).values_list('name', flat=True)
        return queryset.filter(FK_Shop__BigCity__in=big_cities)

    def filter_city(self, queryset, name, value):
        cities = City.objects.filter(id__in=value.split(',')).values_list('name', flat=True)
        return queryset.filter(FK_Shop__City__in=cities)

    def filter_discounted(self, queryset, name, value):
        return queryset.filter(OldPrice__gt=0) if value else queryset

    def filter_shop(self, queryset, name, value):
        return queryset.filter(FK_Shop__Slug=value)

    def filter_in_campaign(self, queryset, name, value):
        return queryset.filter(FK_Shop__in_campaign=True)