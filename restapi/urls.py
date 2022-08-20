from django.urls import path
from . import views

app_name = 'restapi'

urlpatterns = [
    path(
        'factor/uncompleted/',
        views.UncompeletedFactors.as_view(),
        name='get_uncompleted_factor'),
    path(
        'factor/completed/',
        views.CompeletedFactors.as_view(),
        name='get_completed_factor'),
    path(
        'factor/shop/<shop_slug>/uncompleted/',
        views.ShopUncompeletedFactors.as_view(),
        name='get_shop_uncompleted_factor'),
    path(
        'factor/shop/<shop_slug>/completed/',
        views.ShopCompeletedFactors.as_view(),
        name='get_shop_completed_factor'),
    path(
        'get-shop-products/<shop_slug>/',
        views.ShopProductList.as_view(),
        name='get_user_shop_products'),
    path(
        'get-user-info/',
        views.UserInfo.as_view(),
        name='get_user_info'),
    path(
        'get-all-state/',
        views.StateList.as_view(),
        name='get_all_state'),
    path(
        'get-big-cities/',
        views.BigCityList.as_view(),
        name='get_big_cities'),
    path(
        'get-cities/',
        views.CityList.as_view(),
        name='get_cities'),
    path(
        'get-factor-details/',
        views.FactorDetails.as_view(),
        name='get_factor_details'),
    path(
        'dashboard/<shop_slug>/',
        views.UserDashboardInfo.as_view(),
        name='user_dashboard_info'),
    path(
        'factor/change-status/confirmed/<factor_id>/',
        views.ChangeFactorToConfirmed.as_view(),
        name='change_factor_status_to_confirmed'),
    path(
        'factor/change-status/sent/<factor_id>/',
        views.ChangeFactorToSent.as_view(),
        name='change_factor_status_to_sent'),
]
