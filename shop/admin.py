from django.contrib import admin
from django.utils.timezone import localtime
import jdatetime
from .models import ShopFeature
from .models import ShopFeatureInvoice
from .models import ShopLanding


# Register your models here.
@admin.register(ShopLanding)
class ShopLandingAdmin(admin.ModelAdmin):
    list_display = ['id', 'shop', 'name', 'status', 'shop_is_landing', 'created_at', 'updated_at']
    list_display_links = ['id', 'shop', 'name']
    search_fields = ['name', 'shop__Title']
    autocomplete_fields = ['shop', ]
    list_filter = ['status', 'created_at', 'updated_at']
    ordering = ['-updated_at', '-created_at', '-id']

    def shop_is_landing(self, obj):
        return obj.shop.is_landing
    shop_is_landing.boolean = True
    shop_is_landing.short_description = 'صفحه فروشگاهی'

    def get_queryset(self, request):
        qs = super().get_queryset(request).filter(shop__Available=True, shop__Publish=True)
        return qs

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(ShopFeature)
class ShopFeatureAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'desc', 'unit', 'price_per_unit_without_discount', 'price_per_unit_with_discount',
                    'demo_days', 'is_publish',)
    list_filter = ('unit', 'is_publish',)
    readonly_fields = ('id', 'desc',)
    ordering = ['-id', ]
    search_fields = ('id', 'name', 'desceription')
    fields = ('id', 'name', 'description', 'unit', 'price_per_unit_without_discount', 'price_per_unit_with_discount',
              'demo_days', 'is_publish',)

    def desc(self, obj):
        return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description

    desc.short_description = 'توضیحات'


@admin.register(ShopFeatureInvoice)
class ShopFeatureInvoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'feature', 'shop', 'status', 'bought_price_per_unit', 'bought_unit',
                    'unit_count', 'shop_owner', 'payment_unique_id', 'is_demo',
                    'start_datetime_jalali', 'expire_datetime_jalali', 'payment_datetime_jalali')
    list_filter = ('status', 'is_demo', 'payment_datetime', 'start_datetime', 'expire_datetime', 'feature')
    readonly_fields = ('id', 'shop_owner', 'start_datetime_jalali', 'expire_datetime_jalali', 'payment_datetime_jalali')
    ordering = ['-id', ]
    search_fields = ('id', 'shop__Title', 'payment_unique_id', )
    fields = ('id', 'feature', 'shop', 'status', 'bought_price_per_unit', 'bought_unit', 'unit_count', 'shop_owner',
              'start_datetime_jalali', 'expire_datetime_jalali', 'payment_datetime_jalali', 'payment_unique_id',
              'is_demo','expire_datetime',)

    def shop_owner(self, obj):
        return obj.shop.FK_ShopManager.get_full_name()

    shop_owner.short_description = 'مدیر فروشگاه'

    def start_datetime_jalali(self, obj):
        datetime = localtime(obj.start_datetime)
        datetime = jdatetime.datetime.fromgregorian(datetime=datetime)
        return datetime.strftime('%Y/%m/%d %H:%M')

    start_datetime_jalali.short_description = 'زمان شروع'

    def expire_datetime_jalali(self, obj):
        datetime = localtime(obj.expire_datetime)
        datetime = jdatetime.datetime.fromgregorian(datetime=datetime)
        return datetime.strftime('%Y/%m/%d %H:%M')

    expire_datetime_jalali.short_description = 'زمان پایان'

    def payment_datetime_jalali(self, obj):
        datetime = localtime(obj.payment_datetime)
        datetime = jdatetime.datetime.fromgregorian(datetime=datetime)
        return datetime.strftime('%Y/%m/%d %H:%M')

    payment_datetime_jalali.short_description = 'زمان پرداخت'
