from django.contrib.sitemaps import Sitemap
from django.contrib import sitemaps
from .models import Shop , Product
from django.urls import reverse

class StaticViewSitemap(sitemaps.Sitemap):
    priority = 1
    changefreq = 'daily'

    def items(self):
        return ['Profile:index','Profile:Markets']

    def location(self, item):
        return reverse(item)


class ProductSitemap(Sitemap):    
    changefreq = "monthly"
    priority = 0.5
 
    def items(self):
        return Product.objects.filter(Publish = True, Available = True)
 
    def lastmod(self, obj):
        return obj.DateUpdate


class ShopSitemap(Sitemap):    
    changefreq = "monthly"
    priority = 0.8
 
    def items(self):
        return Shop.objects.filter(Publish = True, Available = True)
 
    def lastmod(self, obj):
        return obj.DateUpdate
