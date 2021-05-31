from django.urls import path 
from accounting import views

app_name = 'accounting'

urlpatterns = [
    path('shop-managers-info/', views.ShopManagersInformation.as_view(), name='shop_managers_information'),
    path('shop-managers-info/v2/', views.ShopManagersInformationV2.as_view(), name='shop_managers_information-v2'),
    path('user-mobile/', views.UserMobile.as_view(), name='user-mobile'),
    path('product-stats/', views.ProductStats.as_view(), name='product-stats'),
    path('user_state/' , views.UserState.as_view() , name='user_state'),
    path('shop-info/' , views.ShopInformation.as_view() , name='shop_information')
]