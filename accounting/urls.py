from django.urls import path 
from accounting.views import (ShopLogisticUnitView, ShopManagersInformation, ShopManagersInformationV2, ShopInformation,
                              UserMobile, ProductStats, UserStats, InvoiceStats, SaleData, ItemData, ShopManagersinfoV3, 
                              Buyersinfo, Invoicesinfo)

app_name = 'accounting'

urlpatterns = [
    path('shop-managers-info/', ShopManagersInformation.as_view(), name='shop-managers-information'),
    path('shop-managers-info/v2/', ShopManagersInformationV2.as_view(), name='shop-managers-information-v2'),
    path('user-mobile/', UserMobile.as_view(), name='user-mobile'),
    path('product-stats/', ProductStats.as_view(), name='product-stats'),
    path('user-stats/' , UserStats.as_view() , name='user_stats'),
    path('shop-info/' , ShopInformation.as_view() , name='shop-information'),
    path('invoice-stats/' , InvoiceStats.as_view() , name='invoice-stats'),
    path('shop-logistic-stats/' , ShopLogisticUnitView.as_view() , name='shop-logistic-stats'),
    path('sale-data/', SaleData.as_view(), name='sale-data'),
    path('item-data/', ItemData.as_view(), name='item-data'),
    path('shop-managers-info/v3/', ShopManagersinfoV3.as_view(), name='shop-managers-information-v3'),
    path('buyers_info/', Buyersinfo.as_view(), name='buyers-information-v3'),
    path('invoices_info/', Invoicesinfo.as_view(), name='invoices-information-v3'),
]