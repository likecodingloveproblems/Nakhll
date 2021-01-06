from django.urls import path
from my_auth import views

app_name = 'auth'

urlpatterns = [
    # login process
    path('login/', views.Login.as_view(), name='login'),
    # logout process
    path('logout/', views.logout_, name='logout'),
    # registration process
    path('register-mobile/', views.RegisterMobile.as_view(), name='register-mobile'),
    path('register-code/', views.RegisterCode.as_view(), name='register-code'),
    path('register-data/', views.RegisterData.as_view(), name='register-data'),
    # forget password process
    path('forget-password-mobile/', views.ForgetPasswordMobile.as_view(), name='forget-password-mobile'),
    path('forget-password-code/', views.ForgetPasswordCode.as_view(), name='forget-password-code'),
    path('forget-password-data/', views.ForgetPasswordData.as_view(), name='forget-password-data'),
]