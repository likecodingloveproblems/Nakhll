from django.urls import include, path 
from django.conf.urls import url
from accounting import views

app_name = 'accounting'

urlpatterns = [
    path('shop-managers-info/', views.ShopManagersInformation.as_view(), name='shop_managers_information'),
]