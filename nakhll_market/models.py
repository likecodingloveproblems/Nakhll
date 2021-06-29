from __future__ import unicode_literals

from django.db.models.aggregates import Avg, Sum
from django.db.models.deletion import SET_DEFAULT
from my_auth.models import ProfileManager
from django.db import models
from django.db.models import F, Q, Count
from django.db.models.functions import Cast
from django.db.models.fields import CharField, FloatField
from tinymce.models import HTMLField
from django.contrib.auth.models import User,Group 
from django.contrib.auth.models import (AbstractUser)
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
from django.utils import timezone
import uuid, random, string, os, time
from django.shortcuts import reverse, get_object_or_404
from django_jalali.db import models as jmodels
from django.dispatch import receiver
import json
import math
import datetime
from django.utils.translation import ugettext_lazy as _
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

# Random Referense Code
@deconstructible
class BuildReferenceCode():
    def __init__(self, Code_Size):
        self.size = Code_Size

    def __call__(self):
        random_str = ''.join( random.choice(string.ascii_lowercase+string.digits) for i in range(self.size))

        return (random_str)

# Fix Image Roting
def upload_path(instance,filename):
    return '{0}/{1}'.format("disforum", filename)

#----------------------------------------------------------------------------------------------------------------------------------

# Tag (تگ) Model
class Tag(models.Model):
    Title=models.CharField(verbose_name='عنوان', max_length=500)
    Slug=models.SlugField(verbose_name='شناسه ویژگی', unique=True, db_index=True)
    Description=models.TextField(verbose_name='توضیحات', blank=True) 

    # Output Customization Based On Title
    def __str__(self):
        return "{}".format(self.Title)

    # Ordering With id
    class Meta:
        ordering = ('id',)   
        verbose_name = "تگ"
        verbose_name_plural = "تگ ها"

#----------------------------------------------------------------------------------------------------------------------------------

# Market (بازارچه) Model 
class Market(models.Model):
    ID=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    FK_MarketManager=models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='مدیر بازارچه', related_name='MarketManager', null=True)
    Title=models.CharField(verbose_name='نام بازارچه', max_length=100, unique=True, db_index=True)
    Description=models.TextField(verbose_name='درباره بازارچه', blank=True)
    Image=models.ImageField(verbose_name='عکس بازارچه', upload_to=PathAndRename('media/Pictures/Markets/'))
    Slug=models.SlugField(verbose_name='شناسه بازارچه', db_index=True, unique=True)
    URL=models.URLField(verbose_name='لینک اخبار مربوط به بازارچه', blank=True)
    DateCreate=models.DateTimeField(verbose_name='تاریخ ثبت بازارچه', auto_now_add=True)
    DateUpdate=models.DateTimeField(verbose_name='تاریخ بروزرسانی بازارچه', auto_now=True)
    AVAILABLE_STATUS =(
        (True,'فعال'),
        (False,'غیر فعال'),
    )
    PUBLISH_STATUS =(
        (True,'منتشر شده'),
        (False,'در انتظار تایید'),
    )
    Available=models.BooleanField(verbose_name='وضعیت ثبت بازارچه', choices=AVAILABLE_STATUS, default=True)
    Publish=models.BooleanField(verbose_name='وضعیت انتشار بازارچه', choices=PUBLISH_STATUS, default=False)
    FK_User=models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='تایید کننده', related_name='Market_Accept', blank=True, null=True) 
    FK_Tag=models.ManyToManyField(Tag, verbose_name='تگ ها', related_name='Market_Tagss', blank=True)

    @property
    def title(self):
        return self.Title

    @property
    def url(self):
        return reverse("nakhll_market:Markets")

    def __str__(self):
        return "{}".format(self.Title)

    class Meta:
        ordering = ('DateCreate','Title',)
        verbose_name = "بازارچه"
        verbose_name_plural = "بازارچه ها"

#----------------------------------------------------------------------------------------------------------------------------------

# Market Banner (بنر بازارچه ها) Model
class MarketBanner (models.Model):
    FK_Market =models.ForeignKey(Market, on_delete=models.SET_NULL, verbose_name='نام بازارچه', related_name='Market_Banner', null=True)
    Title=models.CharField(verbose_name='برچسب روی بنر', max_length=100, db_index=True)
    Description=models.CharField(max_length=350, verbose_name='درباره بنر', blank=True)
    URL=models.URLField(verbose_name='لینک', help_text='لینکی که در صورت کلیک به آن منتقل می شود', blank=True)
    Image=models.ImageField(verbose_name='بنر بازارچه', upload_to=PathAndRename('media/Pictures/Markets/Banners/'), help_text='بنر بازارچه را اینجا وارد کنید')
    BannerBuilder=models.CharField(verbose_name='نام تولید کننده بنر', max_length=120, blank=True)
    BannerURL=models.URLField(verbose_name='لینک تولید کننده بنر', blank=True)
    DateCreate=models.DateTimeField(verbose_name='تاریخ بارگذاری بنر بازارچه', auto_now_add=True)
    DateUpdate=models.DateTimeField(verbose_name='تاریخ بروزرسانی بنر بازارچه', auto_now=True)
    AVAILABLE_STATUS =(
        (True,'فعال'),
        (False,'غیر فعال'),
    )
    PUBLISH_STATUS =(
        (True,'منتشر شده'),
        (False,'در انتظار تایید'),
    )
    Available=models.BooleanField(verbose_name='وضعیت بارگذاری بنر بازارچه', choices=AVAILABLE_STATUS, default=True)
    Publish=models.BooleanField(verbose_name='وضعیت انتشار بنر بازارچه', choices=PUBLISH_STATUS, default=False)
    FK_User=models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='تایید کننده', related_name='Market_Banner_Accept', blank=True, null=True) 
    FK_Tag=models.ManyToManyField(Tag, verbose_name='تگ ها', related_name='Market_Banner_Tag', blank=True)

    # Output Customization Based On Title
    def __str__(self):
        return "{}".format(self.Title)

    # Ordering With DateCreate
    class Meta:
        ordering = ('id','Title',)  
        verbose_name = "بنر بازارچه"
        verbose_name_plural = "بنر بازارچه ها"

#----------------------------------------------------------------------------------------------------------------------------------  

# SubMarket (راسته) Model 
class SubMarket(models.Model):
    ID=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    FK_Market=models.ForeignKey(Market, on_delete=models.SET_NULL, verbose_name='نام بازارچه', related_name='FatherMarket', null=True)
    Title=models.CharField(verbose_name='نام راسته', max_length=100, db_index=True)
    Description=models.TextField(verbose_name='درباره راسته', blank=True)
    Image=models.ImageField(verbose_name='عکس راسته',upload_to=PathAndRename('media/Pictures/Markets/SubMarkets/'), help_text='عکس مورد نظر را اینجا وارد کنید', null=True, blank=True)
    Slug=models.SlugField(verbose_name='شناسه راسته', unique=True, db_index=True)
    URL=models.URLField(verbose_name='لینک اخبار مربوط به راسته', blank=True)
    DateCreate=models.DateTimeField(verbose_name='تاریخ ثبت راسته', auto_now_add=True)
    DateUpdate=models.DateTimeField(verbose_name='تاریخ بروزرسانی راسته', auto_now=True)
    AVAILABLE_STATUS =(
        (True,'فعال'),
        (False,'غیر فعال'),
    )
    PUBLISH_STATUS =(
        (True,'منتشر شده'),
        (False,'در انتظار تایید'),
    )
    Available=models.BooleanField(verbose_name='وضعیت ثبت راسته', choices=AVAILABLE_STATUS, default=True)
    Publish=models.BooleanField(verbose_name='وضعیت انتشار راسته', choices=PUBLISH_STATUS, default=False)
    FK_User=models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='تایید کننده', related_name='SubMarket_Accept', blank=True, null=True) 
    FK_Tag=models.ManyToManyField(Tag, verbose_name='تگ ها', related_name='SubMarket_Tag', blank=True)

    @property
    def title(self):
        return self.Title

    @property
    def slug(self):
        return self.Slug

    @property
    def market(self):
        return self.FK_Market

    @property
    def url(self):
        return reverse(
            'nakhll_market:SubMarkets',
            kwargs={'submarket_slug':self.slug}
        )

    # Output Customization Based On Title
    def __str__(self):
        return "{}".format(self.Title)

    # Ordering With DateCreate
    class Meta:
        ordering = ('DateCreate','Title',)    
        verbose_name = "راسته"  
        verbose_name_plural ="راسته ها"

#----------------------------------------------------------------------------------------------------------------------------------

# SubMarket Banner (بنر راسته ها) Model
class SubMarketBanner (models.Model):
    FK_SubMarket=models.ForeignKey(SubMarket, on_delete=models.SET_NULL, verbose_name='نام راسته', related_name='SubMarket_Banner', null=True)
    Title=models.CharField(verbose_name='برچسب روی بنر', max_length=100, db_index=True)
    Description=models.TextField(verbose_name='درباره بنر',max_length=350, blank=True)
    URL=models.URLField(verbose_name='لینک', help_text='لینکی که در صورت کلیک به آن منتقل می شود', blank=True)
    Image=models.ImageField(verbose_name='بنر راسته', upload_to=PathAndRename('media/Pictures/Markets/SubMarkets/Banners/'), help_text='بنر راسته را اینجا وارد کنید')
    BannerBuilder=models.CharField(verbose_name='نام تولید کننده بنر', max_length=120, blank=True)
    BannerURL=models.URLField(verbose_name='لینک تولید کننده بنر', blank=True)
    DateCreate=models.DateTimeField(verbose_name='تاریخ بارگذاری بنر راسته', auto_now_add=True)
    DateUpdate=models.DateTimeField(verbose_name='تاریخ بروزرسانی بنر راسته', auto_now=True)
    AVAILABLE_STATUS =(
        (True,'فعال'),
        (False,'غیر فعال'),
    )
    PUBLISH_STATUS =(
        (True,'منتشر شده'),
        (False,'در انتظار تایید'),
    )
    Available=models.BooleanField(verbose_name='وضعیت بارگذاری بنر راسته', choices=AVAILABLE_STATUS, default=True)
    Publish=models.BooleanField(verbose_name='وضعیت انتشار راسته', choices=PUBLISH_STATUS, default=False)
    FK_User=models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='تایید کننده', related_name='SubMarket_Banner_Accept', blank=True, null=True) 
    FK_Tag=models.ManyToManyField(Tag, verbose_name='تگ ها', related_name='SubMarket_Banner_Tag', blank=True)

    # Output Customization Based On Title
    def __str__(self):
        return "{}".format(self.Title)

    # Ordering With DateCreate
    class Meta:
        ordering = ('id','Title',)  
        verbose_name = "بنر راسته"
        verbose_name_plural = "بنر راسته ها"

#----------------------------------------------------------------------------------------------------------------------------------

class CategoryManager(models.Manager):

    def get_category_publush_avaliable(self):
        categories = Category.objects\
            .filter(Publish = True, Available = True, FK_SubCategory = None)\
            .annotate(product_count = Count('ProductCategory'))\
            .filter(product_count__gt=5)
        categories_id = list(categories\
            .values_list('id', flat=True))
        categories = categories\
            .filter(pk__in=random.sample(categories_id, 12))
        return categories
 
    
# Category (دسته بندی) Model 
class Category(models.Model):
    objects = CategoryManager()
    Title=models.CharField(verbose_name='عنوان دسته بندی', max_length=150, unique=True, db_index=True)
    Description=models.TextField(verbose_name='درباره دسته بندی', blank=True)
    Image=models.ImageField(verbose_name='عکس دسته بندی', upload_to=PathAndRename('media/Pictures/Categories/'), help_text='عکس دسته بندی را اینجا وارد کنید', blank=True, null=True)
    Image_thumbnail = ImageSpecField(source='Image',
                                    processors=[ResizeToFill(175, 175)],
                                    format='JPEG',
                                    options={'quality': 60} )
    Slug=models.SlugField(verbose_name='شناسه دسته بندی', unique=True, db_index=True)
    URL=models.URLField(verbose_name='لینک اخبار مربوط به دسته بندی', blank=True)
    FK_SubCategory =models.ForeignKey('self', on_delete=models.SET_NULL, verbose_name='سر دسته', blank=True, null=True, related_name='SubCategory')
    DateCreate=models.DateTimeField(verbose_name='تاریخ ثبت دسته بندی', auto_now_add=True)
    DateUpdate=models.DateTimeField(verbose_name='تاریخ بروزرسانی دسته بندی', auto_now=True)
    AVAILABLE_STATUS =(
        (True,'فعال'),
        (False,'غیر فعال'),
    )
    PUBLISH_STATUS =(
        (True,'منتشر شده'),
        (False,'در انتظار تایید'),
    )
    Available=models.BooleanField(verbose_name='وضعیت ثبت دسته بندی', choices=AVAILABLE_STATUS, default=True)
    Publish=models.BooleanField(verbose_name='وضعیت انتشار دسته بندی', choices=PUBLISH_STATUS, default=False)
    FK_User=models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='تایید کننده', related_name='Category_Accept', blank=True, null=True) 

    @property
    def title(self):
        return self.Title

    @title.setter
    def title(self, value):
        self.Title = value

    @property
    def slug(self):
        return self.Slug

    @slug.setter
    def slug(self, value):
        self.Slug = value

    @property
    def description(self):
        return self.Description

    @property
    def image(self):
        return self.Image
    
    @property
    def image_thumbnail(self):
        return self.Image_thumbnail_url

    @property
    def date_created(self):
        return self.DateCreate

    @property
    def date_updated(self):
        return self.DateUpdate

    @property
    def available(self):
        return self.Available

    @property
    def publish(self):
        return self.Publish

    @property
    def sub_category(self):
        return self.FK_SubCategory

    @property
    def url(self):
        return '/category/{}/newest/none/'.format(self.Slug)

    def __str__(self):
        return "{}".format(self.Title)

    def is_father(self):
        if self.FK_SubCategory is None:
            return True
        else:
            return False

    def get_sub_category(self):
        return Category.objects.filter(FK_SubCategory = self)

    def Image_thumbnail_url(self):
        try:
            i = self.Image_thumbnail.url
            url = self.Image_thumbnail.url
            return url
        except:
            url ="https://nakhll.com/media/Pictures/default.jpg"
            return url

    class Meta:
     ordering = ('id','Title','DateCreate',)  
     verbose_name = "دسته بندی"
     verbose_name_plural = "دسته بندی ها"

#----------------------------------------------------------------------------------------------------------------------------------

# PostRange (ناحیه ارسال) Model
class PostRange (models.Model):
    State=models.CharField(verbose_name='استان', max_length=50)
    BigCity=models.CharField(max_length=50, verbose_name='شهرستان', blank=True)
    City=models.CharField(max_length=50, verbose_name='شهر', blank=True)

    @property
    def state(self):
        return self.State

    @state.setter
    def state(self, value):
        self.State = value

    @property
    def big_city(self):
        return self.BigCity

    @big_city.setter
    def big_city(self, value):
        self.BigCity = value

    @property
    def city(self):
        return self.City

    @city.setter
    def city(self, value):
        self.City = value

    # Output Customization Based On State - BigCity - City 
    def __str__(self):
        if (self.BigCity != '') and (self.City == ''):
            return "استان {} - شهرستان {}".format(self.State, self.BigCity)
        elif (self.BigCity != '') and (self.City != ''):
            return "استان {} - شهرستان {} - شهر {}".format(self.State, self.BigCity, self.City)
        else:
            return "استان {}".format(self.State)

    # Get Post Range To String
    def get_string(self):
        if (self.BigCity != '') and (self.City == ''):
            return 'استان' + ' ' + self.State + ', ' + 'شهرستان' + ' ' + self.BigCity
        elif (self.BigCity != '') and (self.City != ''):
            return 'استان ' + ' ' + self.State + ', ' + 'شهرستان ' + ' ' + self.BigCity + ', ' + 'شهر' + ' ' + self.City
        else:
            return 'استان' + ' ' + self.State
        
    # Ordering With Title
    class Meta:
        ordering = ('id',)  
        verbose_name = "ناحیه ارسال"
        verbose_name_plural = "ناحیه های ارسال"

#----------------------------------------------------------------------------------------------------------------------------------

class ShopManager(models.Manager):

    def shop_managers_info(self):
        queryset = self.get_queryset()
        return queryset.values(
            'FK_ShopManager__first_name',
            'FK_ShopManager__last_name',
            'FK_ShopManager__User_Profile__NationalCode',
            'State',
            'BigCity',
            'City',
            'Location',
            )
    
    def shop_managers_info_marketing(self):
        queryset = self.get_queryset()
        return queryset.values(
            'FK_ShopManager__first_name',
            'FK_ShopManager__last_name',
            'FK_ShopManager__User_Profile__MobileNumber',
            'FK_SubMarket__Title',
            'FK_SubMarket__FK_Market__Title',
            'State',
            'BigCity',
            'City',
            'Location',
            )
        
    def most_last_week_sale_shops(self):
        queryset = self.get_queryset()
        number_of_days = 7
        now = timezone.now()
        one_week_ago = now - datetime.timedelta(days=7)
        return queryset\
            .filter(Publish=True, Available=True)\
            .filter(ShopProduct__Factor_Product__Factor_Products__OrderDate__gte=one_week_ago)\
            .annotate(number_sale=Sum('ShopProduct__Factor_Product__ProductCount'))\
            .order_by('-number_sale')[:5]

    def get_random_shops(self):
        # Shop.objects\
        # .filter(Publish = True, Available = True)\
        # .annotate(product_count = Count('ShopProduct'))\
        # .filter(product_count__gt=1)\
        # .order_by('?')[:12]
        sql = '''
            SELECT 
                "nakhll_market_shop"."ID",
                "nakhll_market_shop"."FK_ShopManager_id",
                "nakhll_market_shop"."Title",
                "nakhll_market_shop"."Slug",
                "nakhll_market_shop"."Description",
                "nakhll_market_shop"."Image",
                "nakhll_market_shop"."NewImage",
                "nakhll_market_shop"."ColorCode",
                "nakhll_market_shop"."Bio",
                "nakhll_market_shop"."State",
                "nakhll_market_shop"."BigCity",
                "nakhll_market_shop"."City",
                "nakhll_market_shop"."Location",
                "nakhll_market_shop"."Point",
                "nakhll_market_shop"."Holidays",
                "nakhll_market_shop"."DateCreate",
                "nakhll_market_shop"."DateUpdate",
                "nakhll_market_shop"."Edite",
                "nakhll_market_shop"."Available",
                "nakhll_market_shop"."Publish",
                "nakhll_market_shop"."FK_User_id",
                "nakhll_market_shop"."CanselCount",
                "nakhll_market_shop"."CanselFirstDate",
                "nakhll_market_shop"."LimitCancellationDate",
                "nakhll_market_shop"."documents",
                COUNT("nakhll_market_product"."ID") AS "product_count" 
            FROM "nakhll_market_shop" 
            LEFT OUTER JOIN 
                "nakhll_market_product" ON ("nakhll_market_shop"."ID" = "nakhll_market_product"."FK_Shop_id") 
            WHERE ("nakhll_market_shop"."Available" AND "nakhll_market_shop"."Publish") 
            GROUP BY "nakhll_market_shop"."ID" HAVING COUNT("nakhll_market_product"."ID") > 1  
            ORDER BY RANDOM() 
            LIMIT 12
        '''
        return Shop.objects.raw(sql)



# Shop (حجره) Model
class Shop(models.Model):
    objects = ShopManager()
    ID=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    FK_ShopManager=models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='حجره دار', related_name='ShopManager', null=True)
    Title=models.CharField(max_length=100, verbose_name='عنوان حجره', db_index=True)
    FK_SubMarket=models.ManyToManyField(SubMarket, verbose_name='نام راسته', related_name='FatherSubMarket', blank=True)
    Slug=models.SlugField(verbose_name='شناسه حجره', unique=True, db_index=True)
    Description=models.TextField(verbose_name='درباره حجره', blank=True)
    Image=models.ImageField(verbose_name='عکس حجره', upload_to=PathAndRename('media/Pictures/Markets/SubMarkets/Shops/'), help_text='عکس حجره را اینجا وارد کنید', default='static/Pictures/DefaultShop.png', null=True)
    Image_thumbnail = ImageSpecField(source='Image',
                                    processors=[ResizeToFill(175, 175)],
                                    format='JPEG',
                                    options={'quality': 60} )
    NewImage=models.ImageField(verbose_name='عکس جدید حجره', upload_to=PathAndRename('media/Pictures/Markets/SubMarkets/Shops/'), null=True, blank=True)
    ColorCode=models.CharField(max_length=9, verbose_name='کد رنگ', help_text='رنگ حجره را اینجا وارد کنید', blank=True)
    Bio=models.TextField(verbose_name='معرفی حجره دار', blank=True)
    State =models.CharField(verbose_name='استان', max_length=50, blank=True)
    BigCity=models.CharField(verbose_name='شهرستان', max_length=50, blank=True)
    City=models.CharField(max_length=50, verbose_name='شهر', blank=True)
    Location=models.CharField(verbose_name='موقعیت مکانی', max_length=150, blank=True, help_text='طول و عرض جغرافیایی')
    Point=models.PositiveIntegerField(verbose_name='امتیاز حجره', default=0)
    Holidays=models.CharField(verbose_name='روز های تعطیلی حجره', max_length=15, blank=True)
    DateCreate=models.DateTimeField(verbose_name='تاریخ ثبت حجره', auto_now_add=True)
    DateUpdate=models.DateTimeField(verbose_name='تاریخ بروزرسانی حجره', auto_now=True)
    #محدودیت های حجره
    AVAILABLE_STATUS =(
        (True,'فعال'),
        (False,'غیر فعال'),
    )
    PUBLISH_STATUS =(
        (True,'منتشر شده'),
        (False,'در انتظار تایید'),
    )
    EDITE_STATUS =(
        (True,'در حال بررسی تغییرات'),
        (False,'تغییری اعمال شده است'),
    )
    Edite=models.BooleanField(verbose_name='وضعیت ویرایش حجره', choices=EDITE_STATUS, default=False)
    Available=models.BooleanField(verbose_name='وضعیت ثبت حجره', choices=AVAILABLE_STATUS, default=True)
    Publish=models.BooleanField(verbose_name='وضعیت انتشار حجره', choices=PUBLISH_STATUS, default=False)
    FK_User=models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='تایید کننده', related_name='Shop_Accept', blank=True, null=True) 
    FK_Tag=models.ManyToManyField(Tag, verbose_name='تگ ها', related_name='Shop_Tag', blank=True)
    CanselCount=models.PositiveIntegerField(verbose_name='تعداد لغو سفارشات حجره', default = 0)
    CanselFirstDate=models.DateField(verbose_name='تاریخ اولین لغو سفارش', null = True, blank = True)
    LimitCancellationDate=models.DateField(verbose_name='تاریخ محدودیت لغو سفارشات', null = True, blank = True)
    documents=ArrayField(
        base_field=models.ImageField(
            verbose_name='عکس جدید حجره', 
            upload_to=PathAndRename('media/Pictures/Shop/Document/'), 
            null=True,
            blank=True
            ),
        default=list,
        blank=True,
        )

    
    @property
    def slug(self):
        return self.Slug

    @property
    def title(self):
        return self.Title

    @property
    def state(self):
        return self.State

    @property
    def url(self):
        return self.get_absolute_url

    @property
    def image_thumbnail_url(self):
        return self.Image_thumbnail_url

    def __str__(self):
        return "{}".format(self.Title)

    def get_absolute_url(self):
        return reverse("nakhll_market:ShopsDetail", kwargs={
            'shop_slug': self.Slug
        })

    def Image_thumbnail_url(self):
        try:
            i = self.Image_thumbnail.url
            url = self.Image_thumbnail.url
            return url
        except:
            url ="https://nakhll.com/media/Pictures/default.jpg"
            return url

    def get_url(self):
        return reverse("nakhll_market:ShopsDetail", kwargs={
            'shop_slug': self.Slug,
        })

    def get_holidays(self):
        return self.Holidays.split('-')

    def get_products_category(self):
        category = []
        for item in self.get_products():
            for category_item in item.FK_Category.filter(FK_SubCategory = None, Publish = True):
                category.append(category_item)
        category = list(dict.fromkeys(category))
        return category

    def get_products(self):
        return Product.objects.filter(Available = True, Publish = True, FK_Shop = self)

    def get_all_products(self):
        return Product.objects.filter(FK_Shop = self)

    def get_all_products_for_view(self):
        this_shop_product = list(Product.objects.filter(FK_Shop = self, Available = True, Publish = True, Status__in = ['1', '2', '3']).order_by('-DateCreate'))
        this_shop_product += list(Product.objects.filter(FK_Shop = self, Available = True, Publish = True, Status = '4').order_by('-DateCreate'))
        return this_shop_product

    def get_banners(self):
        return ShopBanner.objects.filter(FK_Shop = self, Available = True, Publish = True)

    def get_comments(self):
        return ShopComment.objects.filter(FK_Shop = self, Available = True)

    def get_managment_image(self):
        return Profile.objects.get(FK_User = self.FK_ShopManager).Image_thumbnail_url()

    def get_shop_manager_full_name(self):
        return '{} {}'.format(self.FK_ShopManager.first_name, self.FK_ShopManager.last_name)

    class Meta:
        ordering = ('DateCreate','Title',)  
        verbose_name = "حجره"
        verbose_name_plural = "حجره ها"

#----------------------------------------------------------------------------------------------------------------------------------

# BankAccount (حساب بانکی) Model
class BankAccount(models.Model):
    ID=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    FK_Profile=models.OneToOneField('Profile', on_delete=models.SET_NULL, verbose_name='نام شخص', related_name='BankAccount_Shop', null=True)
    CreditCardNumber=models.CharField(verbose_name='شماره کارت بانکی', max_length=16)
    ShabaBankNumber=models.CharField(verbose_name='شماره شباء', max_length=26)
    AccountOwner=models.CharField(verbose_name='نام و نام خانوادگی صاحب حساب', max_length=300)

    # Output Customization Based On AccountOwner
    def __str__(self):
        return "{}".format(self.AccountOwner)

    # Ordering With id
    class Meta:
        ordering = ('ID',)   
        verbose_name = "حساب بانکی"
        verbose_name_plural = "حساب های بانکی"

#----------------------------------------------------------------------------------------------------------------------------------

# Shop Banners (بنر حجره) Model
class ShopBanner (models.Model):
    FK_Shop=models.ForeignKey(Shop, on_delete=models.SET_NULL, verbose_name='نام حجره', related_name='Shop_Banner', null=True)
    Title=models.CharField(verbose_name='برچسب روی بنر', max_length=100, blank=True)
    Description=models.TextField(verbose_name='درباره بنر',max_length=350, blank=True)
    URL=models.URLField(verbose_name='لینک', help_text='لینکی که در صورت کلیک به آن منتقل می شود', blank=True)
    Image_thumbnail = ImageSpecField(source='Image',
                                    processors=[ResizeToFill(250, 250)],
                                    format='JPEG',
                                    options={'quality': 60})
    Image=models.ImageField(verbose_name='بنر حجره', upload_to=PathAndRename('media/Pictures/Markets/SubMarkets/Shops/Banners'), help_text='بنر حجره را اینجا وارد کنید')
    NewImage=models.ImageField(verbose_name='عکس جدید حجره', upload_to=PathAndRename('media/Pictures/Markets/SubMarkets/Shops/Banners'), null=True, blank=True)
    BannerBuilder=models.CharField(verbose_name='نام تولید کننده بنر', max_length=120, blank=True)
    BannerURL=models.URLField(verbose_name='لینک تولید کننده بنر', blank=True)
    DateCreate=models.DateTimeField(verbose_name='تاریخ بارگذاری بنر حجره', auto_now_add=True)
    DateUpdate=models.DateTimeField(verbose_name='تاریخ بروزرسانی بنر حجره', auto_now=True)
    AVAILABLE_STATUS =(
        (True,'فعال'),
        (False,'غیر فعال'),
    )
    PUBLISH_STATUS =(
        (True,'منتشر شده'),
        (False,'در انتظار تایید'),
    )
    EDITE_STATUS =(
        (True,'در حال بررسی تغییرات'),
        (False,'تغییری اعمال شده است'),
    )
    Edite=models.BooleanField(verbose_name='وضعیت ویرایش بنر حجره', choices=EDITE_STATUS, default=False)
    Available=models.BooleanField(verbose_name='وضعیت بارگذاری بنر حجره', choices=AVAILABLE_STATUS, default=True)
    Publish=models.BooleanField(verbose_name='وضعیت انتشار بنر حجره', choices=PUBLISH_STATUS, default=False)
    FK_User=models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='تایید کننده', related_name='Shop_Banner_Accept', blank=True, null=True) 
    FK_Tag=models.ManyToManyField(Tag, verbose_name='تگ ها', related_name='Shop_Banner_Tag', blank=True)

    def Image_thumbnail_url(self):
        try:
            i = self.Image_thumbnail.url
            url = self.Image_thumbnail.url
            return url
        except:
            url ="static/images/banner_default.jpg"
            return url

    def __str__(self):
        return "{}".format(self.Title)

    class Meta:
        ordering = ('id',)   
        verbose_name = "بنر حجره"
        verbose_name_plural = "بنر حجره ها"

#----------------------------------------------------------------------------------------------------------------------------------

# Shop Movie (فیلم حجره) Model
class ShopMovie (models.Model):
    FK_Shop=models.ForeignKey(Shop, on_delete=models.SET_NULL, verbose_name='نام حجره', related_name='Shop_Movie', null=True)
    Title=models.CharField(verbose_name='عنوان فیلم', max_length=100, db_index=True)
    Description=models.TextField(verbose_name='توضیخات فیلم',max_length=350, blank=True)
    URL=models.URLField(verbose_name='لینک خارجی فیلم', help_text='اگر فیلم خود را جای دیگری بارگذاری کرده اید، لینک آن را اینجا وارد کنید', blank=True)
    Video=models.FileField(verbose_name='فیلم', upload_to=PathAndRename('media/Videos/Markets/SubMarkets/Shops'), help_text='فیلم خود را اینجا وراد کنید', blank=True, null=True)
    BannerBuilder=models.CharField(verbose_name='نام تولید کننده فیلم', max_length=120, blank=True)
    BannerURL=models.URLField(verbose_name='لینک تولید کننده فیلم', blank=True)
    DateCreate=models.DateTimeField(verbose_name='تاریخ بارگذاری فیلم حجره', auto_now_add=True)
    DtatUpdate=models.DateTimeField(verbose_name='تاریخ بروزرسانی فیلم حجره', auto_now=True)
    AVAILABLE_STATUS =(
        (True,'فعال'),
        (False,'غیر فعال'),
    )
    PUBLISH_STATUS =(
        (True,'منتشر شده'),
        (False,'در انتظار تایید'),
    )
    EDITE_STATUS =(
        (True,'در حال بررسی تغییرات'),
        (False,'تغییری اعمال شده است'),
    )
    Edite=models.BooleanField(verbose_name='وضعیت ویرایش بنر حجره', choices=EDITE_STATUS, default=False)
    Available=models.BooleanField(verbose_name='وضعیت بارگذاری فیلم حجره', choices=AVAILABLE_STATUS, default=True)
    Publish=models.BooleanField(verbose_name='وضعیت انتشار فیلم حجره', choices=PUBLISH_STATUS, default=False)
    FK_User=models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='تایید کننده', related_name='Shop_Movie_Accept', blank=True, null=True) 
    FK_Tag=models.ManyToManyField(Tag, verbose_name='تگ ها', related_name='Shop_Movie_Tag', blank=True)

    # Output Customization Based On Title
    def __str__(self):
        return "{}".format(self.Title)

    # Ordering With DateCreate
    class Meta:
        ordering = ('id','Title',)   
        verbose_name = "فیلم حجره"
        verbose_name_plural = "فیلم های حجره"

#----------------------------------------------------------------------------------------------------------------------------------

# Attribute (ویژگی ها) Model
class Attribute(models.Model):
    Title=models.CharField(verbose_name='عنوان ویژگی', max_length=300)
    Unit=models.CharField(verbose_name='واحد ویژگی', max_length=50)  
    PUBLISH_STATUS =(
        (True,'منتشر شده'),
        (False,'در انتظار تایید'),
    )
    Publish=models.BooleanField(verbose_name='وضعیت انتشار ویژگی', choices=PUBLISH_STATUS, default=False)
    FK_User=models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='تایید کننده', related_name='Attribute_Accept', blank=True, null=True) 

    @property
    def title(self):
        return self.Title

    @property
    def unit(self):
        return self.Unit

        
    # Output Customization Based On Title
    def __str__(self):
        if self.Unit != '-':
            return "{} (واحد : {})".format(self.Title, self.Unit)
        else:
            return "{} (بدون واحد)".format(self.Title)

    # Ordering With DateCreate
    class Meta:
        ordering = ('id','Title',)   
        verbose_name = "ویژگی"
        verbose_name_plural = "ویژگی ها"

#----------------------------------------------------------------------------------------------------------------------------------
class ProductManager(models.Manager):

    def get_most_discount_precentage_available_product(self):
        queryset = self.get_queryset()
        return queryset\
            .filter(Publish=True, Available = True, Status__in=['1','2','3'])\
            .exclude(OldPrice=0)\
            .annotate(OldPrice_float=Cast(F('OldPrice'), FloatField()))\
            .annotate(Price_float=Cast(F('Price'), FloatField()))\
            .annotate(discount_ratio=(F('OldPrice_float')-F('Price_float'))/F('OldPrice_float'))\
            .order_by('-discount_ratio')

    def get_one_most_discount_precenetage_available_product_random(self):
        result = self.get_most_discount_precentage_available_product()
        random_id = random.randint(0, int(result.count()/10))
        return result[random_id]

    def get_last_created_products(self):
        return Product.objects\
            .filter(Publish = True, Available = True, OldPrice = 0, Status__in = ['1', '2', '3'])\
                .order_by('-DateCreate')[:12]

    def get_last_created_discounted_products(self):
        return Product.objects\
            .filter(Publish = True, Available = True, Status__in = ['1', '2', '3'])\
            .exclude(OldPrice=0)\
            .order_by('-DateCreate')[:16]

    def get_random_products(self):
        return Product.objects\
            .filter(
                Publish = True,
                Available = True,
                OldPrice = 0,
                Status__in = ['1', '2', '3']
                )\
            .order_by('?')[:16]

    def get_most_discount_precentage_products(self):
        return Product.objects\
            .get_most_discount_precentage_available_product()\
            .order_by('?')[:15]

    def get_products_in_same_factor(self, id):
        try:
            product = Product.objects.get(ID=id)
            return Product.objects\
                .filter(Factor_Product__Factor_Products__FK_FactorPost__FK_Product=product)\
                .exclude(ID = product.ID)\
                .distinct()
        except:
            return None

        
# Product (محصول) Model
class Product(models.Model):
    POSTRANGE_TYPE=(
        ('1','سراسر کشور'),
        ('2','استانی'),
        ('3','شهرستانی'),
        ('4','شهری'),
    )
    PRODUCT_STATUS=(
        ('1','آماده در انبار'),
        ('2','تولید بعد از سفارش'),
        ('3','سفارشی سازی فروش'),
        ('4','موجود نیست'),
    )
    AVAILABLE_STATUS =(
        (True,'فعال'),
        (False,'غیر فعال'),
    )
    PUBLISH_STATUS =(
        (True,'منتشر شده'),
        (False,'در انتظار تایید'),
    )
    EDITE_STATUS =(
        (True,'در حال بررسی تغییرات'),
        (False,'تغییری اعمال شده است'),
    )
    objects = ProductManager()
    ID=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    Title=models.CharField(max_length=200, verbose_name='نام محصول', db_index=True)
    Slug=models.SlugField(verbose_name='شناسه محصول', unique=True, db_index=True)
    FK_SubMarket=models.ForeignKey(SubMarket, verbose_name='نام راسته', related_name='Product_SubMarket', null=True, on_delete=models.SET_NULL)
    Story=models.TextField(verbose_name='داستان محصول', blank=True)
    Description=models.TextField(verbose_name='درباره محصول', blank=True)
    Bio=models.TextField(verbose_name='معرفی محصول', blank=True)
    Image=models.ImageField(verbose_name='عکس محصول', upload_to=PathAndRename('media/Pictures/Markets/SubMarkets/Shops/Products/'), help_text='عکس محصول خود را اینجا بارگذاری کنید')
    Image_thumbnail = ImageSpecField(source='Image',
                                      processors=[ResizeToFill(180, 180)],
                                      format='JPEG',
                                      options={'quality': 60})
    Image_medium = ImageSpecField(source='Image',
                                      processors=[ResizeToFill(450, 450)],
                                      format='JPEG',
                                      options={'quality': 60})
    NewImage=models.ImageField(verbose_name='عکس جدید حجره', upload_to=PathAndRename('media/Pictures/Markets/SubMarkets/Shops/Products/'), null=True, blank=True)
    Catalog=models.FileField(verbose_name='کاتالوگ محصول', upload_to=PathAndRename('media/Catalogs/Markets/SubMarkets/Shops/Products/'), help_text='کاتالوگ محصول خود را اینجا وارد کنید', null=True, blank=True)
    FK_Shop=models.ForeignKey(Shop, null=True, on_delete=models.SET_NULL, verbose_name='حجره',related_name='ShopProduct')
    FK_Category=models.ManyToManyField(Category, verbose_name='دسته بندی های محصول', related_name='ProductCategory', blank=True)
    Price=models.BigIntegerField(verbose_name='قیمت محصول')
    OldPrice=models.BigIntegerField(verbose_name='قیمت حذف محصول', default=0)
    # Product Weight Info
    Net_Weight=models.CharField(verbose_name='وزن خالص محصول (گرم)', max_length=6, default='0')
    Weight_With_Packing=models.CharField(verbose_name='وزن محصول با بسته بندی (گرم)', max_length=6, default='0')
    # Product Dimensions Info
    Length_With_Packaging=models.CharField(verbose_name='طول محصول با بسته بندی (سانتی متر(', max_length=4, default='0')
    Width_With_Packaging=models.CharField(verbose_name='عرض محصول با بسته بندی (سانتی متر(', max_length=4, default='0')
    Height_With_Packaging=models.CharField(verbose_name='ارتفاع محصول با بسته بندی (سانتی متر(', max_length=4, default='0')
    # Product Inventory
    Inventory=models.IntegerField(verbose_name='میزان موجودی از این کالا در انبار', default=5)
    
    PostRangeType=models.CharField(verbose_name='محدوده ارسال محصولات', max_length=1, choices=POSTRANGE_TYPE, default='1', help_text='محدوده ارسال را بر اساس تایپ های مشخص شده، تعیین کنید.')
    FK_PostRange=models.ManyToManyField('PostRange', verbose_name='استان، شهرستان و شهر', related_name='Product_PostRange', blank=True)
    FK_ExceptionPostRange=models.ManyToManyField('PostRange', verbose_name='استثناء های محدوده ارسال', related_name='Poduct_PostRange_Exception', blank=True)
    FK_Points = models.ManyToManyField('UserPoint', verbose_name = 'امتیاز ها', related_name = 'User_Points', blank = True)
    FK_OptinalAttribute = models.ManyToManyField('OptinalAttribute', verbose_name = 'ویژگی های انتخابی', related_name = 'product_optional_attribute', blank = True)
    
    Status=models.CharField(verbose_name='وضعیت فروش', max_length=1, choices=PRODUCT_STATUS)
    DateCreate=models.DateTimeField(verbose_name='تاریخ بارگذاری محصول', auto_now_add=True)
    DateUpdate=models.DateTimeField(verbose_name='تاریخ بروزرسانی محصول', auto_now=True)
    
    Edite=models.BooleanField(verbose_name='وضعیت ویرایش محصول', choices=EDITE_STATUS, default=False)
    Available=models.BooleanField(verbose_name='وضعیت بارگذاری محصول', choices=AVAILABLE_STATUS, default=True)
    Publish=models.BooleanField(verbose_name='وضعیت انتشار محصول', choices=PUBLISH_STATUS, default=False)
    FK_User=models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='تایید کننده', related_name='Product_Accept', blank=True, null=True) 
    FK_Tag=models.ManyToManyField(Tag, verbose_name='تگ ها', related_name='Product_Tag', blank=True)

    @property
    def sub_market(self):
        return self.FK_SubMarket

    @property
    def image(self):
        return self.get_image()

    @property
    def description(self):
        return self.Description

    @property
    def available(self):
        return self.Available

    @property
    def publish(self):
        return self.Publish

    @property
    def old_price(self):
        return self.OldPrice

    @old_price.setter
    def old_price(self, value):
        self.OldPrice = value

    @property
    def price(self):
        return self.Price

    @price.setter
    def price(self, value):
        self.Price = value

    @property
    def slug(self):
        return self.Slug

    @property
    def title(self):
        return self.Title

    @property
    def status(self):
        return self.get_status()

    @property
    def id(self):
        return self.ID
    
    @property
    def net_weight(self):
        return self.Net_Weight

    @property
    def weight_with_packing(self):
        return self.Weight_With_Packing

    @property
    def length_with_packing(self):
        return self.Length_With_Packaging

    @property
    def width_with_packing(self):
        return self.Width_With_Packaging

    @property 
    def height_with_packaging(self):
        return self.Height_With_Packaging

    @property
    def story(self):
        return self.Story

    @property
    def post_range(self):
        return self.FK_PostRange.all()

    @property
    def exception_post_range(self):
        return self.FK_ExceptionPostRange.all()

    @property
    def image_thumbnail_url(self):
        return self.Image_thumbnail_url()

    @property
    def url(self):
        return self.get_url()

    @property
    def discount(self):
        return self.get_discounted()

    @property
    def related_products(self):
        return self.get_related_products()

    @property
    def attributes(self):
        return self.Product_Attr.all()

    @property
    def attributes_price(self):
        return self.AttrPrice_Product.all()

    @property
    def banners(self):
        return self.Product_Banner.all()

    @property
    def reviews(self):
        return self.Product_Review.all()

    @property
    def comments_count(self):
        return self.Product_Comment.count()

    @property
    def comments(self):
        return self.Product_Comment.all()

    @property
    def shop(self):
        return self.FK_Shop

    @property
    def inventory(self):
        return self.Inventory

    @property
    def average_user_point(self):
        return self.FK_Points.aggregate(average=Avg('Point'))['average']

    @property
    def total_sell(self):
        return self.Factor_Product.count()

    def __str__(self):
        return "{}".format(self.Title)

    def get_status(self):
        Status = {
            "1" : 'آماده در انبار',
            "2" : 'تولید بعد از سفارش',
            "3" : 'سفارشی سازی فروش',
            "4" : 'موجود نیست',
        }
        return Status[self.Status]

    def get_sendtype(self):
        SendType = {
            "1" : 'سراسر کشور',
            "2" : 'استانی',
            "3" : 'شهرستانی',
            "4" : 'شهری',
        }
        return SendType[self.PostRangeType]

    def get_absolute_url(self):
        return reverse("nakhll_market:ProductsDetail", kwargs={
            'shop_slug': self.FK_Shop.Slug,
            'product_slug': self.Slug,
        })

    def get_add_to_cart_url(self):
        return reverse("Payment:add-to-cart", kwargs={
            'ID': self.ID
        })

    def get_remove_from_cart_url(self):
        return reverse("Payment:remove-from-cart", kwargs={
            'ID': self.ID
        })

    def get_discounted(self):
        # Get Discounted
        try:
            return int((100 - (int(self.Price) / (int(self.OldPrice) / 100))))
        except:
            return 0

    def get_product_net_weight(self):
        # Get Net Weight
        try:
            return self.Net_Weight
        except:
            return 'نا مشخص'
    
    def get_product_weight_with_packing(self):
        # Get Weight With Packing
        try:
            return self.Weight_With_Packing
        except:
            return 'نا مشخص'

    def get_product_dimensions(self):
        # Get Dimensions
        try:
            return str(self.Length_With_Packaging) + ' * ' + str(self.Width_With_Packaging) + ' * ' + str(self.Height_With_Packaging)
        except:
            return 'نا مشخص'

    def get_product_weight_convert_to_int(self):
        # Get Product Weightn Convert To Int
        try:
            net_weight = int(self.Net_Weight)
            weight_with_packing = int(self.Weight_With_Packing)
            this_sum = 0
            if (weight_with_packing > net_weight) or (weight_with_packing == net_weight):
                this_sum += weight_with_packing
            else:
                this_sum += net_weight
            return this_sum
        except:
            return 0

    def get_product_packing_volume_convert_to_int(self):
        # Get Product Packing Volume Convert To Int
        try:
            vloume = int(self.Length_With_Packaging) * int(self.Width_With_Packaging) * int(self.Height_With_Packaging)
            this_vloume = 0
            if vloume > 3000:
                this_vloume += math.ceil(vloume / 3000) * 50
            elif vloume != 0 :
                this_vloume += 50
            return this_vloume
        except:
            return 0

    def get_total_product_weight(self):
        try:
            return self.get_product_weight_convert_to_int() + self.get_product_packing_volume_convert_to_int()
        except:
            return 0

    def check_product_post_status(self):
        # Check Product Post Status
        if (self.get_total_product_weight() > 40000) or ((int(self.Length_With_Packaging) > 100) or (int(self.Width_With_Packaging) > 100) or (int(self.Height_With_Packaging) > 100)):
            return True
        else:
            return False

    def default_image_url(self):
        return 'https://nakhll.com/media/Pictures/default.jpg'

    def get_image(self):
        try:
            return self.Image.url
        except:
            return self.defautl_image_url()

    def get_image_alt(self):
        return self.Title
        
    def Image_thumbnail_url(self):
        try:
            url = self.Image_thumbnail.url
            return url
        except:
            url ="https://nakhll.com/media/Pictures/default.jpg"
            return url

    def Image_medium_url(self):
        try:
            i = self.Image_medium.url
            url = self.Image_medium.url
            return url
        except:
            url ="https://nakhll.com/media/Pictures/default.jpg"
            return url

    def get_url(self):
        try:
            return reverse("nakhll_market:ProductsDetail", kwargs={
                'shop_slug': self.FK_Shop.Slug,
                'product_slug': self.Slug
            })
        except:
            return '/'

    def get_point(self):
        try:
            this_point = 0.0
            for item in self.FK_Points.all():
                this_point += item.Point
            return round(this_point / self.get_point_count(), 2)
        except:
            return 0.0

    def Point(self):
        return self.get_point()

    def get_point_count(self):
        return self.FK_Points.all().count()

    def get_related_products(self):
        return Product.objects\
                .filter(
                    Available = True,
                    Publish = True,
                    Status__in = ['1', '2', '3'],
                    FK_Category__in = self.FK_Category.all()
                    ).order_by('?')[:12]

    def get_product_categories(self):
        result = []
        class item_category:
            def __init__(self, item, status):
                self.Category = item
                self.Status = status
        for item in Category.objects.filter(Publish = True):
            if item in self.FK_Category.all():
                newobject = item_category(item, True)
                result.append(newobject)
            else:
                newobject = item_category(item, False)
                result.append(newobject)
        return result

    def get_product_inpostrange(self):
        result = []
        class item_postrange:
            def __init__(self, item, status):
                self.PostRange = item
                self.Status = status
        for item in PostRange.objects.all():
            if item in self.FK_PostRange.all():
                newobject = item_postrange(item, True)
                result.append(newobject)
            else:
                newobject = item_postrange(item, False)
                result.append(newobject)
        return result

    def get_product_outpostrange(self):
        result = []
        class item_postrange:
            def __init__(self, item, status):
                self.PostRange = item
                self.Status = status
        for item in PostRange.objects.all():
            if item in self.FK_ExceptionPostRange.all():
                newobject = item_postrange(item, True)
                result.append(newobject)
            else:
                newobject = item_postrange(item, False)
                result.append(newobject)
        return result

    def get_shop_slug(self):
        return self.FK_Shop.Slug

    class Meta:
        ordering = ('DateCreate','Title',)   
        verbose_name = "محصول"
        verbose_name_plural = "محصولات"

    

#----------------------------------------------------------------------------------------------------------------------------------

# AttrProduct (ویژگی محصولات) Model
class AttrProduct(models.Model):
    FK_Product=models.ForeignKey(Product, null=True, on_delete=models.SET_NULL, verbose_name='نام محصول', related_name='Product_Attr')
    FK_Attribute=models.ForeignKey(Attribute, null=True, on_delete=models.SET_NULL, verbose_name='نام ویژگی', related_name='Attribute_Product')
    Value=models.CharField(verbose_name='مقدار ویژگی', max_length=50)
    AVAILABLE_STATUS =(
        (True,'نمایش ویژگی'),
        (False,'عدم نمایش ویژگی'),
    )
    Available=models.BooleanField(verbose_name='وضعیت نمایش ویژگی محصول', choices=AVAILABLE_STATUS, default=False)
    DateCreate=models.DateTimeField(verbose_name='تاریخ ثبت ویژگی', auto_now_add=True)
    DtatUpdate=models.DateTimeField(verbose_name='تاریخ بروزرسانی ویژگی', auto_now=True)
    
    @property
    def value(self):
        return self.Value

    
    # Output Customization Based On Title
    def __str__(self):
        return "{}".format(self.Value)

    # Get Data - Attribute Title
    def get_attribute_title(self):
        return self.FK_Attribute.Title
    
    # Get Data - Attribute Unit
    def get_attribute_unit(self):
        return self.FK_Attribute.Unit

    # Ordering With DateCreate
    class Meta:
        ordering = ('id','Value',)   
        verbose_name = "مقدار ویژگی"
        verbose_name_plural = "مقدار ویژگی ها"

#----------------------------------------------------------------------------------------------------------------------------------

# AttrPrice (قیمت ویژگی) Model
class AttrPrice(models.Model):
    FK_Product=models.ForeignKey(Product, on_delete=models.SET_NULL, verbose_name='محصول', related_name='AttrPrice_Product', null=True)
    Description=models.TextField(verbose_name='درباره ویژگی', blank=True)
    Value=models.CharField(verbose_name='مقدار ویژگی', max_length=50, blank=True)
    ExtraPrice=models.CharField(verbose_name='قیمت اضافه', max_length=15, default='0', blank=True)
    Unit=models.CharField(verbose_name='واحد', max_length=50, blank=True)
    PUBLISH_STATUS =(
        (True,'منتشر شده'),
        (False,'در انتظار تایید'),
    )
    AVAILABLE_STATUS =(
        (True,'فعال'),
        (False,'غیر فعال'),
    )
    Available=models.BooleanField(verbose_name='وضعیت نمایش ارزش ویژگی محصول', choices=AVAILABLE_STATUS, default=True)
    Publish=models.BooleanField(verbose_name='وضعیت انتشار ارزش ویژگی محصول', choices=PUBLISH_STATUS, default=True)

    @property
    def description(self):
        return self.Description

    @property
    def value(self):
        return self.Value

    @property
    def extra_price(self):
        return self.ExtraPrice

    @property
    def unit(self):
        return self.Unit

    @property
    def available(self):
        return self.Available

    @property
    def publish(self):
        return self.Publish
    
    # Output Customization Based On Attribute
    def __str__(self):
        return "{}".format(self.FK_Product)

    # Ordering With DateCreate
    class Meta:
        ordering = ('id',)   
        verbose_name = "ارزش ویژگی"
        verbose_name_plural = "ارزش های ویژگی"
        
#----------------------------------------------------------------------------------------------------------------------------------

# Optinal Attribute (ویژگی های انتخابی) Model
class OptinalAttribute(models.Model):
    Title = models.CharField(verbose_name = 'عنوان ویژگی', max_length = 255)
    SELECTION_TYPE = (
        ('0','تک انتخابی'),
        ('1','چند انتخابی'),
    )
    Type = models.CharField(verbose_name = 'نوع انتخابی', max_length = 1, choices = SELECTION_TYPE)
    SELECTION_STATUS = (
        (True,'اجباری'),
        (False,'انتخابی'),
    )
    Status = models.BooleanField(verbose_name = 'وضعیت انتخاب', choices = SELECTION_STATUS, default = False)
    FK_Details = models.ManyToManyField('Details', verbose_name = 'جزئیات', related_name = 'optional_attrinute_details', blank = True)
    PUBLISH_STATUS = (
        (True,'منتشر شده'),
        (False,'در انتظار تایید'),
    )
    AVAILABLE_STATUS = (
        (True,'فعال'),
        (False,'غیر فعال'),
    )
    Available = models.BooleanField(verbose_name = 'وضعیت نمایش', choices = AVAILABLE_STATUS, default = True)
    Publish = models.BooleanField(verbose_name = 'وضعیت انتشار', choices = PUBLISH_STATUS, default = False)

    def get_details(self):
        return list(self.FK_Details.all())

    class Meta:
        ordering = ('id',)   
        verbose_name = "ویژگی انتخابی"
        verbose_name_plural = "ویژگی های انتخابی"
        
#----------------------------------------------------------------------------------------------------------------------------------

# Details (جزئیات) Model
class Details(models.Model): 
    Value = models.CharField(verbose_name = 'عنوان', max_length = 255) 
    Price = models.CharField(verbose_name = 'قیمت محصول', max_length = 15) 
    Weight = models.CharField(verbose_name='وزن محصول با بسته بندی (گرم)', max_length = 6, default = '0') 
    Length = models.CharField(verbose_name = 'طول محصول با بسته بندی (سانتی متر(', max_length = 4, default = '0') 
    Width = models.CharField(verbose_name = 'عرض محصول با بسته بندی (سانتی متر(', max_length = 4, default = '0') 
    Height = models.CharField(verbose_name = 'ارتفاع محصول با بسته بندی (سانتی متر(', max_length = 4, default = '0') 
    Inventory = models.IntegerField(verbose_name = 'موجودی', default = 0) 
    PRODUCT_STATUS = ( 
        ('1','آماده در انبار'), 
        ('2','تولید بعد از سفارش'), 
        ('3','سفارشی سازی فروش'), 
        ('4','موجود نیست'), 
    ) 
    Status = models.CharField(verbose_name = 'وضعیت محصول', max_length = 1, choices = PRODUCT_STATUS)

    def convert_to_string(self):
        str_list = []
        str_list.append('مقدار : ' + str(self.Value))
        str_list.append('قیمت : ' + str(self.Price))
        str_list.append('وزن محصول با بسته بندی : ' + str(self.Weight) + ' (گرم)')
        str_list.append('ابعاد محصول با بسته بندی : ' + str(self.Length) + ' * ' + str(self.Width) + ' * ' + str(self.Height) + ' (سانتی متر)')
        str_list.append('وضعیت محصول : ' + str(self.get_status()))
        str_list.append('موجودی محصول : ' + str(self.Inventory))
        return ' - '.join(str_list)

    def get_status(self):
        staus_type = {
            "1" : 'آماده در انبار',
            "2" : 'تولید بعد از سفارش',
            "3" : 'سفارشی سازی فروش',
            "4" : 'موجود نیست',
        }
        return staus_type[self.Status] 

    class Meta: 
        ordering = ('id',) 
        verbose_name = "جزئیات" 
        verbose_name_plural = "جزئیات ها"

#----------------------------------------------------------------------------------------------------------------------------------

# Product Banner (گالری محصول) Model
class ProductBanner (models.Model):
    FK_Product=models.ForeignKey(Product, null=True, on_delete=models.SET_NULL, verbose_name='نام محصول', related_name='Product_Banner')
    Title=models.CharField(verbose_name='برچسب روی بنر', max_length=100, null=True)
    Description=models.TextField(verbose_name='درباره بنر', max_length=350, blank=True)
    URL=models.URLField(verbose_name='لینک', help_text='لینکی که در صورت کلیک به آن منتقل می شود', blank=True)
    Image=models.ImageField(verbose_name='بنر محصول', upload_to=PathAndRename('media/Pictures/Markets/SubMarkets/Shops/Products/Banners/'), help_text='بنر محصول را اینجا وارد کنید')
    Image_medium = ImageSpecField(source='Image',
                                    processors=[ResizeToFill(450, 450)],
                                    format='JPEG',
                                    options={'quality': 60})
    NewImage=models.ImageField(verbose_name='عکس جدید حجره', upload_to=PathAndRename('media/Pictures/Markets/SubMarkets/Shops/Products/Banners/'), null=True, blank=True)
    BannerBuilder=models.CharField(verbose_name='نام تولید کننده بنر', max_length=120, blank=True)
    BannerURL=models.URLField(verbose_name='لینک تولید کننده بنر', blank=True)
    DateCreate=models.DateTimeField(verbose_name='تاریخ بارگذاری بنر محصول', auto_now_add=True)
    DateUpdate=models.DateTimeField(verbose_name='تاریخ بروزرسانی بنر محصول', auto_now=True)
    AVAILABLE_STATUS =(
        (True,'فعال'),
        (False,'غیر فعال'),
    )
    PUBLISH_STATUS =(
        (True,'منتشر شده'),
        (False,'در انتظار تایید'),
    )
    EDITE_STATUS =(
        (True,'در حال بررسی تغییرات'),
        (False,'تغییری اعمال شده است'),
    )
    Edite=models.BooleanField(verbose_name='وضعیت ویرایش بنر حجره', choices=EDITE_STATUS, default=False)
    Available=models.BooleanField(verbose_name='وضعیت بارگذاری بنر محصول', choices=AVAILABLE_STATUS, default=True)
    Publish=models.BooleanField(verbose_name='وضعیت انتشار بنر محصول', choices=PUBLISH_STATUS, default=False)
    FK_User=models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='تایید کننده', related_name='Product_Banner_Accept', blank=True, null=True) 
    FK_Tag=models.ManyToManyField(Tag, verbose_name='تگ ها', related_name='Product_Banner_Tag', blank=True)

    @property
    def image(self):
        return self.Image_thumbnail_url()
    
    def Image_thumbnail_url(self):
        try:
            i = self.Image_medium.url
            url = self.Image_medium.url
            return url
        except:
            url ="https://nakhll.com/media/Pictures/default.jpg"
            return url

    # Output Customization Based On Title
    def __str__(self):
        return "{}".format(self.Title)

    class Meta:
        ordering = ('id','Title',)   
        verbose_name = "گالری محصول"
        verbose_name_plural = "گالری محصولات "

#----------------------------------------------------------------------------------------------------------------------------------

# Product Movie (فیلم محصول) Model
class ProductMovie (models.Model):
    FK_Product=models.ForeignKey(Product, on_delete=models.SET_NULL, verbose_name='نام محصول', related_name='Product_Movie', null=True)
    Title=models.CharField(verbose_name='عنوان فیلم', max_length=100, db_index=True)
    Description=models.TextField(verbose_name='توضیخات فیلم', max_length=350, blank=True)
    URL=models.URLField(verbose_name='لینک خارجی فیلم', help_text='اگر فیلم خود را جای دیگری بارگذاری کرده اید، لینک آن را اینجا وارد کنید', blank=True)
    Video=models.FileField(verbose_name='فیلم', upload_to=PathAndRename('media/Videos/Markets/SubMarkets/Shops/Products/'), help_text='فیلم خود را اینجا وراد کنید', null=True)
    BannerBuilder=models.CharField(verbose_name='نام تولید کننده بنر', max_length=120, blank=True)
    BannerURL=models.URLField(verbose_name='لینک تولید کننده بنر', blank=True)
    DateCreate=models.DateTimeField(verbose_name='تاریخ بارگذاری فیلم محصول', auto_now_add=True)
    DtatUpdate=models.DateTimeField(verbose_name='تاریخ بروزرسانی فیلم محصول', auto_now=True)
    AVAILABLE_STATUS =(
        (True,'فعال'),
        (False,'غیر فعال'),
    )
    PUBLISH_STATUS =(
        (True,'منتشر شده'),
        (False,'در انتظار تایید'),
    )
    EDITE_STATUS =(
        (True,'در حال بررسی تغییرات'),
        (False,'تغییری اعمال شده است'),
    )
    Edit=models.BooleanField(verbose_name='وضعیت ویرایش بنر حجره', choices=EDITE_STATUS, default=False)
    Available=models.BooleanField(verbose_name='وضعیت بارگذاری فیلم محصول', choices=AVAILABLE_STATUS, default=True)
    Publish=models.BooleanField(verbose_name='وضعیت انتشار فیلم محصول', choices=PUBLISH_STATUS, default=False)
    FK_User=models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='تایید کننده', related_name='Product_Movie_Accept', blank=True, null=True) 
    FK_Tag=models.ManyToManyField(Tag, verbose_name='تگ ها', related_name='Product_Movie_Tag', blank=True)

    # Output Customization Based On Title
    def __str__(self):
        return "{}".format(self.Title)

    # Ordering With DateCreate
    class Meta:
        ordering = ('id','Title',)   
        verbose_name = "فیلم محصول"
        verbose_name_plural = "فیلم های محصول"

#----------------------------------------------------------------------------------------------------------------------------------

# Comment (نظر محصول) Model
class Comment(models.Model):
    TYPE_STATUS =(
        (False,'منفی'),
        (True,'مثبت'),
    )
    Type=models.BooleanField(verbose_name='نوع نظر', choices=TYPE_STATUS, default=True)
    FK_UserAdder=models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='کاربر', related_name='User_Comment', null=True)
    FK_Product=models.ForeignKey(Product, on_delete=models.SET_NULL, verbose_name='محصول', related_name='Product_Comment', blank=True, null=True)
    Description=models.TextField(verbose_name='توضیخات نظر')
    FK_Like=models.ManyToManyField(User, verbose_name='لایک کننده', related_name='Comment_Like', blank=True)
    FK_Pater=models.ForeignKey('self', on_delete=models.SET_NULL, verbose_name='ریپلای شده', related_name='Comment_Pater', blank=True, null=True)
    Available=models.BooleanField(verbose_name='وضعیت انتشار نظر', default=False)
    DateCreate=models.DateTimeField(verbose_name='تاریخ ثبت نظر', auto_now_add=True)
    FK_User=models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='تایید کننده', related_name='Comment_Accept', blank=True, null=True) 

    @property
    def user(self):
        return self.FK_UserAdder

    @property
    def product(self):
        return self.FK_Product

    @property
    def description(self):
        return self.Description

    @property
    def number_like(self):
        return self.FK_Like.count()

    @property
    def reply(self):
        return self.FK_Pater

    @property
    def date_create(self):
        return self.DateCreate

    @property
    def type(self):
        return self.TYPE_STATUS[self.Type][1]

    def get_type(self):
        if self.Type:
            return 'مثبت'
        else:
            return 'منفی'
        
    def get_status(self):
        if self.Available:
            return 'منتشر شده'
        else:
            return 'در حال بررسی'

    def get_like_count(self):
        return self.FK_Like.all().count()

    def get_object_name(self):
        return 'محصول ' + self.FK_Product.Title

    # Output Customization Based On User Adder, Product
    def __str__(self):
        return "{} - {}".format(self.FK_UserAdder, self.FK_Product)

    # Ordering With DateCreate
    class Meta:
        ordering = ('id',)   
        verbose_name = "نظر محصول"
        verbose_name_plural = "نظرات محصولات"

    # Get Comment Profile Image
    def get_comment_profile_image(self):
        try:
            # Get User Profile
            this_profile = get_object_or_404(Profile, FK_User = self.FK_UserAdder)
            return this_profile.Image_thumbnail_url()
        except:
            url = "https://nakhll.com/media/Pictures/avatar.png"
            return url

#----------------------------------------------------------------------------------------------------------------------------------

# ShopComment (نظر حجره) Model
class ShopComment(models.Model):
    TYPE_STATUS =(
        (True,'مثبت'),
        (False,'منفی'),
    )
    Type=models.BooleanField(verbose_name='نوع نظر', choices=TYPE_STATUS, default=True)
    FK_UserAdder=models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='کاربر', related_name='User_ShoComment', null=True)
    FK_Shop=models.ForeignKey(Shop, on_delete=models.SET_NULL, verbose_name='حجره', related_name='Shop_Comment', blank=True, null=True)
    Description=models.TextField(verbose_name='توضیخات نظر')
    FK_Like=models.ManyToManyField(User, verbose_name='لایک کننده', related_name='ShoComment_Like', blank=True)
    FK_Pater=models.ForeignKey('self', on_delete=models.SET_NULL, verbose_name='ریپلای شده', related_name='ShoComment_Pater', blank=True, null=True)
    Available=models.BooleanField(verbose_name='وضعیت انتشار نظر', default=False)
    DateCreate=models.DateTimeField(verbose_name='تاریخ ثبت نظر', auto_now_add=True)
    FK_User=models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='تایید کننده', related_name='ShoComment_Accept', blank=True, null=True) 


    def get_type(self):
        if self.Type:
            return 'مثبت'
        else:
            return 'منفی'
        
    def get_status(self):
        if self.Available:
            return 'منتشر شده'
        else:
            return 'در حال بررسی'

    def get_like_count(self):
        return self.FK_Like.all().count()

    def get_object_name(self):
        return 'حجره ' + self.FK_Shop.Title


    # Output Customization Based On User Adder, Shop
    def __str__(self):
        return "{} - {}".format(self.FK_UserAdder, self.FK_Shop)

    # Ordering With DateCreate
    class Meta:
        ordering = ('id',)   
        verbose_name = "نظر حجره"
        verbose_name_plural = "نظرات حجره"

    # Get Comment Profile Image
    def get_comment_profile_image(self):
        try:
            # Get User Profile
            this_profile = get_object_or_404(Profile, FK_User = self.FK_UserAdder)
            return this_profile.Image_thumbnail_url()
        except:
            url = "https://nakhll.com/media/Pictures/avatar.png"
            return url

#----------------------------------------------------------------------------------------------------------------------------------

# Note (نکته) Model
class Note(models.Model):
    Item=models.TextField(verbose_name='نکته')

    # Output Customization Based On Title,Date Create
    def __str__(self):
        return "{}".format(self.Item)

    # Ordering With DateCreate
    class Meta:
        ordering = ('id',)   
        verbose_name = "نکته"
        verbose_name_plural = "نکات"

#----------------------------------------------------------------------------------------------------------------------------------

# Review (نقد و بررسی) Model
class Review(models.Model):
    Title=models.CharField(verbose_name='عنوان', max_length=150, db_index=True)
    FK_PositiveNote=models.ManyToManyField(Note, verbose_name='نقاط قوت', related_name='Review_Positive_Note', blank=True)
    FK_NegativeNote=models.ManyToManyField(Note, verbose_name='نقاط ضعف', related_name='Review_Negative_Note', blank=True)
    FK_UserAdder=models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='کاربر', related_name='User_Review', null=True)
    FK_Product=models.ForeignKey(Product, on_delete=models.SET_NULL, verbose_name='محصول', related_name='Product_Review', null=True)
    Description=models.TextField(verbose_name='نفد و بررسی', blank=True)
    FK_Like=models.ManyToManyField(User, verbose_name='لایک کننده', related_name='Review_Like', blank=True)
    Available=models.BooleanField(verbose_name='وضعیت انتشار نظر', default=False)
    DateCreate=models.DateTimeField(verbose_name='تاریخ ثبت نظر', auto_now_add=True)
    FK_User=models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='تایید کننده', related_name='Review_Accept', blank=True, null=True) 

    def __str__(self):
        return "{}".format(self.Title)

    def get_user_fullname(self):
        try:
            return self.FK_UserAdder.first_name + ' ' + self.FK_UserAdder.last_name
        except:
            return None

    # Get Review Profile Image
    def get_review_profile_image(self):
        try:
            # Get User Profile
            this_profile = get_object_or_404(Profile, FK_User = self.FK_UserAdder)
            return this_profile.Image_thumbnail_url()
        except:
            url = "https://nakhll.com/media/Pictures/avatar.png"
            return url

    class Meta:
        ordering = ('id',)   
        verbose_name = "نقد و بررسی"
        verbose_name_plural = "نقد و بررسی ها "

#----------------------------------------------------------------------------------------------------------------------------------

# UserphoneValid (فعالسازی شماره) Model   
# class UserphoneValid(models.Model):
#     MobileNumber=models.CharField(verbose_name='شماره موبایل', max_length=11, unique=True)
#     ValidCode=models.CharField(verbose_name='کد فعال سازی', max_length=8, blank=True,default='80')
#     Validation=models.BooleanField(verbose_name='تایید شماره تماس', default=False)
#     Date=jmodels.jDateField(verbose_name='تاریخ', null=True, auto_now=True)
    
#     def __str__(self):
#        return "{}".format(self.MobileNumber)

#     class Meta:
#         ordering = ('Date',)   
#         verbose_name = "فعالسازی شماره"
#         verbose_name_plural = "فعالسازی شماره"

#----------------------------------------------------------------------------------------------------------------------------------

# Profile (پروفایل) Model
class Profile(models.Model):
    objects = ProfileManager()
    ID=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    FK_User=models.OneToOneField(User, on_delete=models.SET_NULL, verbose_name='کاربر', related_name='User_Profile', null=True)
    SEX_STATUS =(
        ('0','انتخاب جنسیت'),
        ('1','زن'),
        ('2','مرد'),
        ('3','سایر'),
    )
    Sex=models.CharField(verbose_name='جنسیت', max_length=1, choices=SEX_STATUS, default='0')
    CountrPreCode=models.CharField(verbose_name='کد کشور', max_length=6, default='098')
    MobileNumber=models.CharField(verbose_name='شماره موبایل', max_length=11, unique=True)
    ZipCode=models.CharField(verbose_name='کد پستی', max_length=10, blank=True)
    NationalCode=models.CharField(verbose_name='کد ملی', max_length=10, unique=True, blank=True, null=True)
    Address=models.TextField(verbose_name='آدرس', blank=True)
    State =models.CharField(verbose_name='استان', max_length=50, blank=True)
    BigCity=models.CharField(verbose_name='شهرستان', max_length=50, blank=True)
    City=models.CharField(verbose_name='شهر', max_length=50, blank=True)
    Location=models.CharField(verbose_name='موقعیت مکانی', max_length=150, blank=True, help_text='طول و عرض جغرافیایی')
    BrithDay=jmodels.jDateField(verbose_name='تاریخ تولد', null=True)
    FaxNumber=models.CharField(verbose_name='شماره فکس', max_length=8, blank=True)
    CityPerCode=models.CharField(verbose_name='پیش شماره', max_length=6, blank=True, default='034')
    PhoneNumber=models.CharField(verbose_name='شماره تلفن ثابت', max_length=8, blank=True)
    Bio=models.CharField(verbose_name='درباره من', max_length=250, blank=True)
    Image=models.ImageField(verbose_name='پروفایل', upload_to=PathAndRename('media/Pictures/Profile/'), null=True, default='static/Pictures/DefaultProfile.png')
    Image_thumbnail = ImageSpecField(source='Image',
                                processors=[ResizeToFill(175, 175)],
                                format='JPEG',
                                options={'quality': 60} )
    ImageNationalCard = models.ImageField(verbose_name="عکس کارت ملی", upload_to=PathAndRename('media/Pictures/NationalCard/'), null=True, blank=True)
    UserReferenceCode=models.CharField(verbose_name='کد شما', max_length=6, unique=True, default=BuildReferenceCode(6))
    Point=models.PositiveIntegerField(verbose_name='امتیاز کاربر', default=0)
    TUTORIALWEB_TYPE =(
        ('0','موتور های جستجو'),
        ('1','حجره داران'),
        ('2','شبکه های اجتماعی'),
        ('3','کاربران'),
        ('4','رسانه ها'),
        ('5','تبلیغات'),
        ('6','NOD'),
        ('7','سایر'),
        ('8','هیچ کدام'),
    )
    TutorialWebsite=models.CharField(verbose_name='نحوه آشنایی با سایت', max_length=1, choices=TUTORIALWEB_TYPE, blank=True, default='8')
    ReferenceCode=models.CharField(verbose_name='کد معرف', max_length=6, blank=True)
    IPAddress=models.CharField(verbose_name='آدرس ای پی', max_length=15, blank=True)

    # Output Customization Based On UserName (ID)
    def __str__(self):
       return "{} ({})".format(self.FK_User, self.ID)

    def Image_thumbnail_url(self):
        try:
            i = self.Image_thumbnail.url
            url = self.Image_thumbnail.url
            return url
        except:
            url = "https://nakhll.com/media/Pictures/avatar.png"
            return url

    def image_national_card_url(self):
        try:
            i = self.ImageNationalCard.url
            url = self.ImageNationalCard.url
            return url
        except:
            url = "https://nakhll.com/static-django/images/image_upload.jpg"
            return url

    # Get User Bank Account Info
    def get_bank_account_name(self):
        if BankAccount.objects.filter(FK_Profile = self).exists():
            return BankAccount.objects.get(FK_Profile = self).AccountOwner
        else:
            return None

    def get_credit_card_number(self):
        if BankAccount.objects.filter(FK_Profile = self).exists():
            return BankAccount.objects.get(FK_Profile = self).CreditCardNumber
        else:
            return None


    def get_shaba_number(self):
        if BankAccount.objects.filter(FK_Profile = self).exists():
            return BankAccount.objects.get(FK_Profile = self).ShabaBankNumber
        else:
            return None

    def chack_user_bank_account(self):
        if (self.get_bank_account_name() == None) or (self.get_credit_card_number() == None) or (self.get_shaba_number() == None):
            return True
        else:
            return False


    def is_user_shoper(self):
        if Shop.objects.filter(FK_ShopManager = self.FK_User).exists():
            return True
        else:
            return False

    
    def get_user_shops(self):
        return Shop.objects.filter(FK_ShopManager = self.FK_User, Publish = True)


    def get_user_products(self):
        return Product.objects.filter(FK_Shop__in = self.get_user_shops(), Publish = True)

    def get_state_name(self):
        try:
            return State.objects.get(id=self.State).name
        except:
            return None
    
    def get_bigcity_name(self):
        try:
            return BigCity.objects.get(id=self.BigCity).name
        except:
            return None

    def get_city_name(self):
        try:
            return City.objects.get(id=self.City).name
        except:
            return None
    # Ordering With DateCreate
    class Meta:
        ordering = ('ID',)   
        verbose_name = "پروفایل"
        verbose_name_plural = "پروفایل ها "

#----------------------------------------------------------------------------------------------------------------------------------

# Survey (نظرسنجی) Model
class Survey(models.Model):
    Question=models.TextField(verbose_name='سوال')
    Point=models.PositiveIntegerField(verbose_name='امتیاز')
    Weight=models.PositiveSmallIntegerField(verbose_name='وزن')
    FK_User=models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='ثبت کننده', related_name='User_Add', null=True) 

    # Output Customization Based On Question
    def __str__(self):
        return "{}".format(self.Question)

    # Ordering With DateCreate
    class Meta:
        ordering = ('id',)   
        verbose_name = "نظرسنجی"
        verbose_name_plural = "نظرسنجی ها"

#----------------------------------------------------------------------------------------------------------------------------------

# Polling (نظرسنجی کردن) Model
class Polling(models.Model):
    FK_Survey=models.ManyToManyField(Survey, verbose_name='سوال', related_name='Polling_Question', blank=True)
    FK_User=models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='کاربر', related_name='Polling_User', null=True)
    FK_Product=models.ForeignKey(Product, on_delete=models.SET_NULL, verbose_name='محصول', related_name='Polling_Product', blank=True, null=True)
    FK_Shop=models.ForeignKey(Shop, on_delete=models.SET_NULL, verbose_name='حجره', related_name='Polling_Shop', blank=True, null=True)
    Status=models.BooleanField(verbose_name='وضعیت')

    # Output Customization Based On Question
    def __str__(self):
        return "{} - {}".format(self.FK_User, self.FK_Product)

    # Ordering With DateCreate
    class Meta:
        ordering = ('id',)   
        verbose_name = "نتیجه نظرسنجی"
        verbose_name_plural = "نتیجه نظرسنجی ها"

#----------------------------------------------------------------------------------------------------------------------------------

# Slider (اسلایدر) Model
class Slider(models.Model):
    FK_Creator=models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='ثبت کننده', related_name='Slider_Create', null=True) 
    Title=models.CharField(verbose_name='برچسب روی اسلایدر', max_length=100, db_index=True)
    Description=models.TextField(verbose_name='درباره اسلایدر', max_length=350, blank=True)
    ShowInfo=models.BooleanField(verbose_name='وضعیت نمایش اطلاعات اسلایدر', default=True, help_text='اگر می خواهید عنوان و توضیحات بنر روی آن نمایش داده شود، این گزینه را فعال کنید.')
    URL=models.URLField(verbose_name='لینک', help_text='لینکی که در صورت کلیک به آن منتقل می شود', blank= True)
    Image=models.ImageField(verbose_name='عکس اسلایدر', upload_to=PathAndRename('media/Pictures/Sliders/'), help_text='اسلایدر را اینجا وارد کنید')
    Location=models.IntegerField(verbose_name='مکان اسلایدر')
    DateCreate=models.DateTimeField(verbose_name='تاریخ بارگذاری اسلایدر', auto_now_add=True)
    DtatUpdate=models.DateTimeField(verbose_name='تاریخ بروزرسانی اسلایدر', auto_now=True)
    
    AVAILABLE_STATUS =(
        (True,'فعال'),
        (False,'غیر فعال'),
    )
    PUBLISH_STATUS =(
        (True,'منتشر شده'),
        (False,'در انتظار تایید'),
    )
    Available=models.BooleanField(verbose_name='وضعیت بارگذاری فیلم محصول', choices=AVAILABLE_STATUS, default=True)
    Publish=models.BooleanField(verbose_name='وضعیت انتشار فیلم محصول', choices=PUBLISH_STATUS, default=False)
    FK_User=models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='تایید کننده', related_name='Slider_Accept', blank=True, null=True) 
    BannerBuilder=models.CharField(verbose_name='نام تولید کننده بنر', max_length=120, blank=True)
    BannerURL=models.URLField(verbose_name='لینک تولید کننده بنر', blank=True)
    
    @property
    def url(self):
        return self.URL

    @property
    def image(self):
        return self.get_image() 

    @property
    def title(self):
        return self.Title

    @property
    def show_info(self):
        return self.ShowInfo

    @property
    def description(self):
        return self.Description

    @property
    def location(self):
        return self.Location

    def get_image(self):
        try:
            return self.Image.url
        except:
            return None

    # Output Customization Based On Title
    def __str__(self):
        return "{}".format(self.Title)

    # Ordering With id
    class Meta:
        ordering = ('id',)   
        verbose_name = "اسلایدر"
        verbose_name_plural = "اسلایدر ها"
    
#----------------------------------------------------------------------------------------------------------------------------------

# Option_Meta (آپشن) Model
class Option_Meta(models.Model):
    """ used to create nav bar items and main menu items """
    Title=models.CharField(verbose_name='عنوان', db_index=True, max_length=500)
    Description=models.TextField(verbose_name='توضیحات', blank=True)
    Value_1=models.CharField(verbose_name='مقدار - اول', max_length=500)
    Value_2=models.CharField(verbose_name='مقدار - دوم', max_length=500, blank=True)

    # Output Customization Based On Title
    def __str__(self):
        return "{}".format(self.Title)

    # Ordering With id
    class Meta:
        ordering = ('id',)   
        verbose_name = "آپشن"
        verbose_name_plural = "آپشن ها"

#----------------------------------------------------------------------------------------------------------------------------------

# User_Message_Status (وضعیت-پیام-کاربر) Model
class User_Message_Status(models.Model):
    FK_User=models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='کاربر', null=True)
    SEEN_STATUS =(
        (True,'دیده شده'),
        (False,'دیده نشده'),
    )
    SeenStatus=models.BooleanField(verbose_name='وضعیت بازدید', choices=SEEN_STATUS, default=False)

    # Output Customization Based On User
    def __str__(self):
        if self.SeenStatus:
            return "{} - (دیده شده)".format(self.FK_User)
        else:
            return "{} - (دیده نشده)".format(self.FK_User)

    # Ordering With DateCreate
    class Meta:
        ordering = ('id',)
        verbose_name = "وضعیت پیام کاربر"
        verbose_name_plural = "وضعیت پیام کاربران"

#----------------------------------------------------------------------------------------------------------------------------------

# Message (پیام) Model
class Message(models.Model):
    Title=models.CharField(verbose_name='عنوان', db_index=True, max_length=250)
    Text=models.TextField(verbose_name='متن')
    FK_Users=models.ManyToManyField(User_Message_Status, verbose_name='کاربران', related_name='Message_User')
    FK_Sender=models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='ارسال کننده', related_name='Message_Sender', null=True)
    Date=models.DateField(verbose_name='تاریخ ثبت', auto_now_add=True)
    MESSAGE_STATUS =(
        (True,'در حال نمایش'),
        (False,'عدم نمایش'),
    )
    Type=models.BooleanField(verbose_name='وضعیت نمایش', choices=MESSAGE_STATUS, default=True)

    # Output Customization Based On User
    def __str__(self):
        return "{} ({})".format(self.Title, self.Date)

    # Ordering With DateCreate
    class Meta:
        ordering = ('id',)
        verbose_name = "اعلان"
        verbose_name_plural = "اعلان ها"

#----------------------------------------------------------------------------------------------------------------------------------

# Pages (برگه ها) Model
class Pages(models.Model):
    Title=models.CharField(verbose_name='عنوان', max_length=150)
    Slug=models.SlugField(verbose_name='شناسه صفحه', unique=True, db_index=True)
    Content=HTMLField(verbose_name='محتوا صفحه')
    DateCreate=models.DateTimeField(verbose_name='تاریخ انتشار صفحه', auto_now_add=True)
    DtatUpdate=models.DateTimeField(verbose_name='تاریخ بروزرسانی صفحه', auto_now=True)
    PUBLISH_STATUS =(
        (True,'منتشر شده'),
        (False,'پیش نویس'),
    )
    Publish=models.BooleanField(verbose_name='وضعیت انتشار', choices=PUBLISH_STATUS, default=True)
    FK_User=models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='منتشر کننده', related_name='User_Published_Page', blank=True, null=True) 

    # Output Customization Based On UserName (ID)
    def __str__(self):
       return "{}".format(self.Title)

    # Ordering With DateCreate
    class Meta:
        ordering = ('id',)   
        verbose_name = "برگه"
        verbose_name_plural = "برگه ها"

#----------------------------------------------------------------------------------------------------------------------------------

# Field (فیلد) Model
class Field(models.Model):
    Title=models.CharField(verbose_name='عنوان', max_length=150)
    Value=models.TextField(verbose_name='مقدار', blank=True)

    # Output Customization Based On Title : Value
    def __str__(self):
       return "{} : {}".format(self.Title, self.Value)

    # Ordering With id
    class Meta:
        ordering = ('id',)   
        verbose_name = "فیلد"
        verbose_name_plural = "فیلد ها"

#----------------------------------------------------------------------------------------------------------------------------------

# Alert (هشدار ها) Model
class Alert(models.Model):
    FK_User=models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='ثبت کننده', related_name='User_Registrar_Alert', blank=True, null=True) 
    PART_TYPE =(
        ('0','ایجاد پروفایل'),
        ('1','ویرایش پروفایل'),
        ('2','ایجاد حجره'),
        ('3','ویرایش حجره'),
        ('4','ایجاد بنر حجره'),
        ('5','ویرایش بنر حجره'),
        ('6','ایجاد محصول'),
        ('7','ویرایش محصول'),
        ('8','ایجاد بنر محصول'),
        ('9','ویرایش بنر محصول'),
        ('10','ایجاد ویژگی جدید'),
        ('11','ثبت ویژگی جدید برای محصول'),
        ('12','ثبت سفارش'),
        ('13','لغو سفارش'),
        ('14','ثبت کامنت جدید'),
        ('15','ثبت نقد و بررسی جدید'),
        ('16','ثبت تیکت جدید'),
        ('17','ایجاد ارزش ویژگی جدید'),
        ('18','ثبت انتقاد و پیشنهاد یا شکایت'),
        ('19','لغو صورت حساب'),
        ('20','تایید سفارش'),
        ('21','ارسال سفارش'),
        ('22','حذف بنر حجره'),
        ('23','حذف بنر محصول'),
        ('24','حذف ویژگی محصول'),
        ('25','حذف ارزش ویژگی'),
        ('26', 'ایجاد کوپن'),
        ('27', 'حذف کوپن'),
        ('28', 'ثبت کامنت پست'),
        ('29', 'ثبت کامنت داستان'),
        ('30', 'ثبت کامنت حجره'),
        ('31', 'درخواست تسویه'),
        ('32', 'ثبت ویژگی انتخابی جدید'),
        ('33', 'حذف ویژگی انتخابی'),
    )
    Part=models.CharField(verbose_name='بخش', choices=PART_TYPE, max_length=2, default='0')
    Slug=models.TextField(verbose_name='شناسه بخش', blank=True, null=True)
    FK_Field=models.ManyToManyField(Field, verbose_name='فیلد ها', related_name='Alert_Fields', blank=True)
    SEEN_STATUS =(
        (True,'دیده شده'),
        (False,'دیده نشده'),
    )
    Seen=models.BooleanField(verbose_name='وضعیت بازدید', choices=SEEN_STATUS, default=False)
    STATUS =(
        (True,'ثبت تغییرات'),
        (False,'عدم ثبت تغییرات'),
    )
    Status=models.BooleanField(verbose_name='وضعیت تغییرات', choices=STATUS, null=True)
    DateCreate=models.DateTimeField(verbose_name='تاریخ ثبت هشدار', auto_now_add=True)
    DateUpdate=models.DateTimeField(verbose_name='تاریخ ثبت تغییرات', auto_now=True)
    Description=models.TextField(verbose_name='توضیحات', blank=True, help_text='در صورت عدم پذیرش تغییرات انجام شده، لطفا دلایل خودت را اینجا وارد نمایید.')
    FK_Staff=models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='ثبت کننده', related_name='Alert_User_Published', blank=True, null=True) 

    def __str__(self):
       return "{} - {}".format(self.FK_User, self.FK_Staff)

    def get_part_display(self):
        if self.Part == '31':
            return 'درخواست تسویه'

    class Meta:
        ordering = ('id',)   
        verbose_name = "هشدار"
        verbose_name_plural = "هشدار ها"

#----------------------------------------------------------------------------------------------------------------------------------

# Point (امتیاز) Model
class UserPoint (models.Model):
    FK_User = models.ForeignKey(User, verbose_name = 'امتیاز دهنده', related_name = 'point_user', on_delete = models.SET_NULL, null = True)
    Point = models.PositiveSmallIntegerField(verbose_name = 'امتیاز', default = 0)
    Date = models.DateField(verbose_name='تاریخ', auto_now_add = True) 

    def __str__(self):
        return "{} - {} - ({})".format(self.FK_User, self.Point, self.Date)

    class Meta:
        ordering = ('id',)   
        verbose_name = "امتیاز"
        verbose_name_plural = "امتیاز ها"
        
#----------------------------------------------------------------------------------------------------------------------------------
class AmazingProductManager(models.Manager):
    def get_amazing_products(self):
        queryset = self.get_queryset()
        now = timezone.now()
        return queryset.filter(
            start_date__lte=now,
            end_date__gte=now
            )

class AmazingProduct(models.Model):
    objects = AmazingProductManager()
    product = models.ForeignKey(
        Product,
        verbose_name='محصول شگفت انگیز',
        on_delete=models.SET_NULL,
        null=True,
        related_name='amazing_product',
        )
    start_date = models.DateTimeField(verbose_name='تاریخ شروع')
    end_date = models.DateTimeField(verbose_name='تاریخ پایان')

    @property
    def start_date_field(self):
        return self.start_date

    @property
    def end_date_field(self):
        return self.end_date

    class Meta:
        ordering = ('id',)   
        verbose_name = "شگفت انگیز"
        verbose_name_plural = "شگفت انگیزان"

    def __str__(self):
        return self.product.Title

#----------------------------------------------------------------------------------------------------------------------------------

# State استان
class State(models.Model):
    name = models.CharField(verbose_name='نام استان', max_length=127)
    code = models.IntegerField(verbose_name='کد استان')
    
    class Meta:
        ordering = ('id',)   
        verbose_name = "استان"
        verbose_name_plural = "استان ها"
    
    def get_bigcities_of_state(self):
        return self.big_city.all()
    
    def get_bigcities_of_state_id_name(self):
        return self.get_bigcities_of_state().values('name', 'id')

# ‌BigCity شهرستان
class BigCity(models.Model):
    name = models.CharField(verbose_name='نام شهرستان', max_length=127)
    code = models.IntegerField(verbose_name='کد شهرستان')
    state = models.ForeignKey(State, related_name='big_city', on_delete=models.CASCADE)

    class Meta:
        ordering = ('id',)   
        verbose_name = "شهرستان"
        verbose_name_plural = "شهرستان ها"

    def get_cities_of_bigcities(self):
        return self.city.all()

    def get_cities_of_bigcities_id_name(self):
        return self.get_cities_of_bigcities().values('id', 'name')

        
# ‌City شهر
class City(models.Model):
    name = models.CharField(verbose_name='نام شهر', max_length=127)
    code = models.IntegerField(verbose_name='کد شهر')
    big_city = models.ForeignKey(BigCity, related_name='city', on_delete=models.CASCADE)

    class Meta:
        ordering = ('id',)   
        verbose_name = "شهر"
        verbose_name_plural = "شهر ها"