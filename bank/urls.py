from django.urls import path, include
from rest_framework import routers
from bank.views import AccountViewSet, Withdraw
app_name = 'bank'

account_router = routers.DefaultRouter()
account_router.register('', AccountViewSet, basename='account')


urlpatterns = [
    path(
        'withdraw/',
        Withdraw.as_view(),
        name='bank_withdraw_request'),
    path('account/', include(account_router.urls), name='account'),
]
