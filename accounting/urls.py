from django.urls import path 
from accounting import views

app_name = 'accounting'

urlpatterns = [
    path('shop-managers-info/', views.ShopManagersInformation.as_view(), name='shop-managers-information'),
    path('shop-managers-info/v2/', views.ShopManagersInformationV2.as_view(), name='shop-managers-information-v2'),
    path('user-mobile/', views.UserMobile.as_view(), name='user-mobile'),
    path('product-stats/', views.ProductStats.as_view(), name='product-stats'),
    path('user-stats/' , views.UserStats.as_view() , name='user_stats'),
    path('shop-info/' , views.ShopInformation.as_view() , name='shop-information'),
    path('factor-stats/' , views.FactorStats.as_view() , name='factor-stats'),
    
]