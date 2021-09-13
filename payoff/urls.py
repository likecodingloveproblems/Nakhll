from django.urls import path
from .views import test_pec


app_name = 'payoff'
urlpatterns = [
    path('pec/token/', test_pec),
]
