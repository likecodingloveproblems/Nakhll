from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from nakhll import settings
from . import setup as nakhll_setup
# from reports.admin import reports_admin_site
nakhll_setup.seutp()


view_urls = [
    path('logintowebsite/', admin.site.urls),
    # path('reportspanel/', reports_admin_site.urls),
    path('accounting/', include('accounting.urls', namespace='accounting')),
    path('torob/', include('torob_api.urls', namespace='torob')),
    path('goto/', include('url_redirector.urls', namespace='url_redirector')),
    path('sms/', include('sms.urls')),
    path('payoff/', include('payoff.urls', namespace='payoff')),
    path('', include('nakhll_market.view_urls', namespace='nakhll_market')),
    path('', include('django_prometheus.urls')),
]

api_urls = [
    path('auth/', include('nakhll_auth.auth_urls')),
    path('profile/', include('nakhll_auth.profile_urls')),
    path('lists/', include('custom_list.urls')),
    path('shop/', include('shop.urls')),
    path('invoices/', include('invoice.urls')),
    path('cart/', include('cart.urls')),
    path('logistic/', include('logistic.urls')),
    path('', include('restapi.urls', namespace='restapi')),
    path('', include('nakhll_market.api_urls', namespace='nakhll_market_api')),
]

urlpatterns = [
    path('', include(view_urls)),
    path('api/v1/', include(api_urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
