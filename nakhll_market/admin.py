from django.contrib import admin
from .models import  Tag, Market, MarketBanner, SubMarket, SubMarketBanner,BankAccount, Category ,PostRange, Shop, ShopBanner, ShopMovie, Attribute, AttrPrice, AttrProduct, Product, ProductBanner, ProductMovie, Comment, Profile, Review, Survey, Slider, Option_Meta, Message, Newsletters, Pages ,Alert ,Field, User_Message_Status, UserPoint
from django.contrib import admin

admin.site.site_header = 'مدیریت بازار نخل '

#tag admin panel
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display=('Title','Description')
    search_fields=('Title','Description')
    ordering=['id']
#-------------------------------------------------
class BankAccountInline(admin.TabularInline):
    model=BankAccount
    list_display=('AccountOwner','CreditCardNumber','ShabaBankNumber',)
    
#profile admin panel
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display=('FK_User','MobileNumber','BrithDay','UserReferenceCode','Point')
    readonly_fields = ('UserReferenceCode',)
    list_filter=('BrithDay',)
    ordering=['ID','BrithDay','Point','UserReferenceCode']
    search_fields=('MobileNumber','UserReferenceCode',)
    inlines=[BankAccountInline]
#-------------------------------------------------
#market admin panel
class MarketBannerInline(admin.StackedInline):
    model=MarketBanner
    extra=1

@admin.register(Market)
class MarketAdmin(admin.ModelAdmin):
    list_display=('Title','Slug','DateCreate','Available','Publish')
    list_filter=('Publish','Available','DateCreate','DateUpdate')
    search_fields=('Title','Slug')
    ordering=['ID','DateCreate','DateUpdate']
    prepopulated_fields={'Slug':('Title',)}
    inlines=[MarketBannerInline]
#-------------------------------------------------
#SubMarket admin panel
class SubMarketBannerInline(admin.StackedInline):
    model=SubMarketBanner
    extra=1

@admin.register(SubMarket)
class SubMarketAdmin(admin.ModelAdmin):
    list_display=('Title','Slug','DateCreate','Available','Publish')
    list_filter=('Publish','Available','DateCreate','DateUpdate')
    search_fields=('Title','Slug')
    ordering=['ID','DateCreate','DateUpdate']
    prepopulated_fields={'Slug':('Title',)}
    inlines=[SubMarketBannerInline]
#-------------------------------------------------
#Shop admin panel
class ShopBannerInline(admin.StackedInline):
    model=ShopBanner
    extra=1

class ShopMovieInline(admin.StackedInline):
    model=ShopMovie
    extra=1


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display=('Title','Slug','City','State','Point','DateCreate','Available','Publish',)
    list_filter=('City','State','Publish','Available','DateCreate','DateUpdate')
    search_fields=('Title','Slug')
    ordering=['ID','DateCreate','DateUpdate']
    inlines=[ShopBannerInline, ShopMovieInline,]
#-------------------------------------------------
#Attribute admin panel
@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    list_display=('Title','Unit','Publish',)
    list_filter=('Publish',)
    search_fields=('Title',)
    ordering=['id']
#-------------------------------------------------
#AttrPrice admin panel
@admin.register(AttrPrice)
class AttrPriceAdmin(admin.ModelAdmin):
    list_display=('FK_Product','Value','ExtraPrice','Unit',)
    ordering=['id','FK_Product','Value','ExtraPrice']
#-------------------------------------------------
# Product admin panel
class AttrProductInline(admin.TabularInline):
    model=AttrProduct
    extra=3

class ProductBannerInline(admin.StackedInline):
    model=ProductBanner
    extra=1

class ProductMovieInline(admin.StackedInline):
    model=ProductMovie
    extra=1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display=('Title','Slug','Bio','Price','Status','DateCreate','Publish')
    list_filter=('Status','Publish','Available','DateCreate','DateUpdate')
    search_fields=('Title','Slug','Description','Bio','Story')
    ordering=['ID','DateCreate','DateUpdate']
    inlines=[AttrProductInline, ProductBannerInline, ProductMovieInline]
#-------------------------------------------------
#Comment admin panel
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display=('Type','Description','FK_User','Available','DateCreate')
    list_filter=('Type','Available','DateCreate',)
    search_fields=('Type','Slug','Description')
    ordering=['DateCreate','id']
#-------------------------------------------------
#Review admin panel
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display=('Title','FK_Product','FK_User','DateCreate','Available')
    list_filter=('Available','DateCreate')
    search_fields=('Title','Positive','Negative','Description')
    ordering=['DateCreate','id']
#-------------------------------------------------
#Category admin panel
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display=('Title','Slug','FK_SubCategory','Publish','DateCreate')
    list_filter=('Available','Publish','DateCreate','DateUpdate')
    search_fields=('Title','Slug','Description')
    ordering=['DateCreate','id','Available','Publish']
#-------------------------------------------------
# Message admin panel
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display=('Title','Text','FK_Sender','Date')
    list_filter=('Date','FK_Sender')
    search_fields=('Title','Text')
    ordering=['id','Title','Date']
#-------------------------------------------------
# User_Message_Status admin panel
@admin.register(User_Message_Status)
class User_Message_StatusAdmin(admin.ModelAdmin):
    list_display=('FK_User','SeenStatus')
    ordering=['id']
#-------------------------------------------------
#PostRange admin panel
@admin.register(PostRange)
class PostRangeAdmin(admin.ModelAdmin):
    list_display=('State','City','BigCity')
    list_filter=('State','City', 'BigCity')
    search_fields=('State','City','BigCity')
    ordering=['id','State','City','BigCity']
#-------------------------------------------------
#Slider admin panel
@admin.register(Slider)
class SliderAdmin(admin.ModelAdmin):
    list_display=('Title','Description','Location','DateCreate','Publish')
    list_filter=('Location','DateCreate','DtatUpdate','Publish')
    ordering=['DateCreate','id','Publish','Title','Location']
#----------------------------------------------------------------------------------------------------------------------------------
#Option_Meta admin panel
@admin.register(Option_Meta)
class Option_MetaAdmin(admin.ModelAdmin):
    list_display=('id', 'Title', 'Description', 'Value_1', 'Value_2',)
    ordering=['id','Title','Value_1', 'Value_2',]
#----------------------------------------------------------------------------------------------------------------------------------
#Newsletters admin panel
@admin.register(Newsletters)
class NewslettersAdmin(admin.ModelAdmin):
    list_display=('id','Email')
    search_fields=('Email',)
    ordering=['id']
#-------------------------------------------------
#pages admin panel
@admin.register(Pages)
class PagesAdmin(admin.ModelAdmin):
    list_display=('Title','Slug','DateCreate','DtatUpdate','Publish','FK_User',)
    list_filter=('Publish','DateCreate','DtatUpdate',)
    search_fields=('Title','Slug','Content',)
    ordering=['id','DateCreate',]
#-------------------------------------------------
#Alert admin panel
@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display=('Part','Slug','Seen','DateCreate','Description',)
    list_filter=('Seen','Status','DateCreate','DateCreate','DateUpdate')
    search_fields=('FK_Field','Description','Content',)
    ordering=['id','DateCreate',]