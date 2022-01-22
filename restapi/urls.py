from os import name
from django.urls import path, re_path ,include
from django.conf.urls import url
from . import views, web_views, analyzeview

from rest_framework_jwt.views import obtain_jwt_token, verify_jwt_token

app_name = 'restapi'

urlpatterns = [


    path('v1/factor/uncompleted/', views.UncompeletedFactors.as_view(), name='get_uncompleted_factor'),
    path('v1/factor/completed/', views.CompeletedFactors.as_view(), name='get_completed_factor'),
    path('v1/factor/shop/<shop_slug>/uncompleted/', views.ShopUncompeletedFactors.as_view(), name='get_shop_uncompleted_factor'),
    path('v1/factor/shop/<shop_slug>/completed/', views.ShopCompeletedFactors.as_view(), name='get_shop_completed_factor'),
    path('v1/get-shop-products/<shop_slug>/', views.ShopProductList.as_view(), name='get_user_shop_products'),
    path('v1/get-user-info/', views.UserInfo.as_view(), name='get_user_info'),
    path('v1/get-all-state/', views.StateList.as_view(), name='get_all_state'),
    path('v1/get-big-cities/', views.BigCityList.as_view(), name='get_big_cities'),
    path('v1/get-cities/', views.CityList.as_view(), name='get_cities'),
    path('v1/get-factor-details/', views.FactorDetails.as_view(), name='get_factor_details'),
    path('v1/dashboard/<shop_slug>/', views.UserDashboardInfo.as_view(), name='user_dashboard_info'),
    path('v1/factor/change-status/confirmed/<factor_id>/', views.ChangeFactorToConfirmed.as_view(), name='change_factor_status_to_confirmed'),
    path('v1/factor/change-status/sent/<factor_id>/', views.ChangeFactorToSent.as_view(), name='change_factor_status_to_sent'),
]