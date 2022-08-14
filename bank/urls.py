from django.urls import path, include
from rest_framework import routers
from bank.views import AccountRequestViewSet, AccountViewSet, Withdraw
app_name = 'bank'

report_router = routers.DefaultRouter()
report_router.register('account', AccountViewSet, basename='account')
report_router.register(
    'account-request',
    AccountRequestViewSet,
    basename='account-request')


urlpatterns = [
    path(
        'withdraw/',
        Withdraw.as_view(),
        name='bank_withdraw_request'),
    path(
        'report/',
        include(report_router.urls),
        name='report'),
]
