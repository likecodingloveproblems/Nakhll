from django.urls import path
from refer import views

app_name = 'refer'
urlpatterns = [
    path(
        'anonymous-visit/',
        views.ReferrerAnonymousUniqueVisit.as_view(),
        name='anonymous-visit'),
]
