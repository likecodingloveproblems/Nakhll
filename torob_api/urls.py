from django.urls import path
from torob_api.api import TorobAllProducts

app_name = 'torob'
urlpatterns = [
    path('products/', TorobAllProducts.as_view()), 
]
