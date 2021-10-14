from django.urls import path
from url_redirector.views import Redirector

app_name = 'url_redirector'
urlpatterns = [
    path('<url_code>/', Redirector.as_view(), name='redirector'),
]