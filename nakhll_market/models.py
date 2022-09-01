from __future__ import unicode_literals
from shop import models as shop_models
import os
from functools import cached_property
import datetime
import math
import uuid
import random
import string
import os
from django.http import Http404
from django.db import models
from django.db.models import F, Q, Count, UniqueConstraint, CheckConstraint
from django.db.models.fields import FloatField
from django.db.models.functions import Cast
from django.db.models.aggregates import Avg, Sum
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.core import serializers
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils import timezone
from django.utils.deconstruct import deconstructible
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import reverse, get_object_or_404
from django_jalali.db import models as jmodels
from django.dispatch import receiver
import jdatetime
from colorfield.fields import ColorField
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from simple_history.models import HistoricalRecords
from nakhll_market.constants import ACTIVE_REFERRAL, EXPIRED_REFERRAL, FIRST_TIME_REFERRAL
from nakhll_market.interface import AlertInterface
from nakhll.utils import datetime2jalali
from refer.constants import REFERRAL_LINK_DURATION


OUTOFSTOCK_LIMIT_NUM = 5


def attach_domain(url):
    """Get domain name from :attr:`nakhll.settings.DOMAIN_NAME` and attach it to url"""
    domain = settings.DOMAIN_NAME
    # Cut domain trailing slash
    domain = domain if domain[-1] != '/' else domain[:-1]
    return domain + url


# Rename Method
@deconstructible
class PathAndRename():
    def __init__(self, sub_path):
        self.path = sub_path

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        rand_strings = ''.join(random.choice(
            string.ascii_letters + string.digits)
            for i in range(6))
        filename = '{}.{}'.format(rand_strings, ext)

        return os.path.join(self.path, filename)


# Random Referense Code
@deconstructible
class build_refer_code():
    def __init__(self, Code_Size):
        self.size = Code_Size

    def __call__(self):
        # it's possible generated code is already in db
        # we can check it by querying db
        random_str = ''.join(
            random.choice(string.ascii_lowercase + string.digits)
            for i in range(self.size))

        return (random_str)


# Fix Image Roting
def upload_path(instance, filename):
    return '{0}/{1}'.format("disforum", filename)


class CategoryManager(models.Manager):
    """Manager class for Category model"""

    def available_category(self):
        """Return all categories that are available for use"""
        queryset = self.get_queryset()
        return queryset.filter(available=True)

    def all_childs(self, category):
        """Get a category object and return all its childs as a flat list

        This is a recursive function without any treshold or limitation to stop recursion. So if you have a category 
        with a lot of childs, it may take a long time to return all childs.
        """
        childs = []
        for child in category.get_sub_category():
            childs.append(child)
            childs.extend(self.all_childs(child))
        return childs

    def parents_to_root(self, category):
        """Return all parents of a category till the root as a flat list

        This is a recursive function without any treshold or limitation to stop recursion. So if you have a category
        that is deep in the tree, it may take a long time to return all parents.
        """
        if category.parent is None:
            return [category]
        else:
            return self.parents_to_root(category.parent) + [category]

    def get_root_categories(self):
        """Return all root categories that are available"""
        return self.available_category().filter(parent=None).order_by('order')

    def categories_with_product_count(self, query=None, shop=None):
        """Return all categories with the number of products in each one

        Args:
            query (str, optional): Search in products which query is in their Title. None means no search.
            shop (Shop, optional): Shop to filter products. None means no filter on shop.

        Returns:
            QuerySet (Category): All categories with the number of products in each one
        """
        filter_query = Q()
        if query:
            filter_query &= Q(products__Title__contains=query)
            filter_query &= Q(products__Publish=True)
            filter_query &= Q(products__FK_Shop__isnull=False)
        if shop:
            filter_query &= Q(products__FK_Shop__Slug=shop)

        queryset = self.annotate(
            products_count=Count(
                'products',
                filter=filter_query))
        return queryset.filter(products_count__gt=0).order_by('-products_count')

    def all_subcategories(self, categories):
        """Get a category object and return all its childs as a flat list

        This is a recursive function without any treshold or limitation to stop recursion. So if you have a category 
        with a lot of childs, it may take a long time to return all childs.
        """
        subcategories = []
        for category in categories:
            subcategories.append(category)
            subcategories.extend(
                self.all_subcategories(
                    category.childrens.all()))
        return subcategories

    def all_ordered(self):
        """Return all available categories ordered by their order field"""
        return self.available_category().order_by('order')


class Category(models.Model):
    """Category model for products

    Attributes:
        name (str): Name of the category
        slug (str): Slug of the category
        parent (Category, optional): Parent category of this category. None means this category is a root category
        description (str, optional): Description of the category
        image (ImageField, optional): Image of the category
        image_thumbnail (ImageField, optional): Thumbnail of the category image
        available = (bool): If this category is available for use or not. Default is True
        market_uuid (str, optional): 
        submarket_uuid (str, optional):
        order (int): Order of the category in the list of categories
    """
    class Meta:
        verbose_name = "دسته بندی"
        verbose_name_plural = "دسته بندی ها"

    name = models.CharField(verbose_name='عنوان دسته بندی', max_length=150)
    slug = models.SlugField(
        verbose_name='شناسه دسته بندی',
        unique=True,
        db_index=True)
    description = models.TextField(verbose_name='درباره دسته بندی', blank=True)
    image = models.ImageField(
        verbose_name='عکس دسته بندی',
        upload_to=PathAndRename('media/Pictures/Categories/'),
        help_text='عکس دسته بندی را اینجا وارد کنید',
        blank=True,
        null=True)
    image_thumbnail = ImageSpecField(source='image',
                                     processors=[ResizeToFill(175, 175)],
                                     format='JPEG',
                                     options={'quality': 60})
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        verbose_name='پدر',
        blank=True,
        null=True,
        related_name='childrens')
    available = models.BooleanField(verbose_name='فعال', default=True)
    created_at = models.DateTimeField(
        verbose_name='تاریخ ایجاد', auto_now_add=True)
    updated_at = models.DateTimeField(
        verbose_name='تاریخ بروزرسانی', auto_now=True)
    market_uuid = models.UUIDField(
        verbose_name='شناسه بازار',
        null=True,
        editable=False)
    submarket_uuid = models.UUIDField(
        verbose_name='شناسه بازارچه',
        null=True,
        editable=False)
    order = models.PositiveIntegerField(verbose_name='ترتیب', default=99999)
    objects = CategoryManager()

    def __str__(self):
        return "{}".format(self.name)


# ----------------------------------------------------------------------------------------------------------------------------------

class ShopManager(models.Manager):
    """Manager for the Shop model"""
    FEW_HOURS_AGO = timezone.make_aware(
        datetime.datetime.now() -
        datetime.timedelta(
            hours=15))

    def shop_managers_info(self):
        """Get informations of all shop managers"""
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
        """Get informations of all shop managers for marketing team"""
        queryset = self.get_queryset()
        return queryset.values(
            'FK_ShopManager__first_name',
            'FK_ShopManager__last_name',
            'FK_ShopManager__User_Profile__MobileNumber',
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

        # Exclude the ones that have been created less than 15 Hours ago
        # Exclude Shops that have default Image
        return queryset .filter(Q(Publish=True), Q(Available=True), Q(DateCreate__lt=self.FEW_HOURS_AGO), Q(ShopProduct__Factor_Product__Factor_Products__OrderDate__gte=one_week_ago), ~Q(
            Image='static/Pictures/DefaultShop.png')) .annotate(number_sale=Sum('ShopProduct__Factor_Product__ProductCount')) .order_by('-number_sale')[:5]

    def get_random_shops(self):
        """Get 12 random shops from the database, excluding the ones that have been created less than 15 Hours ago"""
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
            WHERE ("nakhll_market_shop"."Available" AND "nakhll_market_shop"."Publish"
                    AND "nakhll_market_shop"."DateCreate" > now() - '15 hours'::INTERVAL)
            GROUP BY "nakhll_market_shop"."ID"
            HAVING COUNT("nakhll_market_product"."ID") > 1
            ORDER BY RANDOM()
            LIMIT 12
        '''
        # METHOD A:
        # return Shop.objects.raw(sql)

        # METHOD B:
        # shops = Shop.objects.filter(Publish=True, Available=True, ShopProduct__gt=1, DateCreate__lt=self.FEW_HOURS_AGO).order_by('?')[:12]

        # METHOD C:

        # METHOD D:
        shop_ids = Shop.objects.filter(Q(Publish=True), Q(Available=True), Q(ShopProduct__gt=1),
                                       # Exclude the ones that have been created
                                       # less than 15 Hours ago
                                       Q(DateCreate__lt=self.FEW_HOURS_AGO),
                                       # Exclude Shops that have default Image
                                       ~Q(Image='static/Pictures/DefaultShop.png')).values_list('ID', flat=True)
        random_id_list = random.sample(list(shop_ids), 12)
        shops = Shop.objects.filter(ID__in=random_id_list)
        return shops

    def public_shops(self):
        """Return all the public shops"""
        return self.filter(Publish=True, Available=True)


# Shop (حجره) Model
class Shop(models.Model):
    """Shop model in Nakhll

    Attributes:
        ID (AutoField): primary key of shop model - UUID field
        FK_ShopManager (ForeignKey): Foreign key to the User model, who is the owner of this shop
        Title (CharField): Title of the shop
        Slug (SlugField): Slug of the shop
        Description (TextField): Description of the shop
        Image (ImageField): Image of the shop
        Image_thumbnail (ImageField): Thumbnail of the shop
        NewImage (ImageField): DEPRECATED, Previously used in django template system
        ColorCode (CharField): Color code of the shop
        Bio (TextField): Bio of the shop
        state_old (CharField): DEPRECATED, Old state of the shop in char mode
        big_city_old (CharField): DEPRECATED, Old big city of the shop in char mode
        city_old (CharField): DEPRECATED, Old city of the shop in char mode
        State (CharField): State of the shop, foreign key to the State model
        BigCity (CharField): Big city of the shop, foreign key to the BigCity model
        City (CharField): City of the shop, foreign key to the City model
        Location (CharField): DEPRECATED
        Point (PointField): DEPRECATED
        Holidays (CharField): DEPRECATED
        DateCreate (DateTimeField): Date of creation of the shop
        DateUpdate (DateTimeField): Date of update of the shop
        in_campaign (BooleanField): If the shop is in campaign or not, Marketing team can use this field to group some shops for their plans
        Edite (BooleanField): DEPRECATED
        Available (BooleanField): If the shop is available or not. This field is editable by the shop owner
        Publish (BooleanField): If the shop is publish or not. This field is editable by the staff
        FK_User (ForeignKey): Foreign key to the User model who is the creator or editor of the shop
        CanselCount (IntegerField): DEPRECATED
        CanselFirstDate (DateTimeField): DEPRECATED
        LimitCancellationDate (DateTimeField): DEPRECATED
        documents (FileField):
        show_contact_info (BooleanField): If we allow to show the contact info of the shop to buyer or not
        is_landing (BooleanField): If the shop has landing page or not
        has_product_group_add_edit_permission (BooleanField): If the shop has permission to create or edit products using bulk system or not
    """
    objects = ShopManager()
    ID = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True)
    FK_ShopManager = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name='حجره دار',
        related_name='ShopManager')
    Title = models.CharField(
        max_length=100,
        verbose_name='عنوان حجره',
        db_index=True,
        unique=True)
    Slug = models.SlugField(
        verbose_name='شناسه حجره',
        unique=True,
        db_index=True,
        allow_unicode=True)
    Description = models.TextField(verbose_name='درباره حجره', blank=True)
    Image = models.ImageField(
        verbose_name='عکس حجره',
        upload_to=PathAndRename('media/Pictures/Markets/SubMarkets/Shops/'),
        help_text='عکس حجره را اینجا وارد کنید',
        default='static/Pictures/DefaultShop.png', null=True)
    Image_thumbnail = ImageSpecField(source='Image',
                                     processors=[ResizeToFill(175, 175)],
                                     format='JPEG',
                                     options={'quality': 60})
    NewImage = models.ImageField(
        verbose_name='عکس جدید حجره',
        upload_to=PathAndRename('media/Pictures/Markets/SubMarkets/Shops/'),
        null=True, blank=True)
    ColorCode = models.CharField(
        max_length=9, verbose_name='کد رنگ',
        help_text='رنگ حجره را اینجا وارد کنید', blank=True)
    Bio = models.TextField(verbose_name='معرفی حجره دار', blank=True)
    # these are only for backup purposes
    state_old = models.CharField(
        max_length=50,
        blank=True)
    big_city_old = models.CharField(
        max_length=50,
        blank=True)
    city_old = models.CharField(max_length=50, blank=True)
    State = models.ForeignKey(
        'State',
        on_delete=models.PROTECT,
        verbose_name='استان',
        blank=True,
        null=True)
    BigCity = models.ForeignKey(
        'BigCity',
        on_delete=models.PROTECT,
        verbose_name='شهرستان',
        blank=True,
        null=True)
    City = models.ForeignKey(
        'City',
        on_delete=models.PROTECT,
        verbose_name='شهر',
        blank=True,
        null=True)
    Location = models.CharField(
        verbose_name='موقعیت مکانی',
        max_length=150,
        blank=True,
        help_text='طول و عرض جغرافیایی')
    Point = models.PositiveIntegerField(verbose_name='امتیاز حجره', default=0)
    Holidays = models.CharField(
        verbose_name='روز های تعطیلی حجره',
        max_length=15,
        blank=True)
    DateCreate = models.DateTimeField(
        verbose_name='تاریخ ثبت حجره',
        auto_now_add=True)
    DateUpdate = models.DateTimeField(
        verbose_name='تاریخ بروزرسانی حجره', auto_now=True)
    in_campaign = models.BooleanField(verbose_name='در کمپین؟', default=False)
    # محدودیت های حجره
    AVAILABLE_STATUS = (
        (True, 'فعال'),
        (False, 'غیر فعال'),
    )
    PUBLISH_STATUS = (
        (True, 'منتشر شده'),
        (False, 'در انتظار تایید'),
    )
    EDITE_STATUS = (
        (True, 'در حال بررسی تغییرات'),
        (False, 'تغییری اعمال شده است'),
    )
    Edite = models.BooleanField(
        verbose_name='وضعیت ویرایش حجره',
        choices=EDITE_STATUS,
        default=False)
    Available = models.BooleanField(
        verbose_name='وضعیت ثبت حجره',
        choices=AVAILABLE_STATUS,
        default=True)
    Publish = models.BooleanField(
        verbose_name='وضعیت انتشار حجره',
        choices=PUBLISH_STATUS,
        default=False)
    FK_User = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        verbose_name='تایید کننده',
        related_name='Shop_Accept',
        blank=True,
        null=True)
    CanselCount = models.PositiveIntegerField(
        verbose_name='تعداد لغو سفارشات حجره', default=0)
    CanselFirstDate = models.DateField(
        verbose_name='تاریخ اولین لغو سفارش', null=True, blank=True)
    LimitCancellationDate = models.DateField(
        verbose_name='تاریخ محدودیت لغو سفارشات', null=True, blank=True)
    documents = ArrayField(
        base_field=models.ImageField(
            verbose_name='عکس جدید حجره',
            upload_to=PathAndRename('media/Pictures/Shop/Document/'),
            null=True,
            blank=True
        ),
        default=list,
        blank=True,
    )
    show_contact_info = models.BooleanField(
        'نمایش اطلاعات تماس حجره', default=False)
    is_landing = models.BooleanField(
        verbose_name='صفحه حجره لندینگ است؟', default=False)
    has_product_group_add_edit_permission = models.BooleanField(
        verbose_name='حجره دسترسی ایجاد و ویرایش محصول به صورت گروهی با استفاده از اکسل دارد؟',
        default=False)

    def __str__(self):
        return "{}".format(self.Title)

    @property
    def id(self):
        return self.ID

    @property
    def slug(self):
        return self.Slug

    @property
    def title(self):
        return self.Title

    @property
    def point(self):
        return self.Point

    @property
    def publish(self):
        return self.Publish

    @property
    def available(self):
        return self.Available

    @property
    def state(self):
        return self.State

    @property
    def big_city(self):
        return self.BigCity

    @property
    def city(self):
        return self.City

    @property
    def url(self):
        return self.get_absolute_url

    @property
    def description(self):
        return self.Description

    @property
    def image_thumbnail_url(self):
        return self.Image_thumbnail_url

    @property
    def profile(self):
        if self.FK_ShopManager:
            return self.FK_ShopManager.User_Profile
        return None

    @property
    def products(self):
        return self.ShopProduct.all()

    @property
    def url(self):
        return self.get_absolute_url

    @property
    def image_thumbnail_url(self):
        return self.Image_thumbnail_url

    @property
    def products_count(self):
        return self.get_products().count()

    @property
    def date_created(self):
        """Return the datetime of the object creation in Jalali."""
        return datetime2jalali(self.DateCreate)

    @property
    def date_updated(self):
        """Return the last update datetime of the object in Jalali."""
        return datetime2jalali(self.DateUpdate)

    @property
    def total_sell(self):
        """Return the total sell amount of the object in Jalali."""
        return self.invoice_model.objects.shop_total_sell_amount(self)

    @property
    def last_sell_date(self):
        """Return the last sell date of the object in Jalali."""
        return self.invoice_model.objects.shop_last_sell_date(self)

    @property
    def manager_last_login(self):
        """Return the last login datetime of the object in Jalali."""
        return datetime2jalali(self.FK_ShopManager.last_login)

    @property
    def manager_mobile_number(self):
        """Return the mobile number of the shop manager."""
        if self.FK_ShopManager and hasattr(self.FK_ShopManager, 'User_Profile'):
            return self.FK_ShopManager.User_Profile.MobileNumber
        return None

    @property
    def manager_full_name(self):
        manager = self.FK_ShopManager
        return f'{manager.first_name} {manager.last_name}'

    @cached_property
    def invoice_model(self):
        """Get invoice model class."""
        from invoice.models import Invoice
        return Invoice

    def get_absolute_url(self):
        """Return the absolute url of the Shop."""
        return attach_domain(f'/shop/{self.Slug}/')

    def Image_thumbnail_url(self):
        try:
            i = self.Image_thumbnail.url
            url = self.Image_thumbnail.url
            return attach_domain(url)
        except BaseException:
            url = "https://nakhll.com/media/Pictures/default.jpg"
            return url

    def get_holidays(self):
        return self.Holidays.split('-')

    def get_products_category(self):
        category = []
        for item in self.get_products():
            for category_item in item.FK_Category.filter(
                    FK_SubCategory=None, Publish=True):
                category.append(category_item)
        category = list(dict.fromkeys(category))
        return category

    def is_available(self):
        """Return True if the shop is available."""
        return self.Available and self.Publish

    def __str__(self):
        return "{}".format(self.Title)

    def Image_thumbnail_url(self):
        try:
            i = self.Image_thumbnail.url
            url = self.Image_thumbnail.url
            return attach_domain(url)
        except BaseException:
            url = "https://nakhll.com/media/Pictures/default.jpg"
            return url

    def get_holidays(self):
        return self.Holidays.split('-')

    def get_products_category(self):
        category = []
        for item in self.get_products():
            for category_item in item.FK_Category.filter(
                    FK_SubCategory=None, Publish=True):
                category.append(category_item)
        category = list(dict.fromkeys(category))
        return category

    def get_products(self):
        """Return all published products of the shop."""
        return self.ShopProduct.filter(
            Publish=True)

    def get_all_products(self):
        """Return all products of the shop."""
        return self.ShopProduct.all()

    def get_all_products_for_view(self):
        this_shop_product = list(
            Product.objects.filter(
                FK_Shop=self,
                Available=True,
                Publish=True,
                Status__in=[
                    '1',
                    '2',
                    '3']).order_by('-DateCreate'))
        this_shop_product += list(
            Product.objects.filter(
                FK_Shop=self,
                Available=True,
                Publish=True,
                Status='4').order_by('-DateCreate'))
        return this_shop_product

    def get_comments(self):
        raise NotImplementedError()

    def get_managment_image(self):
        return Profile.objects.get(
            FK_User=self.FK_ShopManager).Image_thumbnail_url()

    def get_shop_manager_full_name(self):
        """Get the full name of the shop manager."""
        return '{} {}'.format(self.FK_ShopManager.first_name,
                              self.FK_ShopManager.last_name)

    def get_active_landing(self):
        """Get the active landing of the shop."""
        return self.landings.filter(
            status=shop_models.ShopLanding.Statuses.ACTIVE).first()

    def has_advertisement(self):
        """Return True if the shop has active advertisement setting."""
        if hasattr(self, 'advertisement'):
            return self.advertisement.yektanet_status == self.advertisement.YektanetStatuses.ACTIVE
        return False

    def get_advertisement(self):
        """Get the active advertisement of the shop."""
        if self.has_advertisement():
            return self.advertisement
        return None

    def delete_image(self) -> None:
        """Delete image

        This method delete image from storage and set image to Default image
        """
        if self.Image:
            self.Image.delete()
        self.save()

    class Meta:
        ordering = ('DateCreate', 'Title',)
        verbose_name = "حجره"
        verbose_name_plural = "حجره ها"


class ShopSocialMedia(models.Model):
    """Social media links for shop

    Attributes:
        shop (Shop): Shop model
        telegram (str): Telegram link
        instagram (str): Instagram link
    """
    class Meta:
        verbose_name = 'شبکه اجتماعی حجره'
        verbose_name_plural = 'شبکه‌های اجتماعی حجره'

    def __str__(self):
        if hasattr(self, 'shop'):
            return self.shop.Slug
        return self.id

    shop = models.OneToOneField(
        Shop,
        verbose_name='حجره',
        on_delete=models.CASCADE,
        related_name='social_media')
    telegram = models.CharField(
        'تلگرام',
        max_length=100,
        help_text='آی‌دی تلگرام بدون نام سایت',
        null=True,
        blank=True)
    instagram = models.CharField(
        'اینستاگرام',
        max_length=100,
        help_text='آی‌دی اینستاگرام بدون نام سایت',
        null=True,
        blank=True)


# ----------------------------------------------------------------------------------------------------------------------------------
# ShopBankAccount (حساب‌های حجره) Model

def iban_validator(value):
    """Validator for IBAN (International Bank Account Number) field.

    Value must be all digits and its length must be equal to 24.
    """
    if not value.isdigit():
        raise ValidationError(_(f'مقدار {value} باید فقط عدد باشد'))
    if len(value) != 24:
        raise ValidationError(_(f'مقدار {value} باید فقط 24 رقم باشد'))


class ShopBankAccount(models.Model):
    """The bank account of the shop.

    Each shop can have only one bank account. The Accountant team will use this bank account to transfer money to the shop.

    Attributes:
        shop (Shop): Shop model
        iban (str): International Bank Account Number
        owner (str): Owner name
    """
    class Meta:
        verbose_name = 'حساب بانکی حجره'
        verbose_name_plural = 'حساب‌های حجره'

    def __str__(self):
        if hasattr(self, 'shop'):
            return self.shop.Slug
        return self.id

    shop = models.OneToOneField(
        Shop,
        verbose_name='حجره',
        on_delete=models.CASCADE,
        related_name='bank_account')
    iban = models.CharField(
        'شماره شبا',
        max_length=24,
        help_text='شماره شبا بدون IR',
        null=True,
        blank=True,
        validators=[iban_validator])
    owner = models.CharField('صاحب حساب', max_length=100, null=True, blank=True)


class ProductManager(models.Manager):
    """Manager for Product model."""
    FEW_HOURS_AGO = timezone.make_aware(
        datetime.datetime.now() -
        datetime.timedelta(
            hours=15))

    def get_most_discount_precentage_available_product(self):
        queryset = self.get_queryset()
        return queryset.filter(
            Publish=True, Available=True, Status__in=['1', '2', '3'],
            DateCreate__lt=self.FEW_HOURS_AGO).exclude(
            OldPrice=0).annotate(
            OldPrice_float=Cast(F('OldPrice'),
                                FloatField())).annotate(
            Price_float=Cast(F('Price'),
                             FloatField())).annotate(
            discount_ratio=(F('OldPrice_float') - F('Price_float')) /
            F('OldPrice_float')).order_by('-discount_ratio')

    def get_one_most_discount_precenetage_available_product_random(self):
        result = self.get_most_discount_precentage_available_product()
        random_id = random.randint(0, int(result.count() / 10))
        return result[random_id]

    def get_last_created_products(self):
        """Get 12 last created products. (within last 15 hours)"""
        return Product.objects \
            .filter(Publish=True, Available=True, OldPrice=0, Status__in=['1', '2', '3'],
                    DateCreate__lt=self.FEW_HOURS_AGO) \
            .order_by('-DateCreate')[:12]

    def get_last_created_discounted_products(self):
        """Get 12 last created discounted products that have discount. (within last 15 hours)"""
        return Product.objects.filter(
            Publish=True, Available=True, Status__in=['1', '2', '3'],
            DateCreate__lt=self.FEW_HOURS_AGO).exclude(
            OldPrice=0).order_by('-DateCreate')[
            : 16]

    def available_products(self):
        """Get all available products.

        A product is avaiable if both itself and its shop is published and available.
        """
        return self.filter(
            Publish=True,
            Available=True,
            FK_Shop__Available=True,
            FK_Shop__Publish=True)

    def get_random_products(self):
        """Return 16 random products from available products that are created more than
        :attr:`nakhll_market.models.ProductManager.FEW_HOURS_AGO`."""

        return self.available_products().filter(
            OldPrice=0,
            Status__in=['1', '2', '3'],
            DateCreate__lt=self.FEW_HOURS_AGO
        ).order_by('?')[:16]

    def get_most_discount_precentage_products(self):
        return self \
            .get_most_discount_precentage_available_product() \
            .order_by('?')[:15]

    def get_products_in_same_factor(self, id):
        queryset = self.get_queryset()
        try:
            product = Product.objects.get(ID=id)
            return Product.objects.filter(
                Factor_Product__Factor_Products__FK_FactorPost__FK_Product=product,
                DateCreated__lt=self.FEW_HOURS_AGO).exclude(
                ID=product.ID).distinct()
        except BaseException:
            return None

    def get_user_shop_products(self, user, shop, order=None):
        """Get all products of a shop that belong to a user.

        Args:
            user (User): User model that products belong to.
            shop (Shop): Shop model that products belong to.
            order (str, Optional): Order by this field.
        """
        queryset = self.get_queryset()
        if order and order in ['total_sell', 'title']:
            try:
                products = self.filter(
                    FK_Shop=shop,
                    FK_Shop__FK_ShopManager=user,
                    Publish=True)
                if order == 'total_sell':
                    return products.annotate(
                        num=Count('Factor_Product')).order_by('-num')
                elif order == 'title':
                    return products.order_by('Title')
            except BaseException:
                pass
        return self.filter(FK_Shop=shop, FK_Shop__FK_ShopManager=user)

    def user_shop_active_products(self, user, shop_slug):
        """Get all active products of a shop that belong to a user."""
        return self.filter(
            FK_Shop__FK_ShopManager=user, FK_Shop__Slug=shop_slug,
            Available=True, Publish=True)

    def user_shop_inactive_products(self, user, shop_slug):
        """Get all inactive products of a shop that belong to a user."""
        return self.filter(
            FK_Shop__FK_ShopManager=user, FK_Shop__Slug=shop_slug,
            Available=False, Publish=True)

    def nearly_outofstock_products(self, user, shop_slug):
        """Get all products that are nearly out of stock of a shop that belong to a user.

        There is a threshold of 10 products for all kind of products which is configurabale from:
        :attr:`nakhll_market.models.OUTOFSTOCK_LIMIT_NUM`. Any published product that has less than
        this threshold will be returned.
        """
        return self.filter(FK_Shop__FK_ShopManager=user,
                           FK_Shop__Slug=shop_slug, Publish=True,
                           Inventory__lt=OUTOFSTOCK_LIMIT_NUM)

    def outofstock_products(self, user, shop_slug):
        """Get all products that are out of stock of a shop that belong to a user."""
        return self.filter(FK_Shop__FK_ShopManager=user,
                           FK_Shop__Slug=shop_slug, Publish=True,
                           Inventory__lt=1)

    @staticmethod
    def is_product_available(product, count):
        """Check if product is available and published and also have enough items in stock."""
        return product.Available and product.Publish and product.Status != '4'

    @staticmethod
    def has_enough_items_in_stock(product, count):
        """Check if product have enough items in stock."""
        return (product.Status == '1' and product.inventory >= count) \
            or (product.Status in ['2', '3'])

    def is_product_list_valid(self, product_list):
        """Check if products in product_list is available, published and have enough in stock.

        Optimization is important here. What we do now is first check for availability and being published all in one
        query; so if a product is not avaiable or published, it rejects the product_list and return False. However if
        this step is passed, it will check every product count one by one.
        Maybe it could be better if we check for product availability and being published and product count one by one.
        """
        product_ids = [x.get('product').id for x in product_list]
        if self.filter(
                Q(ID__in=product_ids) and (
                    Q(Available=False) or Q(Publish=False)
                )).exists():
            return False
        for item in product_list:
            product = item.get('product').get_from_db()
            if product.Inventory < item.get('count'):
                return False
        return True

    @staticmethod
    def jsonify_product(product):
        """Convert a product to json format."""
        if isinstance(product, Product):
            product = [product]
        return serializers.serialize('json', product, ensure_ascii=False)

    def all_public_products(self):
        """Get all public products ordered by last updated datetime."""
        return self.filter(Publish=True, Available=True).order_by('-DateUpdate')

    def get_available_products(self):
        """Get all available products.

        A product is avaiable if both itself and its shop is published and available. Besides, there must be enough
        item of this product in stock and the status of the product must be 1, 2 or 3.
        """
        return self.get_queryset().filter(
            Publish=True, Available=True, Status__in=['1', '2', '3'],
            Inventory=True, FK_Shop__Available=True, FK_Shop__Publish=True)

    def get_most_sold_product(self):
        return self.get_available_products() \
                   .annotate(num_sell=Count('invoice_items__invoice')) \
                   .order_by('-num_sell')[:20]

    @staticmethod
    def get_product(id, raise_exception=True):
        """Get a product by id or raise Http404 exception if raise_exception is True, else return None."""
        try:
            return Product.objects.get(ID=id)
        except BaseException:
            if raise_exception:
                raise Http404
            return None


# Product (محصول) Model
class Product(models.Model):
    """Product model

    Attributes:
        ID (AutoField): Primary key of UUID.
        Title (CharField): Title of the product.
        Slug (SlugField): Slug of the product.
        Story (TextField): DEPRECATED, Story of the product.
        Description (TextField): Description of the product.
        Bio (TextField): DEPRECATED, Bio of the product.
        Image (ImageField): Main image of the product. Other images are stored in 
            :class:`nakhll_market.models.ProductImage`.
        Image_thumbnail (ImageField): Thumbnail of the main image of the product.
        Image_medium (ImageField): Medium size of the main image of the product.
        NewImage (ImageField): DEPRECATED
        Catalog (FileField): DEPRECATED, Catalog file of the product.
        FK_Shop (ForeignKey): Foreign key of the shop that this product belongs to.
        category (ForeignKey): Foreign key of the category that this product belongs to.
        Price (DecimalField): Price of the product.
        OldPrice (DecimalField): Old price of the product which must be 0 or any value greater than :attr:`Price`.
            Zero means this product doesn't have any discount, otherwise this product has a discount. 
            In any case, the actual price of the product is :attr:`Price`.
        Net_Weight (CharField): Net weight of the product without packaging.
        Weight_With_Packing (CharField): Weight of the product with packaging.
        Length_With_Packaging (CharField): DEPRECATED, Length of the product with packaging.
        Width_With_Packaging (CharField): DEPRECATED, Width of the product with packaging.
        Height_With_Packaging (CharField): DEPRECATED, Height of the product with packaging.
        Inventory (IntegerField): Inventory of the product. We don't have Inventory system, so we just increase and 
            decrease this field.
        PostRangeType (CharField): DEPRECATED, Post range type of the product. Can be any value of :attr:`POSTRANGE_TYPE`.
        Status (CharField): Status of the product. Can be any value of :attr:`PRODUCT_STATUS`.
        DateCreate (DateTimeField): Date time of the creation of the product.
        DateUpdate (DateTimeField): Date time of the last update of the product.
        Edite (BooleanField): DEPRECATED, True if the product is edited, else False.
        Available (BooleanField): True if the product is available, else False. This field editable by the shop owner.
        Publish (BooleanField): True if the product is published, else False. This field editable by the staff.
        FK_User (ForeignKey): Foreign key of the user that created, edited or confirmed this product.
        PreparationDays (IntegerField): Total number of days to prepare the product.
        post_range_cities (ManyToManyField): DEPRECATED, Cities that this product is available to post.
        is_advertisement (BooleanField): ???
        barcode (CharField): Barcode of the product. In bulk operations, we should rely on a unique field country-wide.
            So we use the barcode that comes with every product in our country. This field has no effect in other 
            sections of Nakhll, just in bulk operations.
        aparat_video_script (TextField): The script from Aparat that contains the video of the product.
        history: Using `django-simple-history <https://django-simple-history.readthedocs.io/en/latest/>`, we track our
            product changes in bulk mode, so shop owner can role back a bulk operation with just on click.
    """
    POSTRANGE_TYPE = (
        ('1', 'سراسر کشور'),
        ('2', 'استانی'),
        ('3', 'شهرستانی'),
        ('4', 'شهری'),
    )
    PRODUCT_STATUS = (
        ('1', 'آماده در انبار'),
        ('2', 'تولید بعد از سفارش'),
        ('3', 'سفارشی سازی فروش'),
        ('4', 'موجود نیست'),
    )
    AVAILABLE_STATUS = (
        (True, 'فعال'),
        (False, 'غیر فعال'),
    )
    PUBLISH_STATUS = (
        (True, 'منتشر شده'),
        (False, 'در انتظار تایید'),
    )
    EDITE_STATUS = (
        (True, 'در حال بررسی تغییرات'),
        (False, 'تغییری اعمال شده است'),
    )
    objects = ProductManager()
    ID = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True)
    Title = models.CharField(
        max_length=200,
        verbose_name='نام محصول',
        db_index=True)
    Slug = models.SlugField(
        max_length=200,
        verbose_name='شناسه محصول',
        unique=True,
        db_index=True,
        allow_unicode=True)
    Story = models.TextField(verbose_name='داستان محصول', blank=True)
    Description = models.TextField(verbose_name='درباره محصول', blank=True)
    Bio = models.TextField(verbose_name='معرفی محصول', blank=True)
    Image = models.ImageField(
        verbose_name='عکس محصول',
        upload_to=PathAndRename(
            'media/Pictures/Markets/SubMarkets/Shops/Products/'),
        help_text='عکس محصول خود را اینجا بارگذاری کنید')
    Image_thumbnail = ImageSpecField(source='Image',
                                     processors=[ResizeToFill(180, 180)],
                                     format='JPEG',
                                     options={'quality': 60})
    Image_medium = ImageSpecField(source='Image',
                                  processors=[ResizeToFill(450, 450)],
                                  format='JPEG',
                                  options={'quality': 60})
    NewImage = models.ImageField(
        verbose_name='عکس جدید حجره',
        upload_to=PathAndRename(
            'media/Pictures/Markets/SubMarkets/Shops/Products/'),
        null=True, blank=True)
    Catalog = models.FileField(
        verbose_name='کاتالوگ محصول',
        upload_to=PathAndRename(
            'media/Catalogs/Markets/SubMarkets/Shops/Products/'),
        help_text='کاتالوگ محصول خود را اینجا وارد کنید', null=True, blank=True)
    FK_Shop = models.ForeignKey(
        Shop,
        on_delete=models.PROTECT,
        verbose_name='حجره',
        related_name='ShopProduct')
    category = models.ForeignKey(
        Category,
        verbose_name='دسته بندی جدید',
        related_name='products',
        on_delete=models.PROTECT,
        db_column='category_id')
    Price = models.BigIntegerField(verbose_name='قیمت محصول')
    OldPrice = models.BigIntegerField(verbose_name='قیمت حذف محصول', default=0)
    # Product Weight Info
    Net_Weight = models.CharField(
        verbose_name='وزن خالص محصول (گرم)',
        max_length=6,
        default='0')
    Weight_With_Packing = models.CharField(
        verbose_name='وزن محصول با بسته بندی (گرم)',
        max_length=6,
        default='0')
    # Product Dimensions Info
    Length_With_Packaging = models.CharField(
        verbose_name='طول محصول با بسته بندی (سانتی متر(', max_length=4, default='0')
    Width_With_Packaging = models.CharField(
        verbose_name='عرض محصول با بسته بندی (سانتی متر(', max_length=4, default='0')
    Height_With_Packaging = models.CharField(
        verbose_name='ارتفاع محصول با بسته بندی (سانتی متر(', max_length=4, default='0')
    # Product Inventory
    Inventory = models.PositiveIntegerField(
        verbose_name='میزان موجودی از این کالا در انبار', default=5)

    PostRangeType = models.CharField(
        verbose_name='محدوده ارسال محصولات', max_length=1,
        choices=POSTRANGE_TYPE, default='1',
        help_text='محدوده ارسال را بر اساس تایپ های مشخص شده، تعیین کنید.')

    Status = models.CharField(
        verbose_name='وضعیت فروش',
        max_length=1,
        choices=PRODUCT_STATUS)
    DateCreate = models.DateTimeField(
        verbose_name='تاریخ بارگذاری محصول',
        auto_now_add=True)
    DateUpdate = models.DateTimeField(
        verbose_name='تاریخ بروزرسانی محصول', auto_now=True)

    Edite = models.BooleanField(
        verbose_name='وضعیت ویرایش محصول',
        choices=EDITE_STATUS,
        default=False)
    Available = models.BooleanField(
        verbose_name='وضعیت بارگذاری محصول',
        choices=AVAILABLE_STATUS,
        default=True)
    Publish = models.BooleanField(
        verbose_name='وضعیت انتشار محصول',
        choices=PUBLISH_STATUS,
        default=True)
    FK_User = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        verbose_name='تایید کننده',
        related_name='Product_Accept',
        blank=True,
        null=True)
    PreparationDays = models.PositiveSmallIntegerField(
        verbose_name='زمان آماده‌سازی', null=True)
    post_range_cities = models.ManyToManyField(
        'City',
        related_name='products',
        verbose_name=_('شهرهای قابل ارسال'),
        blank=True)
    is_advertisement = models.BooleanField(
        verbose_name=_('آگهی'), default=False, null=True)
    barcode = models.CharField(
        verbose_name='بارکد',
        max_length=13,
        null=True,
        blank=True)
    aparat_video_script = models.CharField(
        verbose_name='اسکریپت ویدیو آپارات',
        max_length=255,
        null=True,
        blank=True,
        default=None)
    history = HistoricalRecords()

    @property
    def id(self):
        return self.ID

    @property
    def user(self):
        return self.FK_User

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
        return self.Product_Comment.filter(FK_Pater=None)

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

    @property
    def preparation_days(self):
        return self.PreparationDays

    @property
    def post_range_type(self):
        return self.PostRangeType

    def is_available(self):
        """Check if product is available or not

        A product is available if it is both Available and Publish and also its shop
        :attr:`nakhll_market.models.Shop.is_available` returns True as well. No matter if it has inventory or not.
        """
        return self.Available and self.Publish and self.FK_Shop.is_available()

    @property
    def salable(self):
        return self.is_available()

    def has_enough_items_in_stock(self, count):
        """Check if product have enough items in stock, no matter if it is available or not"""
        return (self.Status == '1' and self.inventory >= count) \
            or (self.Status in ['2', '3'])

    # These properties are created for Torob API
    @property
    def page_url(self):
        """Torob API property: The URL of the product that Torob redirect users after clicking on purchase button.

        This URL is a  intermediary URL in our website that redirects user to the product page. We use a intermediary
        view between Torob and our end-user product page to be able to track users that are redirected from Torob
        """
        url = f'/torob/products/{self.ID}/'
        return attach_domain(url)

    @property
    def page_unique(self):
        """Torob API property: A unique identifier for our products in Torob Website"""
        return self.ID

    @property
    def subtitle(self):
        """Torob API property: Use product Slug as subtitle

        Torob needs a title and a subtitle of our products, so we use :attr:`Title` as title and :attr:`Slug` as slug
        """
        return self.Slug

    @property
    def current_price(self):
        """Torob API property: Use product :attr:`Price` as  current_price in Torob

        Torob needs a current_price and a old_price of our products, so we use :attr:`Price` as current_price and
        :attr:`OldPrice` as old_price
        """
        return self.Price

    @property
    def availability(self):
        """Torob API property: Availability of product in Torob website.

        An available product in Torob must be both :attr:`is_available` and has at least one item in stock
        """
        return 'instock' if self.Available and self.Publish and \
            self.FK_Shop.is_available() and \
            (self.Status == '1' and self.inventory) or \
            (self.Status in ['2', '3']) else ''

    @property
    def category_name(self):
        """Torob API property: Category name of the product"""
        return self.category.name

    @property
    def image_link(self):
        """Torob API property: The image link of the product"""
        if self.Image:
            return attach_domain(self.Image.url)

    @property
    def short_desc(self):
        """Torob API property: A description of our product in Torob"""
        return self.Description

    def __str__(self):
        return "{}".format(self.Title)

    def get_status(self):
        """Get the Persian message of the product property"""
        Status = {
            "1": 'آماده در انبار',
            "2": 'تولید بعد از سفارش',
            "3": 'سفارشی سازی فروش',
            "4": 'موجود نیست',
        }
        return Status[self.Status] if (self.Status == '1' and self.inventory) \
            or (self.Status in ['2', '3']) else Status['4']

    def get_sendtype(self):
        """Get the Persian message of the product :attr:`PostRangeType`"""
        SendType = {
            "1": 'سراسر کشور',
            "2": 'استانی',
            "3": 'شهرستانی',
            "4": 'شهری',
        }
        return SendType[self.PostRangeType]

    def get_absolute_url(self):
        """Absolute URL of our product in Front-end framework"""
        return attach_domain(f'/shop/{self.FK_Shop.Slug}/product/{self.Slug}')

    def get_add_to_cart_url(self):
        return reverse("Payment:add-to-cart", kwargs={
            'ID': self.ID
        })

    def get_remove_from_cart_url(self):
        return reverse("Payment:remove-from-cart", kwargs={
            'ID': self.ID
        })

    def get_discounted(self):
        """Get total amount of discount for this product"""
        try:
            return int((self.OldPrice - self.Price) * 100 / self.OldPrice)
        except BaseException:
            return 0

    def get_product_net_weight(self):
        # Get Net Weight
        try:
            return self.Net_Weight
        except BaseException:
            return 'نا مشخص'

    def get_product_weight_with_packing(self):
        # Get Weight With Packing
        try:
            return self.Weight_With_Packing
        except BaseException:
            return 'نا مشخص'

    def get_product_dimensions(self):
        # Get Dimensions
        try:
            return str(self.Length_With_Packaging) + ' * ' + str(
                self.Width_With_Packaging) + ' * ' + str(self.Height_With_Packaging)
        except BaseException:
            return 'نا مشخص'

    def get_product_weight_convert_to_int(self):
        # Get Product Weightn Convert To Int
        try:
            net_weight = int(self.Net_Weight)
            weight_with_packing = int(self.Weight_With_Packing)
            this_sum = 0
            if (weight_with_packing > net_weight) or (
                    weight_with_packing == net_weight):
                this_sum += weight_with_packing
            else:
                this_sum += net_weight
            return this_sum
        except BaseException:
            return 0

    def get_product_packing_volume_convert_to_int(self):
        # Get Product Packing Volume Convert To Int
        try:
            vloume = int(self.Length_With_Packaging) * int(
                self.Width_With_Packaging) * int(self.Height_With_Packaging)
            this_vloume = 0
            if vloume > 3000:
                this_vloume += math.ceil(vloume / 3000) * 50
            elif vloume != 0:
                this_vloume += 50
            return this_vloume
        except BaseException:
            return 0

    def get_total_product_weight(self):
        try:
            return self.get_product_weight_convert_to_int(
            ) + self.get_product_packing_volume_convert_to_int()
        except BaseException:
            return 0

    def check_product_post_status(self):
        # Check Product Post Status
        if (self.get_total_product_weight() > 40000) or (
                (int(self.Length_With_Packaging) > 100) or (int(self.Width_With_Packaging) > 100) or (
                int(self.Height_With_Packaging) > 100)):
            return True
        else:
            return False

    def default_image_url(self):
        """Default image of product if there is no image is available"""
        return 'https://nakhll.com/media/Pictures/default.jpg'

    def get_image(self):
        """Get the absolute URL of product's image if available, else return :attr:`default_image_url`"""
        try:
            return attach_domain(self.Image.url)
        except BaseException:
            return self.default_image_url()

    def get_image_alt(self):
        return self.Title

    def Image_thumbnail_url(self):
        """Get the absolute URL of product's thumbnail image if available, else return a default image"""
        try:
            url = self.Image_thumbnail.url
            return attach_domain(url)
        except BaseException:
            url = "https://nakhll.com/media/Pictures/default.jpg"
            return url

    def Image_medium_url(self):
        """Get the absolute URL of product's medium image if available, else return a default image"""
        try:
            url = self.Image_medium.url
            return attach_domain(url)
        except BaseException:
            url = "https://nakhll.com/media/Pictures/default.jpg"
            return url

    def get_url(self):
        try:
            return reverse("nakhll_market:ProductsDetail", kwargs={
                'shop_slug': self.FK_Shop.Slug,
                'product_slug': self.Slug
            })
        except BaseException:
            return '/'

    def get_point(self):
        try:
            this_point = 0.0
            for item in self.FK_Points.all():
                this_point += item.Point
            return round(this_point / self.get_point_count(), 2)
        except BaseException:
            return 0.0

    def Point(self):
        return self.get_point()

    def get_point_count(self):
        return self.FK_Points.all().count()

    def get_related_products(self):
        return Product.objects \
            .filter(
                Available=True,
                Publish=True,
                Status__in=['1', '2', '3'],
                FK_Category__in=self.FK_Category.all()
            ).order_by('?')[:12]

    def get_product_categories(self):
        raise NotImplementedError()

    def get_product_inpostrange(self):
        raise NotImplementedError()

    def get_product_outpostrange(self):
        raise NotImplementedError()

    def get_shop_slug(self):
        return self.FK_Shop.Slug

    def reduce_stock(self, count):
        """Reduce product's inventory after a successful purchase.

        This is one of the :attr:`invoice.modeles.Invoice.complete_payment` method of invoice model which will trigger
        after a successful purchase. In case the inventory of the product doesn't have enough item, it will create an
        alert for staff and return without any action.
        """
        if self.Inventory < count:
            AlertInterface.not_enogth_in_stock(self, count)
            return
        self.Inventory -= count
        self.save()

    class Meta:
        ordering = ('DateCreate', 'Title',)
        verbose_name = "محصول"
        verbose_name_plural = "محصولات"
        constraints = [
            UniqueConstraint(
                fields=[
                    'Title',
                    'FK_Shop_id'],
                name='unique_shop_product_title'),
            CheckConstraint(
                check=~Q(Price=0),
                name='check_price_not_zero'),
            CheckConstraint(
                check=Q(OldPrice__gt=F('Price')) | Q(OldPrice=0),
                name='price_is_greater_than_discounted_price'
            )]


class Tag(models.Model):
    """Tag model for a shop"""
    name = models.CharField(max_length=127, verbose_name=_('نام تگ'),
                            error_messages={
        'max_length': _('نام تگ باید کمتر از 127 کاراکتر باشد.'), }
    )
    shop = models.ForeignKey(
        Shop,
        on_delete=models.CASCADE,
        verbose_name=_('حجره'),
        related_name="tags")

    class Meta:
        unique_together = ('name', 'shop')
        verbose_name = _('تگ')
        verbose_name_plural = _('تگ‌')

    def __str__(self):
        return f"{self.name}"


class ProductTag(models.Model):
    """Tag model for a product"""
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name=_('محصول'),
        related_name="product_tags")
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        verbose_name=_('تگ'),
        related_name='product_tags')

    class Meta:
        unique_together = ('product', 'tag')
        verbose_name = _('تگ محصول')
        verbose_name_plural = _('تگ محصول')

    def __str__(self):
        return f"{self.product} - {self.tag}"


# Product Banner (گالری محصول) Model
class ProductBanner(models.Model):
    """Images of a product besides the main product image

    Attributes:
        FK_Product (:class:`Product`): Product which this banner belongs to
        Title (str): Title of the image
        Description (str): Description of the image
        URL (str): The URL which user will redirect to after clicking the image
        Image (ImageField): The actual image file
        Image_medium (ImageField): The medium size image file
        NewImage (ImageField): DEPRECATED
        BannerBuilder (CharField): DEPRECATED 
        BannerURL (CharField): DEPRECATED
        DateCreate (DateTimeField): DateTime of creation
        DateUpdate (DateTimeField): DateTime of last update
        Edite (BooleanField): DEPRECATED, Whether the image is edited or not
        Available (BooleanField): Whether the image is available or not. This field is editable by shop owner.
        Publish (BooleanField): Whether the image is published or not. This field is editable by staff only.
        FK_User (ForeignKey): DEPRECATED, User who confirmed the image
    """
    FK_Product = models.ForeignKey(
        Product,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='نام محصول',
        related_name='Product_Banner')
    Title = models.CharField(
        verbose_name='برچسب روی بنر',
        max_length=100,
        null=True,
        blank=True,)
    Description = models.TextField(
        verbose_name='درباره بنر',
        max_length=350,
        blank=True)
    URL = models.URLField(
        verbose_name='لینک',
        help_text='لینکی که در صورت کلیک به آن منتقل می شود',
        blank=True)
    Image = models.ImageField(
        verbose_name='بنر محصول',
        upload_to=PathAndRename(
            'media/Pictures/Markets/SubMarkets/Shops/Products/Banners/'),
        help_text='بنر محصول را اینجا وارد کنید')
    Image_medium = ImageSpecField(source='Image',
                                  processors=[ResizeToFill(450, 450)],
                                  format='JPEG',
                                  options={'quality': 60})
    NewImage = models.ImageField(
        verbose_name='عکس جدید حجره',
        upload_to=PathAndRename(
            'media/Pictures/Markets/SubMarkets/Shops/Products/Banners/'),
        null=True, blank=True)
    BannerBuilder = models.CharField(
        verbose_name='نام تولید کننده بنر',
        max_length=120,
        blank=True)
    BannerURL = models.URLField(verbose_name='لینک تولید کننده بنر', blank=True)
    DateCreate = models.DateTimeField(
        verbose_name='تاریخ بارگذاری بنر محصول',
        auto_now_add=True)
    DateUpdate = models.DateTimeField(
        verbose_name='تاریخ بروزرسانی بنر محصول', auto_now=True)
    AVAILABLE_STATUS = (
        (True, 'فعال'),
        (False, 'غیر فعال'),
    )
    PUBLISH_STATUS = (
        (True, 'منتشر شده'),
        (False, 'در انتظار تایید'),
    )
    EDITE_STATUS = (
        (True, 'در حال بررسی تغییرات'),
        (False, 'تغییری اعمال شده است'),
    )
    Edite = models.BooleanField(
        verbose_name='وضعیت ویرایش بنر حجره',
        choices=EDITE_STATUS,
        default=False)
    Available = models.BooleanField(
        verbose_name='وضعیت بارگذاری بنر محصول',
        choices=AVAILABLE_STATUS,
        default=True)
    Publish = models.BooleanField(
        verbose_name='وضعیت انتشار بنر محصول',
        choices=PUBLISH_STATUS,
        default=False)
    FK_User = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        verbose_name='تایید کننده',
        related_name='Product_Banner_Accept',
        blank=True,
        null=True)

    @property
    def image(self):
        return self.Image_thumbnail_url()

    def Image_thumbnail_url(self):
        try:
            i = self.Image_medium.url
            url = self.Image_medium.url
            return attach_domain(url)
        except BaseException:
            url = "https://nakhll.com/media/Pictures/default.jpg"
            return url

    # Output Customization Based On Title
    def __str__(self):
        return "{}".format(self.Title)

    class Meta:
        ordering = ('id', 'Title',)
        verbose_name = "گالری محصول"
        verbose_name_plural = "گالری محصولات "


# Comment (نظر محصول) Model
class Comment(models.Model):
    """DEPRECATED MODEL"""
    TYPE_STATUS = (
        (False, 'منفی'),
        (True, 'مثبت'),
    )
    Type = models.BooleanField(
        verbose_name='نوع نظر',
        choices=TYPE_STATUS,
        default=True)
    FK_UserAdder = models.ForeignKey(
        User, on_delete=models.SET_NULL, verbose_name='کاربر',
        related_name='User_Comment', null=True)
    FK_Product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        verbose_name='محصول',
        related_name='Product_Comment',
        blank=True,
        null=True)
    Description = models.TextField(verbose_name='توضیخات نظر')
    FK_Like = models.ManyToManyField(
        User,
        verbose_name='لایک کننده',
        related_name='Comment_Like',
        blank=True)
    FK_Pater = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        verbose_name='ریپلای شده',
        related_name='Comment_Pater',
        blank=True,
        null=True)
    Available = models.BooleanField(
        verbose_name='وضعیت انتشار نظر', default=False)
    DateCreate = models.DateTimeField(
        verbose_name='تاریخ ثبت نظر',
        auto_now_add=True)
    FK_User = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        verbose_name='تایید کننده',
        related_name='Comment_Accept',
        blank=True,
        null=True)

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
        return datetime2jalali(self.DateCreate)

    @property
    def type(self):
        return self.TYPE_STATUS[self.Type][1]

    def get_type(self):
        if self.Type:
            return 'مثبت'
        else:
            return 'منفی'

    @property
    def comment_replies(self):
        if self.Comment_Pater:
            return self.Comment_Pater.all()

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
            this_profile = get_object_or_404(Profile, FK_User=self.FK_UserAdder)
            return this_profile.Image_thumbnail_url()
        except BaseException:
            url = "https://nakhll.com/media/Pictures/avatar.png"
            return url


class ProfileQuerySet(models.QuerySet):
    def shop_count(self):
        return self.annotate(shop_count=Count('FK_User__ShopManager'))

    def have_shop(self):
        return self.filter(shop_count__gte=1)

    def have_not_shop(self):
        return self.filter(shop_count=0)


class ProfileManager(models.Manager):
    def get_queryset(self):
        return ProfileQuerySet(self.model, using=self._db)

    def get_user_by_mobile_number(self, mobile_number: str) -> User:
        queryset = self.get_queryset()
        return queryset.get(MobileNumber=mobile_number).FK_User

    def user_exists_by_mobile_number(self, mobile_number: str) -> bool:
        if self.get_user_by_mobile_number(mobile_number):
            return True
        else:
            return False

    def set_user_password_by_mobile_number(
            self, mobile_number, password) -> User:
        user = self.get_user_by_mobile_number(mobile_number)
        user.set_password(password)
        user.save()
        return user

    def create_profile(self, mobile_number, user, reference_code, user_ip):
        '''
        this function create user and all related objects
        it must be transactional because we create 3 objects
        or we don't need none of them.
        TODO MAKE IT TRANSACTIONAL
        '''
        queryset = self.get_queryset()
        return queryset.create(
            FK_User=user,
            MobileNumber=mobile_number,
            IPAddress=user_ip,
            ReferenceCode=reference_code
        )


# Profile (پروفایل) Model
class Profile(models.Model):
    """Profile model for User with OneToOne Relationship.

    Attributes:
        ID (AutoField): Primary Key of UUID type.
        FK_User (OneToOneField): Foreign Key of User model.
        Sex (CharField): DEPRECATED, The gender of the user
        CountrPreCode (CharField): DEPRECATED, Country Code of User
        MobileNumber (CharField): Mobile number of user which should be unique
        ZipCode (CharField): DEPRECATED, Zip code of user
        NationalCode (CharField): National code of user
        Address (CharField): DEPRECATED, Address of user
        State (CharField): DEPRECATED, State of user
        BigCity (CharField): DEPRECATED, Big city of user
        City (CharField): DEPRECATED, City of user
        Location (CharField): DEPRECATED, Location of user
        BrithDay (jmodels.jDateField): DEPRECATED, Brithday of user in Jalali format
        FaxNumber (CharField): DEPRECATED, Fax number of user
        CityPerCode (CharField): DEPRECATED, City code of user
        PhoneNumber (CharField): DEPRECATED, Fix phone number of user
        Bio (CharField): DEPRECATED, Bio of user
        Image (ImageField): Image of user
        Image_thumbnail (ImageField): Image of user in thumbnail size
        ImageNationalCard (ImageField): DEPRECATED, Image of user's national card after verification
        ImageNationalCardUnverified (ImageField): DEPRECATED, Image of user's national card before verification
        UserReferenceCode (CharField): DEPRECATED, User reference code
        Point (IntegerField): DEPRECATED, Point of user
        TutorialWebsite (CharField): DEPRECATED, How the user introducted with our website
        ReferenceCode (CharField): DEPRECATED, Reference code of user
        IPAddress (CharField): DEPRECATED, IP address of user
    """
    SEX_STATUS = (
        ('0', 'انتخاب جنسیت'),
        ('1', 'زن'),
        ('2', 'مرد'),
        ('3', 'سایر'),
    )
    TUTORIALWEB_TYPE = (
        ('0', 'موتور های جستجو'),
        ('1', 'حجره داران'),
        ('2', 'شبکه های اجتماعی'),
        ('3', 'کاربران'),
        ('4', 'رسانه ها'),
        ('5', 'تبلیغات'),
        ('6', 'NOD'),
        ('7', 'سایر'),
        ('8', 'هیچ کدام'),
    )
    objects = ProfileManager()
    ID = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True)
    FK_User = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        verbose_name='کاربر',
        related_name='User_Profile',
        null=True)
    Sex = models.CharField(
        verbose_name='جنسیت',
        max_length=1,
        choices=SEX_STATUS,
        default='0')
    CountrPreCode = models.CharField(
        verbose_name='کد کشور',
        max_length=6,
        default='098')
    MobileNumber = models.CharField(
        verbose_name='شماره موبایل',
        max_length=11,
        unique=True)
    ZipCode = models.CharField(
        verbose_name='کد پستی',
        max_length=10,
        blank=True)
    NationalCode = models.CharField(
        verbose_name='کد ملی',
        max_length=10,
        unique=True,
        blank=True,
        null=True)
    Address = models.TextField(verbose_name='آدرس', blank=True)
    State = models.CharField(verbose_name='استان', max_length=50, blank=True)
    BigCity = models.CharField(
        verbose_name='شهرستان',
        max_length=50,
        blank=True)
    City = models.CharField(verbose_name='شهر', max_length=50, blank=True)
    Location = models.CharField(
        verbose_name='موقعیت مکانی',
        max_length=150,
        blank=True,
        help_text='طول و عرض جغرافیایی')
    BrithDay = jmodels.jDateField(verbose_name='تاریخ تولد', null=True)
    FaxNumber = models.CharField(
        verbose_name='شماره فکس',
        max_length=8,
        blank=True)
    CityPerCode = models.CharField(
        verbose_name='پیش شماره',
        max_length=6,
        blank=True,
        default='034')
    PhoneNumber = models.CharField(
        verbose_name='شماره تلفن ثابت',
        max_length=8,
        blank=True)
    Bio = models.CharField(verbose_name='درباره من', max_length=250, blank=True)
    Image = models.ImageField(
        verbose_name='پروفایل',
        upload_to=PathAndRename('media/Pictures/Profile/'),
        null=True, default='static/Pictures/DefaultProfile.png')
    Image_thumbnail = ImageSpecField(source='Image',
                                     processors=[ResizeToFill(175, 175)],
                                     format='JPEG',
                                     options={'quality': 60})
    ImageNationalCard = models.ImageField(
        verbose_name="عکس کارت ملی",
        upload_to=PathAndRename('media/Pictures/NationalCard/'),
        null=True, blank=True)
    ImageNationalCardUnverified = models.ImageField(
        verbose_name="عکس کارت ملی تایید نشده",
        upload_to=PathAndRename('media/Pictures/NationalCard/'),
        null=True, blank=True)
    refer_code = models.CharField(
        verbose_name='کد شما', max_length=6, unique=True,
        default=build_refer_code(6))
    Point = models.PositiveIntegerField(verbose_name='امتیاز کاربر', default=0)
    TutorialWebsite = models.CharField(
        verbose_name='نحوه آشنایی با سایت', max_length=1,
        choices=TUTORIALWEB_TYPE, blank=True, default='8')
    IPAddress = models.CharField(
        verbose_name='آدرس ای پی',
        max_length=15,
        blank=True)
    referrer = models.ForeignKey(
        User,
        verbose_name='دعوت کننده به نخل',
        null=True,
        blank=True,
        on_delete=models.SET_NULL)
    expiration_date_of_referral_link = jmodels.jDateField(null=True, blank=True)

    # Output Customization Based On UserName (ID)
    def __str__(self):
        return "{} ({})".format(self.FK_User, self.ID)

    def Image_thumbnail_url(self):
        try:
            i = self.Image_thumbnail.url
            url = self.Image_thumbnail.url
            return attach_domain(url)
        except BaseException:
            url = "https://nakhll.com/media/Pictures/avatar.png"
            return url

    def image_national_card_url(self):
        try:
            i = self.ImageNationalCard.url
            url = self.ImageNationalCard.url
            return attach_domain(url)
        except BaseException:
            url = "https://nakhll.com/static-django/images/image_upload.jpg"
            return url

    # Get User Bank Account Info
    def get_bank_account_name(self):
        raise NotImplementedError()

    def get_credit_card_number(self):
        raise NotImplementedError()

    def get_shaba_number(self):
        raise NotImplementedError()

    def chack_user_bank_account(self):
        if (self.get_bank_account_name() is None) or (
                self.get_credit_card_number() is None) or (self.get_shaba_number() is None):
            return True
        else:
            return False

    def is_user_shoper(self):
        if Shop.objects.filter(FK_ShopManager=self.FK_User).exists():
            return True
        else:
            return False

    def get_user_shops(self):
        return Shop.objects.filter(FK_ShopManager=self.FK_User, Publish=True)

    def get_user_products(self):
        return Product.objects.filter(
            FK_Shop__in=self.get_user_shops(),
            Publish=True)

    def get_state_name(self):
        try:
            return State.objects.get(id=self.State).name
        except BaseException:
            return None

    def get_bigcity_name(self):
        try:
            return BigCity.objects.get(id=self.BigCity).name
        except BaseException:
            return None

    def get_city_name(self):
        try:
            return City.objects.get(id=self.City).name
        except BaseException:
            return None

    def is_referral_link_active(self):
        if self.expiration_date_of_referral_link and\
                self.expiration_date_of_referral_link >= timezone.now():
            return True
        return False

    def extend_referral_link(self):
        self._extend_referral_link()

    def _extend_referral_link(self):
        self.expiration_date_of_referral_link = jdatetime.date.today(
        ) + REFERRAL_LINK_DURATION
        self.save()

    @property
    def id(self):
        return self.ID

    @property
    def user(self):
        return self.FK_User

    @property
    def first_name(self):
        return self.user.first_name

    @property
    def last_name(self):
        return self.user.last_name

    @property
    def sex(self):
        return self.Sex

    @property
    def birth_day(self):
        return str(self.BrithDay)

    @property
    def counter_pre_code(self):
        return self.CountrPreCode

    @property
    def mobile_number(self):
        return self.MobileNumber

    @property
    def zip_code(self):
        return self.ZipCode

    @property
    def national_code(self):
        return self.NationalCode

    @property
    def address(self):
        return self.Address

    @property
    def state(self):
        return self.State

    @property
    def big_city(self):
        return self.BigCity

    @property
    def city(self):
        return self.City

    @property
    def location(self):
        return self.Location

    @property
    def fax_number(self):
        return self.FaxNumber

    @property
    def city_per_code(self):
        return self.CityPerCode

    @property
    def phone_number(self):
        return self.PhoneNumber

    @property
    def bio(self):
        return self.Bio

    @property
    def image(self):
        return attach_domain(self.Image.url)

    @property
    def image_national_card(self):
        return attach_domain(
            self.ImageNationalCard.url) if self.ImageNationalCard else None
            
    @property
    def point(self):
        return self.Point

    @property
    def tutorial_website(self):
        return self.TutorialWebsite

    @property
    def reference_code(self):
        return self.ReferenceCode

    @property
    def ip_address(self):
        return self.IPAddress

    @property
    def shops(self):
        return self.FK_User.ShopManager.all()

    @property
    def date_joined(self):
        return datetime2jalali(self.FK_User.date_joined, date_only=True)

    @property
    def is_referred(self):
        return bool(self.referrer)

    @property
    def link_status(self):
        if self.expiration_date_of_referral_link is None:
            return FIRST_TIME_REFERRAL
        if self.is_referral_link_active():
            return ACTIVE_REFERRAL
        else:
            return EXPIRED_REFERRAL

    # Ordering With DateCreate
    class Meta:
        ordering = ('ID',)
        verbose_name = "پروفایل"
        verbose_name_plural = "پروفایل ها "


# Slider (اسلایدر) Model
class Slider(models.Model):
    """DEPRECATED"""
    FK_Creator = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        verbose_name='ثبت کننده',
        related_name='Slider_Create',
        null=True)
    Title = models.CharField(
        verbose_name='برچسب روی اسلایدر',
        max_length=100,
        db_index=True)
    Description = models.TextField(
        verbose_name='درباره اسلایدر',
        max_length=350,
        blank=True)
    ShowInfo = models.BooleanField(
        verbose_name='وضعیت نمایش اطلاعات اسلایدر', default=True,
        help_text='اگر می خواهید عنوان و توضیحات بنر روی آن نمایش داده شود، این گزینه را فعال کنید.')
    URL = models.URLField(
        verbose_name='لینک',
        help_text='لینکی که در صورت کلیک به آن منتقل می شود',
        blank=True)
    Image = models.ImageField(
        verbose_name='عکس اسلایدر',
        upload_to=PathAndRename('media/Pictures/Sliders/'),
        help_text='اسلایدر را اینجا وارد کنید')
    Location = models.IntegerField(verbose_name='مکان اسلایدر')
    DateCreate = models.DateTimeField(
        verbose_name='تاریخ بارگذاری اسلایدر',
        auto_now_add=True)
    DtatUpdate = models.DateTimeField(
        verbose_name='تاریخ بروزرسانی اسلایدر', auto_now=True)

    AVAILABLE_STATUS = (
        (True, 'فعال'),
        (False, 'غیر فعال'),
    )
    PUBLISH_STATUS = (
        (True, 'منتشر شده'),
        (False, 'در انتظار تایید'),
    )
    Available = models.BooleanField(
        verbose_name='وضعیت بارگذاری فیلم محصول',
        choices=AVAILABLE_STATUS,
        default=True)
    Publish = models.BooleanField(
        verbose_name='وضعیت انتشار فیلم محصول',
        choices=PUBLISH_STATUS,
        default=False)
    FK_User = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        verbose_name='تایید کننده',
        related_name='Slider_Accept',
        blank=True,
        null=True)
    BannerBuilder = models.CharField(
        verbose_name='نام تولید کننده بنر',
        max_length=120,
        blank=True)
    BannerURL = models.URLField(verbose_name='لینک تولید کننده بنر', blank=True)

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
            return attach_domain(self.Image.url)
        except BaseException:
            return None

    # Output Customization Based On Title
    def __str__(self):
        return "{}".format(self.Title)

    # Ordering With id
    class Meta:
        ordering = ('id',)
        verbose_name = "اسلایدر"
        verbose_name_plural = "اسلایدر ها"


# Alert (هشدار ها) Model
class Alert(models.Model):
    """The notification model for events in Nakhll system

    For each event that we want to notify staffs, we create an alert object.
    Staffs should regualrly check the alerts and see if there is any new event.

    Attributes:
        FK_User (User): The user who created the alert, or the user who is this event is related to.
        Part (str): The type of the event. Event types are defined in :attr:`PART_TYPE`.
        Slug (str): The slug of the model that is related to the event. Using Part and Slug, we can find the related
            model instance that the event is related to.
        Seen (bool): Whether the alert has been seen or not.
        alert_description (str): The description of the alert.
        Status (str): The status of the alert. Alert statuses are defined in :attr:`STATUS`.
        DateCreate (datetime): The date of the alert creation.
        DateUpdate (datetime): The date of the alert update.
        Description (str): In case the alert is rejectable, this is the reason why staff rejected the alert.
        FK_Staff (User): The staff that accepted or rejected the alert.

    """
    class AlertParts:
        ADD_PROFILE = '0'
        EDIT_PROFILE = '1'
        PAYMENT_ERROR = '35'

    FK_User = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        verbose_name='ثبت کننده',
        related_name='User_Registrar_Alert',
        blank=True,
        null=True)
    PART_TYPE = (
        ('0', 'ایجاد پروفایل'),
        ('1', 'ویرایش پروفایل'),
        ('2', 'ایجاد حجره'),
        ('3', 'ویرایش حجره'),
        ('4', 'ایجاد بنر حجره'),
        ('5', 'ویرایش بنر حجره'),
        ('6', 'ایجاد محصول'),
        ('7', 'ویرایش محصول'),
        ('8', 'ایجاد بنر محصول'),
        ('9', 'ویرایش بنر محصول'),
        ('10', 'ایجاد ویژگی جدید'),
        ('11', 'ثبت ویژگی جدید برای محصول'),
        ('12', 'ثبت سفارش'),
        ('13', 'لغو سفارش'),
        ('14', 'ثبت کامنت جدید'),
        ('15', 'ثبت نقد و بررسی جدید'),
        ('16', 'ثبت تیکت جدید'),
        ('17', 'ایجاد ارزش ویژگی جدید'),
        ('18', 'ثبت انتقاد و پیشنهاد یا شکایت'),
        ('19', 'لغو صورت حساب'),
        ('20', 'تایید سفارش'),
        ('21', 'ارسال سفارش'),
        ('22', 'حذف بنر حجره'),
        ('23', 'حذف بنر محصول'),
        ('24', 'حذف ویژگی محصول'),
        ('25', 'حذف ارزش ویژگی'),
        ('26', 'ایجاد کوپن'),
        ('27', 'حذف کوپن'),
        ('28', 'ثبت کامنت پست'),
        ('29', 'ثبت کامنت داستان'),
        ('30', 'ثبت کامنت حجره'),
        ('31', 'درخواست تسویه'),
        ('32', 'ثبت ویژگی انتخابی جدید'),
        ('33', 'حذف ویژگی انتخابی'),
        ('34', 'ارسال سفارش‌های جداگانه'),
        ('35', 'خطای پرداخت'),
    )
    Part = models.CharField(
        verbose_name='بخش',
        choices=PART_TYPE,
        max_length=2,
        default='0')
    Slug = models.TextField(verbose_name='شناسه بخش', blank=True, null=True)
    SEEN_STATUS = (
        (True, 'دیده شده'),
        (False, 'دیده نشده'),
    )
    Seen = models.BooleanField(
        verbose_name='وضعیت بازدید',
        choices=SEEN_STATUS,
        default=False)
    STATUS = (
        (True, 'ثبت تغییرات'),
        (False, 'عدم ثبت تغییرات'),
    )
    alert_description = models.TextField(
        verbose_name='توضیحات', blank=True, null=True,
        help_text='توضیحات در مورد هشدار')
    Status = models.BooleanField(
        verbose_name='وضعیت تغییرات',
        choices=STATUS,
        null=True)
    DateCreate = models.DateTimeField(
        verbose_name='تاریخ ثبت هشدار',
        auto_now_add=True)
    DateUpdate = models.DateTimeField(
        verbose_name='تاریخ ثبت تغییرات', auto_now=True)
    Description = models.TextField(
        verbose_name='توضیحات', blank=True,
        help_text='در صورت عدم پذیرش تغییرات انجام شده، لطفا دلایل خودت را اینجا وارد نمایید.')
    FK_Staff = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        verbose_name='ثبت کننده',
        related_name='Alert_User_Published',
        blank=True,
        null=True)

    def __str__(self):
        return "{} - {}".format(self.FK_User, self.FK_Staff)

    def get_part_display(self):
        if self.Part == '31':
            return 'درخواست تسویه'

    class Meta:
        ordering = ('id',)
        verbose_name = "هشدار"
        verbose_name_plural = "هشدار ها"


# ----------------------------------------------------------------------------------------------------------------------------------
class AmazingProductManager(models.Manager):
    def get_amazing_products(self):
        queryset = self.get_queryset()
        now = timezone.now()
        return queryset.filter(
            start_date__lte=now,
            end_date__gte=now
        )


class AmazingProduct(models.Model):
    """The Amazing Product Model

    Amazing products are products that are selected (usally by marketing team) to be shown in special locations on the
    website, like the main page.

    Attributes:
        product (Product): The product that is selected as amazing.
        start_date (DateTimeField): The date from which the product is selected as amazing.
        end_date (DateTimeField): The date until which the product is selected as amazing.
    """
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


# ----------------------------------------------------------------------------------------------------------------------------------

# State استان
class State(models.Model):
    """Iran states

    Attributes:
        name (CharField): The name of the state.
        code (IntegerField): The code of the state.
    """
    name = models.CharField(verbose_name='نام استان', max_length=127)
    code = models.IntegerField(verbose_name='کد استان')

    class Meta:
        ordering = ('id',)
        verbose_name = "استان"
        verbose_name_plural = "استان ها"

    def get_bigcities_of_state(self):
        """Return all big cities of the state as a queryset."""
        return self.big_city.all()

    def get_bigcities_of_state_id_name(self):
        """Return all big cities of the state as a dictionary of name and id."""
        return self.get_bigcities_of_state().values('name', 'id')

    def __str__(self):
        return f'{self.name}'


# ‌BigCity شهرستان
class BigCity(models.Model):
    """Big cities of each state

    Attributes:
        name (CharField): The name of the big city.
        code (IntegerField): The code of the big city.
        state (State): The state of the big city.
    """
    name = models.CharField(verbose_name='نام شهرستان', max_length=127)
    code = models.IntegerField(verbose_name='کد شهرستان')
    state = models.ForeignKey(
        State,
        related_name='big_city',
        on_delete=models.CASCADE)

    class Meta:
        ordering = ('id',)
        verbose_name = "شهرستان"
        verbose_name_plural = "شهرستان ها"

    def get_cities_of_bigcities(self):
        """Return all cities of the big city as a queryset."""
        return self.city.all()

    def get_cities_of_bigcities_id_name(self):
        """Return all cities of the big city as a dictionary of name and id."""
        return self.get_cities_of_bigcities().values('id', 'name')

    def __str__(self):
        return f'{self.state} - {self.name}'


# ‌City شهر
class City(models.Model):
    """City of each big city

    Attributes:
        name (CharField): The name of the city.
        code (IntegerField): The code of the city.
        big_city (BigCity): The big city of the city.
    """
    name = models.CharField(verbose_name='نام شهر', max_length=127)
    code = models.IntegerField(verbose_name='کد شهر')
    big_city = models.ForeignKey(
        BigCity,
        related_name='city',
        on_delete=models.CASCADE)

    class Meta:
        ordering = ('id',)
        verbose_name = "شهر"
        verbose_name_plural = "شهر ها"

    @property
    def value(self):
        return self.id

    @property
    def label(self):
        return self.name

    def __str__(self):
        return f'{self.name} ({self.big_city.state.name})'


class DashboardBannerManager(models.Manager):
    def get_banners(self, banner_status):
        return self.filter(publish_status=banner_status)


class DashboardBanner(models.Model):
    """Banner images in shop dashboard

    After shop owners logs in their dashboard, they can see some banners that are published by staff. 

    Attributes:
        image (ImageField): The image of the banner.
        url (URLField): The url of the banner which user will redirect to after clicking.
        staff_user (User): The user who created the banner.
        created_datetime (DateTimeField): The date and time of the creation of the banner.
        publish_status (CharField): The status of the banner. Statuses can be found in :attr:`PublishStatuses`.
    """
    class Meta:
        verbose_name = 'بنر داشبرد'
        verbose_name_plural = 'بنرهای داشبرد'

    class PublishStatuses(models.TextChoices):
        PUBLISH = 'pub', 'منتشر شده'
        PREVIEW = 'prv', 'پیش‌نمایش'

    def __str__(self):
        return self.image.name

    image = models.ImageField(
        verbose_name='عکس بنر',
        upload_to=PathAndRename('media/Pictures/Dashboard/Banner/'))
    url = models.URLField(max_length=100, verbose_name='لینک بنر', null=True)
    staff_user = models.ForeignKey(
        User,
        verbose_name='کارشناس',
        on_delete=models.SET_NULL,
        null=True,
        related_name='dashboard_banners')
    created_datetime = models.DateTimeField(
        verbose_name='تاریخ ثبت', auto_now=False, auto_now_add=True)
    publish_status = models.CharField(
        max_length=3, choices=PublishStatuses.choices,
        default=PublishStatuses.PUBLISH)
    objects = DashboardBannerManager()


class LandingPageSchemaManager(models.Manager):
    def is_mobile(self, request):
        return 'Mobile' in request.META['HTTP_USER_AGENT']

    def get_for_device(self, request):
        return self.get_queryset()

    def get_published_schema(self, request):
        return self.get_for_device(request).filter(
            publish_status=LandingPageSchema.PublishStatuses.PUBLISH,
            shoppageschema=None).order_by('order')


class LandingPageSchema(models.Model):
    class Meta:
        verbose_name = 'برنامه بندی صفحه اول'
        verbose_name_plural = 'برنامه بندی صفحه اول'

    class PublishStatuses(models.TextChoices):
        PUBLISH = 'pub', 'منتشر شده'
        PREVIEW = 'prv', 'پیش‌نمایش'

    class ComponentTypes(models.IntegerChoices):
        SLIDER = 1, 'اسلایدر'
        ONE_BANNER = 2, '1 بنر'
        TWO_BANNER = 3, '2 بنر'
        THREE_BANNER = 4, '3 بنر'
        FOUR_BANNER = 5, '4 بنر'
        PRODUCT_ROW = 6, 'ردیف محصول'
        PRODUCT_ROW_AMAZING = 7, 'ردیف محصول شگفت انگیز'
        ICON = 8, 'آیکن'

    def __str__(self):
        return 'type:{}, order:{}, data:{}'.format(
            self.get_component_type_display(),
            self.order, self.data)

    component_type = models.IntegerField(
        verbose_name='نوع برنامه بندی',
        choices=ComponentTypes.choices,
        default=ComponentTypes.ONE_BANNER)
    data = models.URLField(verbose_name='داده ها', max_length=255)
    title = models.CharField(
        verbose_name='عنوان',
        max_length=127,
        null=True,
        blank=True)
    subtitle = models.CharField(
        verbose_name='زیر عنوان',
        max_length=127,
        null=True,
        blank=True)
    url = models.URLField(
        max_length=255,
        verbose_name='لینک',
        null=True,
        blank=True)
    background_color = ColorField(
        verbose_name='رنگ پس زمینه',
        null=True,
        blank=True)
    image = models.ImageField(verbose_name='عکس', upload_to=PathAndRename(
        'media/Pictures/LandingPage/Schema/'), null=True, blank=True)
    order = models.IntegerField(verbose_name='ترتیب', default=0)
    staff_user = models.ForeignKey(
        User,
        verbose_name='کارشناس',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='landing_page_schemas')
    created_datetime = models.DateTimeField(
        verbose_name='تاریخ ثبت', auto_now=False, auto_now_add=True)
    publish_status = models.CharField(
        max_length=3, choices=PublishStatuses.choices,
        default=PublishStatuses.PUBLISH)
    is_mobile = models.BooleanField(
        verbose_name='دستگاه موبایل است؟', default=True)
    objects = LandingPageSchemaManager()


class ShopPageSchemaManager(LandingPageSchemaManager):
    def get_published_schema(self, request, shop_id):
        return self.get_for_device(request).filter(
            shop=shop_id, publish_status=ShopPageSchema.PublishStatuses.PUBLISH).order_by('order')

    def get_unpublished_schema(self, request, shop_id):
        return self.get_for_device(request).filter(
            shop=shop_id, publish_status=ShopPageSchema.PublishStatuses.PREVIEW).order_by('order')


class ShopPageSchema(LandingPageSchema):
    class Meta:
        verbose_name = 'برنامه بندی صفحه حجره دار'
        verbose_name_plural = 'برنامه بندی صفحه حجره دار'

    shop = models.ForeignKey(
        Shop,
        verbose_name='فروشگاه',
        on_delete=models.CASCADE,
        related_name='shop_page_schemas')
    objects = ShopPageSchemaManager()


class UserImage(models.Model):
    """Images that a user uploaded for different purposes.

    This model mainly serves as a way to store images that a shop owner uploaded for his/her shop landing page.
    Yet, you can use it for other purposes as well.

    Attributes:
        profile (Profile): Profile of the user who uploaded the image. Unlike other models, this model has link to the
            profile model which reduce the consistency of the database.
        image (ImageField): Image field.
        image_thumbnail (ImageField): Thumbnail of the image.
        publish (BooleanField): Whether the image is published or not.
        title (CharField): Title of the image.
        description (TextField): Description of the image.
        created_at (DateTimeField): DateTime of the creation of the image.
        updated_at (DateTimeField): DateTime of the last update of the image.
    """
    class Meta:
        verbose_name = 'تصویر بارگذاری شده کاربر'
        verbose_name_plural = 'تصویر بارگذاری شده کاربر'

    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='uploaded_images',
        verbose_name='کاربر')
    title = models.CharField(max_length=100, verbose_name='عنوان', blank=True)
    description = models.TextField(verbose_name='توضیحات', blank=True)
    image = models.ImageField(
        verbose_name='تصویر بارگذاری شده',
        upload_to=PathAndRename('media/Pictures/User/UploadedImages/'))
    image_thumbnail = ImageSpecField(
        source='image', processors=[ResizeToFill(180, 180)],
        format='JPEG', options={'quality': 60})
    publish = models.BooleanField(verbose_name='منتشر شده?', default=True)
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name='تاریخ ویرایش')

    def __str__(self):
        return f'{self.profile.MobileNumber}: {self.title} ({self.image})'


@receiver(models.signals.post_delete, sender=UserImage)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """Deletes file from filesystem"""
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)


@receiver(models.signals.pre_save, sender=UserImage)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """Deletes file from filesystem if it's changed"""
    if not instance.pk:
        return False
    try:
        old_image = UserImage.objects.get(pk=instance.pk).image
    except UserImage.DoesNotExist:
        return False
    new_image = instance.image
    if not old_image == new_image:
        if os.path.isfile(old_image.path):
            os.remove(old_image.path)


class LandingPage(models.Model):
    class Meta:
        verbose_name = 'صفحه فرود'
        verbose_name_plural = 'صفحه فرود'
        ordering = ('-id',)

    class Statuses(models.IntegerChoices):
        INACTIVE = 0, 'غیرفعال'
        ACTIVE = 1, 'فعال'

    slug = models.CharField(
        max_length=100,
        verbose_name='نام صفحه',
        unique=True)
    status = models.IntegerField(
        verbose_name='وضعیت',
        choices=Statuses.choices,
        default=Statuses.ACTIVE)
    staff = models.ForeignKey(
        User,
        verbose_name='کارشناس',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='landing_pages')
    page_data = models.TextField(
        verbose_name=_('داده‌های صفحه'),
        null=True, blank=True)
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name='تاریخ ویرایش')

    def __str__(self):
        return self.page_slug


class LandingImage(models.Model):
    class Meta:
        verbose_name = 'تصویر صفحه فرود'
        verbose_name_plural = 'تصویر صفحه فرود'

    landing_page = models.ForeignKey(
        LandingPage,
        verbose_name='صفحه فرود',
        on_delete=models.CASCADE,
        related_name='images')
    image = models.ImageField(
        verbose_name='تصویر',
        upload_to=PathAndRename('media/Pictures/Landing/'))
    image_thumbnail = ImageSpecField(
        source='image', processors=[ResizeToFill(180, 180)],
        format='JPEG', options={'quality': 60})
    staff = models.ForeignKey(
        User,
        verbose_name='کارشناس',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='landing_images')
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name='تاریخ ویرایش')

    def __str__(self):
        return f'{self.landing_page.page_slug}: {self.image}'
