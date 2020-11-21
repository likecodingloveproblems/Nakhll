from django.contrib.sitemaps import Sitemap
from .models import PostBlog , VendorStory


class PostBlogSitemap(Sitemap):    
    changefreq = "monthly"
    priority = 0.9
 
    def items(self):
        return PostBlog.objects.filter(Publish = True)
 
    def lastmod(self, obj):
        return obj.DateUpdate


class VendorStorySitemap(Sitemap):    
    changefreq = "monthly"
    priority = 0.9
 
    def items(self):
        return VendorStory.objects.filter(Publish = True)
 
    def lastmod(self, obj):
        return obj.DateUpdate
