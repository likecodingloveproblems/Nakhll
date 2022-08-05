from django.urls import path
from bank.views import Withdraw
app_name = 'bank'


urlpatterns = [
    path(
        'factor/uncompleted/',
        Withdraw.as_view(),
        name='bank_withdraw_request'),
         ]
