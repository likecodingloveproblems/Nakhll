from django.db import models
from django.contrib.auth.models import User
from nakhll_market.models import Shop, Product, Tag, Profile
from django.utils.deconstruct import deconstructible
import uuid, random, string, os, time
from tinymce.models import HTMLField
from django_jalali.db import models as jmodels
from django.shortcuts import reverse

from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill

# Rename Method
@deconstructible
class PathAndRename():
    def __init__(self, sub_path):
        self.path = sub_path

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        rand_strings = ''.join( random.choice(string.ascii_letters+string.digits) for i in range(6))
        filename = '{}.{}'.format(rand_strings, ext)

        return os.path.join(self.path, filename)


#----------------------------------------------------------------------------------------------------------------------------------

# CategoryBlog (دسته بندی) Model 
class CategoryBlog(models.Model):
    Title=models.CharField(verbose_name='عنوان دسته بندی', max_length=150, unique=True, db_index=True)
    Description=models.TextField(verbose_name='درباره دسته بندی', blank=True)
    Image=models.ImageField(verbose_name='عکس دسته بندی', upload_to=PathAndRename('media/Pictures/Categories/'), help_text='عکس دسته بندی را اینجا وارد کنید', blank=True, null=True)
    Slug=models.SlugField(verbose_name='شناسه دسته بندی', unique=True, db_index=True)
    FK_SubCategory =models.ForeignKey('self', on_delete=models.SET_NULL, verbose_name='سر دسته', blank=True, null=True, related_name='SubCategoryBlog')
    DateCreate=jmodels.jDateField(verbose_name='تاریخ ثبت دسته بندی', auto_now_add=True)
    DateUpdate=jmodels.jDateField(verbose_name='تاریخ بروزرسانی دسته بندی', auto_now=True)
    PUBLISH_STATUS =(
        (True,'منتشر شده'),
        (False,'در انتظار تایید'),
    )
    Publish=models.BooleanField(verbose_name='وضعیت انتشار دسته بندی', choices=PUBLISH_STATUS, default=False)
    FK_User=models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='تایید کننده', related_name='Category_Accept_blog', blank=True, null=True) 

    # Output Customization Based On Title 
    def __str__(self):
        return "{}".format(self.Title)

    # Ordering With Title
    class Meta:
     ordering = ('id','Title','DateCreate',)  
     verbose_name = "دسته بندی"
     verbose_name_plural = "دسته بندی ها"

#----------------------------------------------------------------------------------------------------------------------------------

# PostBlog(پست) Model
class PostBlog(models.Model):
    Title=models.CharField(max_length=300, verbose_name='عنوان پست ', db_index=True)
    Slug=models.SlugField(verbose_name='شناسه پست', unique=True, db_index=True)
    Content=HTMLField(verbose_name='متن پست')
    Summary=models.CharField(max_length=400, verbose_name='خلاصه', blank=True)
    Index_Image=models.ImageField(verbose_name='تصویر صفحه اصلی', upload_to=PathAndRename('media/Pictures/Blog/Post/IndexImage/'), help_text='تصویری که در صفحه اصلی نمایش داده می شود را اینجا بارگذاری نمایید.', default='static/images/banner_default.jpg')
    Slider=models.ImageField(verbose_name='اسلایدر پست', upload_to=PathAndRename('media/Pictures/Blog/Post/Slider/'), help_text='تصویری که به صورت اسلایدر در صفحه پست نمایش داده می شود را اینجا بارگذاری نمایید.', null=True, blank=True)
    FK_Shop=models.ForeignKey(Shop, null=True, on_delete=models.SET_NULL, verbose_name='حجره',related_name='ShopBlog', blank=True)
    FK_Category=models.ManyToManyField(CategoryBlog, verbose_name='دسته بندی های پست', related_name='PostCategoryBlog', blank=True)
    FK_Point=models.ManyToManyField(User, verbose_name='امتیاز دهنده', related_name='Post_Point', blank=True)
    Point=models.FloatField(verbose_name='امتیاز', default=0.0)
    DateCreate=jmodels.jDateField(verbose_name='تاریخ بارگذاری', auto_now_add=True)
    DateUpdate=jmodels.jDateField(verbose_name='تاریخ بروزرسانی', auto_now=True)
    PUBLISH_STATUS =(
        (True,'منتشر شده'),
        (False,'در انتظار تایید'),
    )
    Publish=models.BooleanField(verbose_name='وضعیت انتشار', choices=PUBLISH_STATUS, default=False)
    FK_User=models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='نویسنده', related_name='authorPost', blank=True, null=True) 
    FK_Tag=models.ManyToManyField(Tag, verbose_name='تگ ها', related_name='Post_Tag', blank=True)

    def __str__(self):
        return "{}".format(self.Title)

    def get_absolute_url(self):
        return reverse("blog:BlogPost", kwargs={
            'Post_Slug': self.Slug,
        })

    def get_poin(self):
        try:
            return round(self.Point, 1)
        except:
            return 0

    class Meta:
        ordering = ('DateCreate','Title',)   
        verbose_name = "پست"
        verbose_name_plural = "پست ها"

#----------------------------------------------------------------------------------------------------------------------------------

# VendorStory (داستان حجره دار) Model
class VendorStory(models.Model):
    Title=models.CharField(max_length=300, verbose_name='عنوان ', db_index=True)
    Slug=models.SlugField(verbose_name='شناسه', unique=True, db_index=True)
    Content=HTMLField(verbose_name='متن')
    Summary=models.CharField(max_length=400, verbose_name='خلاصه', blank=True)
    Slider=models.ImageField(verbose_name='اسلایدر', upload_to=PathAndRename('media/Pictures/Markets/SubMarkets/Shops/VendorStory/'), help_text='عکسی که در بالای صفحه داستان محصول قرار می گیرد را اینجا وارد نمایید.', null=True, blank=True)
    Shop_Image=models.ImageField(verbose_name='عکس حجره دار', upload_to=PathAndRename('media/Pictures/Markets/SubMarkets/Shops/VendorStory/'), help_text='در صورتی که نمی خواهید از عکس حجره دار استفاده شود، عکس جایگزین را اینجا وارد نمایید.', null=True, blank=True)
    Shop_Image_thumbnail = ImageSpecField(source='Shop_Image',
                                processors=[ResizeToFill(120, 120)],
                                format='JPEG',
                                options={'quality': 60} )
    SHOW_STATUS =(
        (True,'نمایش عکس جایگزین'),
        (False,'نمایش عکس پروفایل حجره دار'),
    )
    Show_Image=models.BooleanField(verbose_name='نمایش عکس جایگزین', choices=SHOW_STATUS, default=False, help_text='وضعیت عکس حجره دار را اینجا مشخص نمایید.')
    FK_Shop=models.ForeignKey(Shop, null=True, on_delete=models.SET_NULL, verbose_name='حجره',related_name='Shop_VendorStory')
    FK_Point=models.ManyToManyField(User, verbose_name='امتیاز دهنده', related_name='Story_Point', blank=True)
    Point=models.FloatField(verbose_name='امتیاز', default=0.0)
    DateCreate=jmodels.jDateField(verbose_name='تاریخ بارگذاری', auto_now_add=True)
    DateUpdate=jmodels.jDateField(verbose_name='تاریخ بروزرسانی', auto_now=True)
    PUBLISH_STATUS =(
        (True,'منتشر شده'),
        (False,'در انتظار تایید'),
    )
    Publish=models.BooleanField(verbose_name='وضعیت انتشار', choices=PUBLISH_STATUS, default=False)
    FK_User=models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='نویسنده', related_name='VendorStory_Accept', blank=True, null=True)
    FK_Tag=models.ManyToManyField(Tag, verbose_name='تگ ها', related_name='Story_Tag', blank=True)

    def __str__(self):
        return "{}".format(self.Title)

    def get_absolute_url(self):
        return reverse("blog:vendorstory", kwargs={
            'Story_Slug': self.Slug,
        })

    def get_poin(self):
        try:
            return round(self.Point, 1)
        except:
            return 0

    def Image_thumbnail_url(self):
        try:
            i = self.Shop_Image_thumbnail.url
            url = self.Shop_Image_thumbnail.url
            return url
        except:
            url ="https://nakhll.com/media/Pictures/default.jpg"
            return url

    class Meta:
        ordering = ('DateCreate','Title',)   
        verbose_name = "داستان حجره دار"
        verbose_name_plural = "داستان های حجره دار"

#----------------------------------------------------------------------------------------------------------------------------------

# CommentPost (نظر پست) Model
class CommentPost(models.Model):
    FK_UserAdder=models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='کاربر', related_name='AddComment', null=True)
    FK_Post=models.ForeignKey(PostBlog, on_delete=models.SET_NULL, verbose_name='پست', blank=True, null=True)
    Description=models.TextField(verbose_name='توضیخات نظر')
    FK_Like=models.ManyToManyField(User, verbose_name='لایک کننده', related_name='Post_Comment_Like', blank=True)
    FK_Pater=models.ForeignKey('self', on_delete=models.SET_NULL, verbose_name='ریپلای شده', blank=True, null=True)
    Available=models.BooleanField(verbose_name='وضعیت انتشار نظر', default=False)
    DateCreate=models.DateTimeField(verbose_name='تاریخ ثبت نظر', auto_now_add=True)
    FK_User=models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='تایید کننده', related_name='VisiteComment', blank=True, null=True) 

    # Output Customization Based On Title,Date Create
    def __str__(self):
        return "{} - {}".format(self.FK_UserAdder, self.FK_Post)

    # Get Comment Profile Image
    def get_comment_profile_image(self):
        try:
            # Get User Profile
            this_profile = Profile.objects.get(FK_User = self.FK_UserAdder)
            return this_profile.Image_thumbnail_url()
        except:
            url = "https://nakhll.com/media/Pictures/avatar.png"
            return url


    # Ordering With DateCreate
    class Meta:
        ordering = ('id',)   
        verbose_name = "نظر پست"
        verbose_name_plural = "نظرات پست"

#----------------------------------------------------------------------------------------------------------------------------------

# StoryPost (نظر داستان) Model
class StoryPost(models.Model):
    FK_UserAdder=models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='کاربر', related_name='UserAdder', null=True)
    FK_VendorStory=models.ForeignKey(VendorStory, on_delete=models.SET_NULL, verbose_name='داستان', blank=True, null=True)
    Description=models.TextField(verbose_name='توضیخات نظر')
    FK_Like=models.ManyToManyField(User, verbose_name='لایک کننده', related_name='Story_Comment_Like', blank=True)
    FK_Pater=models.ForeignKey('self', on_delete=models.SET_NULL, verbose_name='ریپلای شده', blank=True, null=True)
    Available=models.BooleanField(verbose_name='وضعیت انتشار نظر', default=False)
    DateCreate=models.DateTimeField(verbose_name='تاریخ ثبت نظر', auto_now_add=True)
    FK_User=models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='تایید کننده', related_name='UserVisiteComment', blank=True, null=True) 

    # Output Customization Based On Title,Date Create
    def __str__(self):
        return "{} - {}".format(self.FK_UserAdder, self.FK_VendorStory)

    # Get Comment Profile Image
    def get_comment_profile_image(self):
        try:
            # Get User Profile
            this_profile = Profile.objects.get(FK_User = self.FK_UserAdder)
            return this_profile.Image_thumbnail_url()
        except:
            url = "https://nakhll.com/media/Pictures/avatar.png"
            return url

    # Ordering With DateCreate
    class Meta:
        ordering = ('id',)   
        verbose_name = "نظر داستان"
        verbose_name_plural = "نظرات داستان"