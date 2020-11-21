from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.http import HttpResponseRedirect

from django.views.decorators.http import require_POST 
from django.contrib.auth.decorators import login_required
from nakhll_market.models import Shop, Product, Profile, Option_Meta ,Newsletters
from django.utils import timezone
from django.http import JsonResponse
from Payment.models import Wallet, Factor,FactorPost
from .models import CategoryBlog, PostBlog, VendorStory, CommentPost, StoryPost
from nakhll_market.models import AttrPrice, Alert, Profile, PageViews, User_View, Alert
from django.contrib.auth.models import User
from django.views import generic
from ipware import get_client_ip
from datetime import datetime, date
import jdatetime
import threading



# Get User IP
def visitor_ip_address(request):

    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class GetUserInfo(threading.Thread):
    def run(self, request):
        # Get This User Profile
        this_user_profile = get_object_or_404(Profile, FK_User = request.user)
        this_user_inverntory = get_object_or_404(Wallet, FK_User = request.user).Inverntory
        # Set Result
        result = {
            "user_profiel": this_user_profile,
            "user_inverntory": this_user_inverntory,
        }
        return result


# -------------------------------------------------------------------------------------------------------------------------------------

# Check View - Get View
def CheckView(request, obj_slug, obj_type):
    # Get Page View
    if PageViews.objects.filter(Object_Slug = obj_slug, Object_Type = obj_type).exists():
        this_page_view = PageViews.objects.get(Object_Slug = obj_slug, Object_Type = obj_type)
        # Get User View
        if this_page_view.FK_Viewer.all().count() != 0:
            if this_page_view.FK_Viewer.filter(User_Ip = visitor_ip_address(request)).count() == 1:
                # Get View 
                this_view = this_page_view.FK_Viewer.get(User_Ip = visitor_ip_address(request))
                # Check Date
                date_format = "%Y-%m-%d"
                a = datetime.strptime(str(date.today()), date_format)
                b = datetime.strptime(str(this_view.DateTime.date()), date_format)
                delta = a - b
                # If Delta > 24H
                if delta.days >= 1:
                    this_page_view.View_Count += 1
                    this_view.DateTime = datetime.now()
                    this_view.save()
                    this_page_view.save()
                view_count = this_page_view.View_Count

            else:

                this_view = User_View.objects.create(User_Ip = visitor_ip_address(request))
                this_page_view.FK_Viewer.add(this_view)
                this_page_view.save()
                if this_page_view.View_Count < this_page_view.FK_Viewer.all().count():
                    this_page_view.View_Count = this_page_view.FK_Viewer.all().count()
                    this_page_view.save()
                else:
                    this_page_view.View_Count += 1
                    this_page_view.save()
                view_count = this_page_view.View_Count
            
        else:

            this_view = User_View.objects.create(User_Ip = visitor_ip_address(request))
            this_page_view.FK_Viewer.add(this_view)
            this_page_view.save()
            if this_page_view.View_Count < this_page_view.FK_Viewer.all().count():
                this_page_view.View_Count = this_page_view.FK_Viewer.all().count()
                this_page_view.save()
            else:
                this_page_view.View_Count += 1
                this_page_view.save()
            view_count = this_page_view.View_Count

    else:

        this_page_view = PageViews.objects.create(Object_Slug = obj_slug, Object_Type = obj_type)
        this_view = User_View.objects.create(User_Ip = visitor_ip_address(request))
        this_page_view.FK_Viewer.add(this_view)
        this_page_view.save()
        if this_page_view.View_Count < this_page_view.FK_Viewer.all().count():
            this_page_view.View_Count = this_page_view.FK_Viewer.all().count()
            this_page_view.save()
        else:
            this_page_view.View_Count += 1
            this_page_view.save()
        view_count = this_page_view.View_Count

    return view_count



# All Blog Post
def Blog(request):
    if request.user.is_authenticated:
        This_User_Info = GetUserInfo().run(request)
        this_profile = This_User_Info["user_profiel"]
        this_inverntory = This_User_Info["user_inverntory"]
    else:
        this_profile = None
        this_inverntory = None
    # Get Menu Item
    options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
    # Get Nav Bar Menu Item
    navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
    # --------------------------------------------------------------------
    blog_list = []
    class Blog:
        def __init__(self, item, writer):
            self.Blog = item
            self.Writer = writer
    # Built New Object
    for item in PostBlog.objects.filter(Publish = True).order_by('-DateCreate'):
        new = Blog(item, Profile.objects.get(FK_User = item.FK_User))
        blog_list.append(new)
    # Get All Blog Category
    catblog = CategoryBlog.objects.filter(Publish = True)

    context = {
        'This_User_Profile':this_profile,
        'This_User_Inverntory': this_inverntory,
        'Options': options,
        'MenuList':navbar,
        'Postblog':blog_list,
        'Catblog':catblog,
    }

    return render(request, 'blog/pages/blog.html', context)




# Blog Like
def BlogLike(request, obj_id, type):

    if request.user.is_authenticated :

        if type == 1: # Like Blog Post

            # Get This Commment Post
            this_post = CommentPost.objects.get(id = obj_id)
            # Chech User
            check_user = False
            for item in this_post.FK_Like.all():
                if item == request.user:
                    check_user = True
                    break
            
            if check_user:

                this_post.FK_Like.remove(request.user)
                return redirect("blog:BlogPost", Post_Slug = this_post.FK_Post.Slug)
                
            else:

                this_post.FK_Like.add(request.user)
                return redirect("blog:BlogPost", Post_Slug = this_post.FK_Post.Slug)

        elif type == 0: # Like Blog Story

            # Get This Commment Story
            this_story = StoryPost.objects.get(id = obj_id)
            # Chech User
            check_user = False
            for item in this_story.FK_Like.all():
                if item == request.user:
                    check_user = True
                    break
            
            if check_user:
                
                this_story.FK_Like.remove(request.user)
                return redirect("blog:vendorstory", Story_Slug = this_story.FK_VendorStory.Slug)
                
            else:

                this_story.FK_Like.add(request.user)
                return redirect("blog:vendorstory", Story_Slug = this_story.FK_VendorStory.Slug)

    else:

        return redirect("nakhll_market:AccountLogin")




# Blog Post ---------------------------------------------------------------------------------------------------------------------------



# Single Post
def SinglePost(request, Post_Slug, status = None, msg = None):
    if request.user.is_authenticated:
        This_User_Info = GetUserInfo().run(request)
        this_profile = This_User_Info["user_profiel"]
        this_inverntory = This_User_Info["user_inverntory"]
    else:
        this_profile = None
        this_inverntory = None
    # Get Menu Item
    options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
    # Get Nav Bar Menu Item
    navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
    # ---------------------------------------------------------------------
    # Get Page
    post = PostBlog.objects.get(Slug = Post_Slug, Publish = True)
    # Get View
    view_count = CheckView(request, post.Slug, '2')
    # Get Date
    month = None
    if post.DateCreate.month == 1:
        month = 'فروردین'
    elif post.DateCreate.month == 2:
        month = 'اردیبهشت'
    elif post.DateCreate.month == 3:
        month = 'خرداد'
    elif post.DateCreate.month == 4:
        month = 'تیر'
    elif post.DateCreate.month == 5:
        month = 'مرداد'
    elif post.DateCreate.month == 6:
        month = 'شهریور'
    elif post.DateCreate.month == 7:
        month = 'مهر'
    elif post.DateCreate.month == 8:
        month = 'آبان'
    elif post.DateCreate.month == 9:
        month = 'آذر'
    elif post.DateCreate.month == 10:
        month = 'دی'
    elif post.DateCreate.month == 11:
        month = 'بهمن'
    elif post.DateCreate.month == 12:
        month = 'اسفند'
    post_date = "%s %s %s" % (post.DateCreate.day, month, post.DateCreate.year)
    # Get Writer Profile
    writer_bio = Profile.objects.get(FK_User = post.FK_User).Bio
    # Get All Tag
    tags = post.FK_Tag.all()
    # Get All Last Post
    last_post = PostBlog.objects.filter(Publish = True).order_by('-DateCreate')[:7]
    # Get All Categories
    categories = CategoryBlog.objects.all().order_by('-DateCreate')[:7]
    # Get All Comment
    post_comments = CommentPost.objects.filter(FK_Post = post, Available = True)
    # Set Point Count
    point_count = post.FK_Point.all().count()
    # Show Message
    if status != None:
        ShowAlart = bool(status)
        AlartMessage = msg
    else:
        ShowAlart = False
        AlartMessage = ''

    context = {
        'This_User_Profile':this_profile,
        'This_User_Inverntory': this_inverntory,
        'Options': options,
        'MenuList':navbar,
        'Post':post,
        'PostDate':post_date,
        'Writer':writer_bio,
        'Tags':tags,
        'LastPost':last_post,
        'Categories':categories,
        'Comments':post_comments,
        'PointCount':point_count,
        'ShowAlart':ShowAlart,
        'AlartMessage':AlartMessage,
        'View_Count':view_count,
    }

    return render(request, 'blog/pages/singlepost.html', context)




# Set Post Point
def SetPoint(request):
    response_data = {}

    if request.user.is_authenticated :
        
        if request.POST.get('action') == 'post':
            try:
                post_blog = request.POST.get("rating")
                Post_Slug = request.POST.get("Slug")
            except:
                response_data['error'] = 'خطای دریافت اطلاعات'
                response_data['status'] = False
                return JsonResponse(response_data)
            # Get Post
            this_post = PostBlog.objects.get(Slug = Post_Slug)
            # Change Point
            if post_blog != '':
                if this_post.FK_Point.filter(id = request.user.id).count() == 0:

                    if this_post.Point == 0:

                        this_post.Point += float(post_blog)
                        this_post.FK_Point.add(request.user)
                        this_post.save()
                    else:

                        this = (float(this_post.Point) + float(post_blog)) / 2
                        this_post.Point = this
                        this_post.FK_Point.add(request.user)
                        this_post.save()
                    
                    response_data['msg'] = 'ok'
                    response_data['status'] = True
                    return JsonResponse(response_data)

                else:

                    response_data['error'] = 'شما قبلا به این پست امتیاز داده اید.'
                    response_data['status'] = False
                    return JsonResponse(response_data)

            else:
                
                response_data['error'] = 'خطای دریافت اطلاعات'
                response_data['status'] = False
                return JsonResponse(response_data)
        else:

            response_data['error'] = 'خطای دریافت اطلاعات'
            response_data['status'] = False
            return JsonResponse(response_data)

    else:
        response_data['error'] = 'لطفا به حساب کاربری خود وارد شوید'
        response_data['status'] = False
        return JsonResponse(response_data)



# Add New Post Comment
def AddNewPostComment(request, Post_Slug, id = None):

    if request.user.is_authenticated :

        if request.method == 'POST':

            try:
                des = request.POST["comment_des"]
            except:
                des = False
            
            # Get Post
            this_post = PostBlog.objects.get(Slug = Post_Slug)
            # Add New Comment
            if des != '':
                
                if id == None:

                    NewComment = CommentPost.objects.create(FK_UserAdder = request.user, FK_Post = this_post, Description = des)
                    Alert.objects.create(Part = '28', FK_User = request.user, Slug = NewComment.id)

                    return redirect("blog:Re_BlogPost",
                    Post_Slug = this_post.Slug,
                    status = 1,
                    msg =  'نظر شما ثبت شد، و پس از تایید کارشناسان نمایش داده خواهد شد.')

                else:

                    # Get Fathers Comment
                    father = CommentPost.objects.get(id = id)
                    NewComment = CommentPost.objects.create(FK_UserAdder = request.user, FK_Post = this_post, Description = des, FK_Pater = father)
                    Alert.objects.create(Part = '28', FK_User = request.user, Slug = NewComment.id)

                    return redirect("blog:Re_BlogPost",
                    Post_Slug = this_post.Slug,
                    status = 1,
                    msg =  'نظر شما ثبت شد، و پس از تایید کارشناسان نمایش داده خواهد شد.')

            else:

                return redirect("blog:Re_BlogPost",
                Post_Slug = this_post.Slug,
                status = 1,
                msg =  'متن نظر نمی تواند خالی باشد!')
        else:

            return redirect("blog:BlogPost", Post_Slug = this_post.Slug)

    else:

        return redirect("nakhll_market:AccountLogin")


# Blog Story --------------------------------------------------------------------------------------------------------------------------


# Single Post
def SingleVendorStory(request, Story_Slug, status = None, msg = None):
    if request.user.is_authenticated:
        This_User_Info = GetUserInfo().run(request)
        this_profile = This_User_Info["user_profiel"]
        this_inverntory = This_User_Info["user_inverntory"]
    else:
        this_profile = None
        this_inverntory = None
    # Get Menu Item
    options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
    # Get Nav Bar Menu Item
    navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
    # ---------------------------------------------------------------------
    # Get Story
    vendorstory = VendorStory.objects.get(Slug = Story_Slug, Publish = True)
    # Get View
    view_count = CheckView(request, vendorstory.Slug, '3')
    # Get Date
    month = None
    if vendorstory.DateCreate.month == 1:
        month = 'فروردین'
    elif vendorstory.DateCreate.month == 2:
        month = 'اردیبهشت'
    elif vendorstory.DateCreate.month == 3:
        month = 'خرداد'
    elif vendorstory.DateCreate.month == 4:
        month = 'تیر'
    elif vendorstory.DateCreate.month == 5:
        month = 'مرداد'
    elif vendorstory.DateCreate.month == 6:
        month = 'شهریور'
    elif vendorstory.DateCreate.month == 7:
        month = 'مهر'
    elif vendorstory.DateCreate.month == 8:
        month = 'آبان'
    elif vendorstory.DateCreate.month == 9:
        month = 'آذر'
    elif vendorstory.DateCreate.month == 10:
        month = 'دی'
    elif vendorstory.DateCreate.month == 11:
        month = 'بهمن'
    elif vendorstory.DateCreate.month == 12:
        month = 'اسفند'
    story_date = "%s %s %s" % (vendorstory.DateCreate.day, month, vendorstory.DateCreate.year)
    # Get Writer Profile
    writer_bio = Profile.objects.get(FK_User = vendorstory.FK_User).Bio
    # Get All Last Story
    last_post = VendorStory.objects.filter(Publish = True).order_by('-DateCreate')[:7]
    # Get All Tag
    tags = vendorstory.FK_Tag.all()
    # Set Point Count
    point_count = vendorstory.FK_Point.all().count()
    # Get All Comment
    story_comments = StoryPost.objects.filter(FK_VendorStory = vendorstory, Available = True)
    # Show Message
    if status != None:
        ShowAlart = bool(status)
        AlartMessage = msg
    else:
        ShowAlart = False
        AlartMessage = ''

    context = {
        'This_User_Profile':this_profile,
        'This_User_Inverntory': this_inverntory,
        'Options': options,
        'MenuList':navbar,
        'Vendorstory':vendorstory,
        'StoryDate':story_date,
        'Writer':writer_bio,
        'LastStory':last_post,
        'PointCount':point_count,
        'Tags':tags,
        'Comments':story_comments,
        'ShowAlart':ShowAlart,
        'AlartMessage':AlartMessage,
        'View_Count':view_count,
    }

    return render(request, 'blog/pages/singlevendorstory.html', context)





# Set Story Point
def SetStoryPoint(request):
    response_data = {}

    if request.user.is_authenticated :
        
        if request.POST.get('action') == 'post':
            try:
                point = request.POST.get("rating")
                story_Slug = request.POST.get("Slug")
            except:
                response_data['error'] = 'خطای دریافت اطلاعات'
                response_data['status'] = False
                return JsonResponse(response_data)
            # Get This Story
            this_story = VendorStory.objects.get(Slug = story_Slug)
            # Change Point
            if point != '':
                if this_story.FK_Point.filter(id = request.user.id).count() == 0:

                    if this_story.Point == 0:

                        this_story.Point += float(point)
                        this_story.FK_Point.add(request.user)
                        this_story.save()
                    else:

                        this = (float(this_story.Point) + float(point)) / 2
                        this_story.Point = this
                        this_story.FK_Point.add(request.user)
                        this_story.save()
                    
                    response_data['msg'] = 'ok'
                    response_data['status'] = True
                    return JsonResponse(response_data)

                else:

                    response_data['error'] = 'شما قبلا به این داستان امتیاز داده اید.'
                    response_data['status'] = False
                    return JsonResponse(response_data)

            else:
                
                response_data['error'] = 'خطای دریافت اطلاعات'
                response_data['status'] = False
                return JsonResponse(response_data)
        else:

            response_data['error'] = 'خطای دریافت اطلاعات'
            response_data['status'] = False
            return JsonResponse(response_data)

    else:
        response_data['error'] = 'لطفا به حساب کاربری خود وارد شوید'
        response_data['status'] = False
        return JsonResponse(response_data)





# Add New Story Comment
def AddNewStoryComment(request, Story_Slug, id = None):

    if request.user.is_authenticated :

        if request.method == 'POST':

            try:
                des = request.POST["comment_des"]
            except:
                des = False
            
            # Get This Story
            this_story = VendorStory.objects.get(Slug = Story_Slug)
            # Add New Comment
            if des != '':
                
                if id == None:

                    NewComment = StoryPost.objects.create(FK_UserAdder = request.user, FK_VendorStory = this_story, Description = des)
                    Alert.objects.create(Part = '29', FK_User = request.user, Slug = NewComment.id)

                    return redirect("blog:Re_SingleVendorStory",
                    Story_Slug = this_story.Slug,
                    status = 1,
                    msg =  'نظر شما ثبت شد، و پس از تایید کارشناسان نمایش داده خواهد شد.')

                else:

                    # Get Fathers Comment
                    father = StoryPost.objects.get(id = id)
                    NewComment = StoryPost.objects.create(FK_UserAdder = request.user, FK_VendorStory = this_story, Description = des, FK_Pater = father)
                    Alert.objects.create(Part = '29', FK_User = request.user, Slug = NewComment.id)

                    return redirect("blog:Re_SingleVendorStory",
                    Story_Slug = this_story.Slug,
                    status = 1,
                    msg =  'نظر شما ثبت شد، و پس از تایید کارشناسان نمایش داده خواهد شد.')

            else:

                return redirect("blog:Re_SingleVendorStory",
                Story_Slug = this_story.Slug,
                status = 1,
                msg =  'متن نظر نمی تواند خالی باشد!')
        else:

            return redirect("blog:Re_SingleVendorStory", Story_Slug = this_story.Slug)

    else:

        return redirect("nakhll_market:AccountLogin")



# Show All Blog Story
def show_all_blog_story(request):
    if request.user.is_authenticated:
        This_User_Info = GetUserInfo().run(request)
        this_profile = This_User_Info["user_profiel"]
        this_inverntory = This_User_Info["user_inverntory"]
    else:
        this_profile = None
        this_inverntory = None
    # Get Menu Item
    options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
    # Get Nav Bar Menu Item
    navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
    # --------------------------------------------------------------------
    # Get All Story
    all_story = VendorStory.objects.filter(Publish = True)

    context = {
        'This_User_Profile':this_profile,
        'This_User_Inverntory': this_inverntory,
        'Options': options,
        'MenuList':navbar,
        'Story':all_story,
    }

    return render(request, 'blog/pages/vendorstory.html', context)