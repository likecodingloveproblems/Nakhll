from django.urls import path
from .views import test_pec, test_pec_callback


app_name = 'payoff'
urlpatterns = [
    path('pec/token/', test_pec),
    path('pec/token/verify/', test_pec_callback),
]
