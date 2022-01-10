from django.urls import path, re_path 
from django.conf.urls import url  
from . import views, profileviews, cartviews, alertviews, ajaxviwes
from nakhll_market import management_coupon_views, management_content_views
from django.contrib.sitemaps.views import sitemap
from .sitemaps import ShopSitemap , ProductSitemap ,StaticViewSitemap
from django.views.generic import TemplateView

sitemaps = {
    'static': StaticViewSitemap,
    'Shops': ShopSitemap,
    'Products' : ProductSitemap,
    
}

app_name = 'nakhll_market'
urlpatterns = [
    url(r'^sitemap\.xml/$', sitemap, {'sitemaps' : sitemaps } , name='sitemap'),
    url(r'^robots\.txt/$', TemplateView.as_view(template_name="robots.txt", content_type='text/plain')),

    # Product Path
    path('product/<shop_slug>/<product_slug>/', views.ProductsDetail, name='ProductsDetail'),
    path('product/<shop_slug>/<product_slug>/<str:status>/<str:msg>/', views.ProductsDetail, name='Re_ProductsDetail'),
    path('product/<product_slug>/', views.ProductsDetailWithSlug, name='ProductsDetail'),
]