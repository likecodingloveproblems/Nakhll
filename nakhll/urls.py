from django.contrib import admin
from django.urls import path, include
from nakhll import settings
from django.conf.urls.static import static


view_urls = [
    path('logintowebsite/', admin.site.urls),
    path('accounting/', include('accounting.urls', namespace='accounting')),
    path('torob/', include('torob_api.urls', namespace='torob')),
    path('goto/', include('url_redirector.urls', namespace='url_redirector')),
    path('payoff/', include('payoff.urls', namespace='payoff')),
    path('', include('nakhll_market.view_urls', namespace='nakhll_market')),
    path('', include('django_prometheus.urls')),
]

api_urls = [
    path('', include('restapi.urls' , namespace='restapi')),
    path('', include('nakhll_market.api_urls', namespace='nakhll_market_api')),
    path('auth/', include('nakhll_auth.auth_urls')),
    path('profile/', include('nakhll_auth.profile_urls')),
    path('lists/', include('custom_list.urls')),
    path('shop/', include('shop.urls')),
    path('invoices/', include('invoice.urls')),
    path('cart/', include('cart.urls')),
    path('logistic/', include('logistic.urls')),
    
]

urlpatterns = [
    path('', include(view_urls)),
    path('api/v1/', include(api_urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)\
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)