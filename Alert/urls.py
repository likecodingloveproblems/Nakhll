from django.urls import path
from . import views


urlpatterns = [ path('profile/alert/<int:pk>/', views.ProfileAlert.as_view(), name='Alert'),



]