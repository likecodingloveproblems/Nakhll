from django.urls import path, re_path 
from django.conf.urls import url
from . import views
from django.contrib.sitemaps.views import sitemap
from .sitemaps import PostBlogSitemap , VendorStorySitemap

sitemaps = {
    'PostsBlog': PostBlogSitemap,
    'VendorStories' : VendorStorySitemap
}

app_name = 'blog'

urlpatterns = [
    url(r'^sitemap\.xml/$', sitemap, {'sitemaps' : sitemaps } , name='sitemap'),
    path('index/', views.Blog, name='BlogSec'),
    path('post/<slug:Post_Slug>/', views.SinglePost, name='BlogPost'),
    path('vendorstory/<slug:Story_Slug>/', views.SingleVendorStory, name='vendorstory'),
    path('post-story/like/<int:obj_id>/<int:type>/', views.BlogLike, name='Post_Story_Like'),
    # Story ---------------------------------------------------------------------------------------
    # Set Story Point
    path('vendorstory/set/story_point', views.SetStoryPoint, name='SetStoryPoint'),
    # Add Story Comment
    path('vendorstory/<slug:Story_Slug>/addcomment', views.AddNewStoryComment, name='AddNewStoryComment'),
    # Add Story Replay Comment
    path('vendorstory/<slug:Story_Slug>/addcomment/<int:id>', views.AddNewStoryComment, name='AddReplayStoryComment'),
    # Show Message In Story
    path('vendorstory/<slug:Story_Slug>/<int:status>/<str:msg>/', views.SingleVendorStory, name='Re_SingleVendorStory'),
    # Show All Story
    path('vendorstory/show-all/shop-story/', views.show_all_blog_story, name='show_all_blog_story'),
    # Post -------------------------------------------------------------------------------------------
    # Set Point
    path('post/set/point', views.SetPoint, name='SetPoint'),
    # Add Post Comment
    path('post/<slug:Post_Slug>/addcomment', views.AddNewPostComment, name='AddNewPostComment'),
    # Add Post Replay Comment
    path('post/<slug:Post_Slug>/addcomment/<int:id>', views.AddNewPostComment, name='AddReplayPostComment'),
    # Show Message In Post
    path('post/<slug:Post_Slug>/<int:status>/<str:msg>/', views.SinglePost, name='Re_BlogPost'),
]