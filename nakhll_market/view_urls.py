from django.urls import path, re_path 
from django.conf.urls import url  
from . import views
from nakhll_market import management_coupon_views, management_content_views
from django.contrib.sitemaps.views import sitemap
from .sitemaps import ShopSitemap , ProductSitemap ,StaticViewSitemap
from django.views.generic import TemplateView


app_name = 'nakhll_market'

urlpatterns = [
    # Urls to redirect old urls (users came from google search) to our new urls
    path('product/<shop_slug>/<product_slug>/', views.ProductsDetail, name='ProductsDetail'),
    path('product/<shop_slug>/<product_slug>/<str:status>/<str:msg>/', views.ProductsDetail, name='Re_ProductsDetail'),
    path('product/<product_slug>/', views.ProductsDetailWithSlug, name='ProductsDetail'),
]