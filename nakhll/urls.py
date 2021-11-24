"""nakhll URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from django.urls.conf import re_path
from nakhll import site_updating
from nakhll import settings
from django.conf.urls.static import static


urlpatterns = [
    # re_path(r'.*', site_updating.update, name='update'), # only for update conditions
    url(r'^oauth/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    path('logintowebsite/', admin.site.urls),
    path('accounts/', include('my_auth.urls', namespace='my_auth')),
    path('', include('nakhll_market.urls', namespace='nakhll_market')),
    url(r'^tinymce/', include('tinymce.urls')),
    url(r'^cart/', include('Payment.urls' , namespace='Payment')),
    url(r'^cart2/', include('cart.urls' , namespace='cart_new')),
    url(r'^logistic/', include('logistic.urls' , namespace='logistic')),
    url(r'^app/api/', include('restapi.urls' , namespace='restapi')),
    path('accounting/', include('accounting.urls', namespace='accounting')),
    path('accounting_new/', include('accounting_new.urls', namespace='accounting_new')),
    path('torob/', include('torob_api.urls', namespace='torob')),
    path('goto/', include('url_redirector.urls', namespace='url_redirector')),
    # api version 1
    url(r'^api/v1/', include('nakhll_market.api_urls', namespace='nakhll_market_api')),
    url(r'^api/v1/', include('custom_list.urls', namespace='custom_list')),
    url(r'^api/v1/', include('shop.urls', namespace='shop')),
    path('api/v1/', include('nakhll_auth.urls', namespace='auth_api')),
    # prometheus
    url('', include('django_prometheus.urls')),
    path('payoff/', include('payoff.urls', namespace='payoff')),
]

# if settings.DEBUG:
    # urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)\
    # + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)