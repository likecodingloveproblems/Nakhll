from django.contrib import admin

from django.contrib import admin
from .models import PostBlog, VendorStory, CategoryBlog, CommentPost
from django.contrib import admin
# Register your models here.

#post admin panel
@admin.register(VendorStory)
class VendorStoryAdmin(admin.ModelAdmin):
    list_display=('Title','Slug','DateCreate','Publish','FK_User',)
    list_filter=('Publish','DateCreate',)
    search_fields=('Title','Slug','Content','FK_Shop')
    ordering=['id','DateCreate',]
    readonly_fields = ["Point",]
#-------------------------------------------------
#PostBlog admin panel
@admin.register(PostBlog)
class PostBlogAdmin(admin.ModelAdmin):
    list_display=('Title','Slug','DateCreate','Publish','FK_User',)
    list_filter=('Publish','DateCreate',)
    search_fields=('Title','Slug','Content','FK_Shop')
    ordering=['id','DateCreate',]
    readonly_fields = ["Point",]
#-------------------------------------------------
#CategoryBlog admin panel
@admin.register(CategoryBlog)
class CategoryBlogAdmin(admin.ModelAdmin):
    list_display=('Title','Description','Slug','FK_SubCategory','Publish','DateCreate')
    list_filter=('Publish','DateCreate',)
    search_fields=('Title','Slug','Description')
    ordering=['id','DateCreate',]
    #-------------------------------------------------
#CommentPost admin panel
@admin.register(CommentPost)
class CommentPostAdmin(admin.ModelAdmin):
    list_display=('FK_UserAdder','Description','FK_Pater','Available','DateCreate')
    list_filter=('Available','DateCreate',)
    search_fields=('FK_UserAdder','FK_User','Description')
    ordering=['id','DateCreate',]