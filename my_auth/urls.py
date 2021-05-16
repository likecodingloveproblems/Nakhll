from django.urls import path
from django.urls.conf import re_path
from my_auth import views

app_name = 'auth'

urlpatterns = [
    # login process
    path('login/', views.Login.as_view(), name='login'),
    # registration process
    path('register-mobile/', views.RegisterMobile.as_view(), name='register-mobile'),
    path('register-code/', views.RegisterCode.as_view(), name='register-code'),
    path('register-data/', views.RegisterData.as_view(), name='register-data'),
    # forget password process
    path('forget-password-mobile/', views.ForgetPasswordMobile.as_view(), name='forget-password-mobile'),
    path('forget-password-code/', views.ForgetPasswordCode.as_view(), name='forget-password-code'),
    path('forget-password-data/', views.ForgetPasswordData.as_view(), name='forget-password-data'),
    # logout process
    re_path(r'^logout/$', views.logout, name='logout'),
    # authenticate user
    re_path(r'^get-phone/$', views.GetPhone.as_view(), name='get-phone'),
    re_path(r'^register/$', views.Register.as_view(), name='register'),
    re_path(r'^login-password/$', views.LoginPassword.as_view(), name='login-password'),
    re_path(r'^login-code/$', views.LoginCode.as_view(), name='login-code'),
    re_path(r'^get-code/$', views.GetCode.as_view(), name='get-code'),
]