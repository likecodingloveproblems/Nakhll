import re
from typing import Any, Dict
from django.contrib.sessions.backends.db import SessionStore
from django.core.files.storage import FileSystemStorage
from django.db.models.aggregates import Sum
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.db.models import Q, F, Count
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect, HttpResponse
from django.conf import settings
from django.urls import reverse
from django.views import generic
from ipware import get_client_ip
from datetime import datetime, date, timedelta
import jdatetime
from django.contrib import messages
from django.utils.datastructures import MultiValueDictKeyError
from django.utils import timezone
from django import template
from itertools import chain
from operator import attrgetter
import random, string, os
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from kavenegar import *
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.conf import settings
from nakhll.settings import KAVENEGAR_KEY


from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin

from django.contrib.auth.models import User
from django.contrib.auth.models import Group 

from django.contrib.postgres.search import TrigramSimilarity

from .models import AmazingProduct, Tag
from .models import Market
from .models import MarketBanner
from .models import SubMarket
from .models import SubMarketBanner
from .models import BankAccount
from .models import Category
from .models import PostRange
from .models import Shop
from .models import ShopBanner
from .models import ShopMovie
from .models import Attribute
from .models import AttrPrice
from .models import AttrProduct
from .models import Product
from .models import ProductBanner
from .models import ProductMovie
from .models import Comment, ShopComment
from .models import Profile
from .models import Review
from .models import Survey
from .models import Slider
from .models import Message
from .models import Option_Meta
from .models import Pages
from .models import Newsletters
from .models import Alert
from .models import Field
from .models import Note
from .models import PageViews, User_View, ShopViews, Date_View
from sms.models import SMS
from my_auth.models import UserphoneValid
from Payment.models import Wallet, Factor ,FactorPost, Coupon

from .forms import Login, CheckEmail
from .profileviews import ProfileDashboard

# Get Username
User_username = None

# Forget Password Code
fogetpasswordcode = None

# Rigister Code
register = None

# phone_number Offline
offphone = None

# Get User IP
def visitor_ip_address(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

#--------------------------------------------------------------------------------------------------------------------------------


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


# Get Shop Number Of Visits
def Get_Shop_Visits_Count(request, obj_id):
    try:
        # Get Page View
        if ShopViews.objects.filter(FK_Shop_id = obj_id).exists():
            this_shop = ShopViews.objects.get(FK_Shop_id = obj_id)
            # Get This IP Info
            if this_shop.FK_Viewer.filter(User_Ip = visitor_ip_address(request)).exists():
                # Get This IP 
                this_ip = this_shop.FK_Viewer.get(User_Ip = visitor_ip_address(request))
                # Check Date
                date_format = "%Y-%m-%d"
                a = datetime.strptime(str(date.today()), date_format)
                b = datetime.strptime(str(this_ip.DateTime.date()), date_format)
                delta = a - b
                # If Delta > 24H
                if delta.days >= 1:
                    this_shop.Total_View = str(int(this_shop.Total_View) + 1)
                    this_ip.DateTime = datetime.now()
                    this_ip.Total_View = str(int(this_ip.Total_View) + 1)
                    this_ip.save()
                    this_shop.save()
                    # Set Date
                    if this_shop.FK_Date.filter(Date = date.today()).exists():
                        this_date = this_shop.FK_Date.get(Date = date.today())
                        this_date.Count = str(int(this_date.Count) + 1)
                        this_date.save()
                    else:
                        this_date = Date_View.objects.create()
                        this_shop.FK_Date.add(this_date)
                    view_count = this_shop.Total_View
                else:
                    this_ip.Total_View = str(int(this_ip.Total_View) + 1)
                    this_ip.save()
                    # Set Date
                    if not this_shop.FK_Date.filter(Date = date.today()).exists():
                        this_date = Date_View.objects.create()
                        this_shop.FK_Date.add(this_date)
                    view_count = this_shop.Total_View  
            else:
                this_shop.FK_Viewer.add(User_View.objects.create(User_Ip = visitor_ip_address(request)))
                # Set Date
                if this_shop.FK_Date.filter(Date = date.today()).exists():
                    this_date = this_shop.FK_Date.get(Date = date.today())
                    this_date.Count = str(int(this_date.Count) + 1)
                    this_date.save()
                else:
                    this_date = Date_View.objects.create()
                    this_shop.FK_Date.add(this_date)

                this_shop.Total_View = str(int(this_shop.Total_View) + 1)
                this_shop.save()
                view_count = this_shop.Total_View
        else:
            this_shop = ShopViews.objects.create(FK_Shop_id = obj_id)
            this_shop.FK_Viewer.add(User_View.objects.create(User_Ip = visitor_ip_address(request)))
            # Set Date
            if this_shop.FK_Date.filter(Date = date.today()).exists():
                this_date = this_shop.FK_Date.get(Date = date.today())
                this_date.Count = str(int(this_date.Count) + 1)
                this_date.save()
            else:
                this_date = Date_View.objects.create()
                this_shop.FK_Date.add(this_date)
            view_count = this_shop.Total_View
        return view_count
    except:
        return 'عدم دسترسی'
        


def index(request):
    if request.user.is_authenticated:
        this_profile = get_object_or_404(Profile, FK_User = request.user)
        this_inverntory = get_object_or_404(Wallet, FK_User = request.user).Inverntory
    else:
        this_profile = None
        this_inverntory = None
    # Get Menu Item
    options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
    # Get Nav Bar Menu Item
    navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
    # ------------------------------------------------------------------------
    # Get All Products
    pubproduct = Product.objects.filter(Publish = True, Available = True, OldPrice = '0', Status__in = ['1', '2', '3']).order_by('-DateCreate')[:12]
    pubproductoldquery = Product.objects.filter(Publish = True, Available = True, OldPrice = '0', Status__in = ['1', '2', '3'])
    numpubproductold = pubproductoldquery.count()
    pubproductold = []
    for i in random.sample(range(0,numpubproductold), 16):
        pubproductold.append(pubproductoldquery[i])
    # Get All Discounted Product
    dis_product = Product.objects.filter(Publish = True, Available = True, Status__in = ['1', '2', '3']).exclude(OldPrice='0').order_by('-DateCreate')[:16]
    # Get Index Sliders
    pubsliders = Slider.objects.filter(Location = 1, Publish = True)
    # Get All Categories
    categories_id = list(Category.objects.filter(Publish = True, Available = True, FK_SubCategory = None)\
        .values_list('id', flat=True))
    categories = Category.objects\
        .filter(Publish = True, Available = True, FK_SubCategory = None)\
        .filter(pk__in=random.sample(categories_id, 12))
    # Get All Index Advertising - Buttom
    pubbuttomadvsliders = Slider.objects.filter(Location = 2, Publish = True)
    # Get All Index Advertising - Center
    pubcenteradvsliders = Slider.objects.filter(Location = 3, Publish = True)
    # Get All Shops
    pubshopsquery = Shop.objects.filter(Publish = True, Available = True)
    numpubshops = pubshopsquery.count()
    pubshops = []
    for i in random.sample(range(0, numpubshops), 12):
        pubshops.append(pubshopsquery[i])

    # Discounted Product
    discounted_product = Product.objects\
        .get_one_most_discount_precenetage_available_product_random()

    # shop 
    most_sale_shops = Shop.objects.most_last_week_sale_shops()

    # amazing products
    amazing_products = AmazingProduct.objects.get_amazing_products()

    context = {
        'This_User_Profile':this_profile,
        'This_User_Inverntory': this_inverntory,
        'Options': options,
        'MenuList':navbar,                          
        'Products' : pubproduct,
        'Productsold':pubproductold,
        'Sliders':pubsliders,
        'Categories':categories,
        'ButtomAdvertisings':pubbuttomadvsliders,
        'CenterAdvertisings':pubcenteradvsliders,
        'Shops':pubshops,
        'DisProduct':discounted_product,
        'AllDisProduct':dis_product,
        'MostSaleShop':most_sale_shops,
        'AmazingProducts':amazing_products,
    }

    # add console.log feature to tell about coming context from back to UI for UI team (only works if we are in debug mode)
    if settings.DEBUG:
        full_info = []
        for key, value in context.items():
            item_info = [key, value]
            forbiden_chars = ''''<>[]'''
            item_info_str = str(item_info)
            for char in forbiden_chars:
                item_info_str = item_info_str.replace(char,"")
            full_info.append(item_info_str)
        
        context['context_in_list'] = full_info
        return render(request, 'nakhll_market/pages/index.html', context)
    
    return render(request, 'nakhll_market/pages/index.html', context)


# get shop category
class get_shop_other_info:
    def run (self, request, shop):
        shop_submarkets = shop.FK_SubMarket.all()
        if shop_submarkets:
            # Get Shop First SubMarket
            this_shop_subMarket = shop_submarkets[0]
            # Get Shop First SubMarket Market
            this_shop_market = this_shop_subMarket.FK_Market
        else:
            # Get Shop First SubMarket
            this_shop_subMarket = None
            # Get Shop First SubMarket Market
            this_shop_market = None
        # ---------------------------------------------------------------------------------
        # Total Sell
        # total_sell = 0
        # # Get All Factor Item Is Product In AllProduct List
        # for item in FactorPost.objects.filter(FK_Product__in = shop.get_all_products(), ProductStatus__in = ['2', '3']):
        #     total_sell += item.ProductCount
        # ----------------------------------------------------------------------------------
        shop_view = Get_Shop_Visits_Count(request, shop.ID)

        # Set Result
        result = {
            "this_shop_subMarket": this_shop_subMarket,
            "this_shop_market":this_shop_market,
            "view":shop_view,
        }
        return result

# Get All Markets
def market(request):
    # Get User Info
    if request.user.is_authenticated:
        
        this_profile = Profile.objects.get(FK_User=request.user)
        this_inverntory = request.user.WalletManager.Inverntory
    else:
        this_profile = None
        this_inverntory = None
    # Get Menu Item
    options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
    # Get Nav Bar Menu Item
    navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
    # ---------------------------------------------------------------------
    # Build Class
    class Markets_Submarkets:
        def __init__(self, item, sub_item):
            self.Market = item
            self.SubMarkets = sub_item
    # Set Date
    markets = []
    for item in Market.objects.filter(Publish = True):
        sub_items = SubMarket.objects.filter(FK_Market = item, Publish = True)
        markets.append(Markets_Submarkets(item, sub_items))
    # Get All Market Sliders
    pubmarketsliders = Slider.objects.filter(Location=4, Publish=True)

    context = {
        'This_User_Profile':this_profile,
        'This_User_Inverntory': this_inverntory,
        'Options': options,
        'MenuList':navbar,
        'MarketList': markets,
        'Sliders':pubmarketsliders,
    }

    return render(request, 'nakhll_market/pages/market.html', context)

# Get SubMarket Detail
def submarket(request, submarket_slug):
    # Get User Info
    if request.user.is_authenticated:
        
        this_profile = Profile.objects.get(FK_User=request.user)
        this_inverntory = request.user.WalletManager.Inverntory
    else:
        this_profile = None
        this_inverntory = None
    # Get Menu Item
    options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
    # Get Nav Bar Menu Item
    navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
    # ------------------------------------------------------------------------
    # Get SubMarket Detail
    submarket = get_object_or_404(SubMarket, Slug = submarket_slug)
    # Get Publishe Shops
    pubshops = Shop.objects.filter(Available = True, Publish = True, FK_SubMarket = submarket)

    context = {
        'This_User_Profile':this_profile,
        'This_User_Inverntory': this_inverntory,
        'Options': options,
        'MenuList':navbar,
        'SubMarket':submarket,
        'Shops':pubshops,
    }

    return render(request, 'nakhll_market/pages/submarket.html', context)


# Get Shop Detail
def ShopsDetail(request, shop_slug, msg = None):
    # Get User Info
    if request.user.is_authenticated:
        
        this_profile = Profile.objects.get(FK_User=request.user)
        this_inverntory = request.user.WalletManager.Inverntory
    else:
        this_profile = None
        this_inverntory = None
    # Get Menu Item
    options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
    # Get Nav Bar Menu Item
    navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
    # -------------------------------------------------------------------
    # Get This Shop
    shop = get_object_or_404(Shop, Slug = shop_slug)
    # Get Date Detail
    date_format = "%Y-%m-%d"
    a = datetime.strptime(str(date.today()), date_format)
    b = datetime.strptime(str(shop.DateCreate.date()), date_format)
    delta = a - b
    # Get All Products
    this_shop_product = shop.get_all_products_for_view()
    # Get All Shop`s Banner
    pubshopbanner = shop.get_banners()
    # Get All Shop Comment
    this_shop_publish_comments = shop.get_comments()
    # get other info
    other_info = get_shop_other_info().run(request, shop)
    # Get Total Sell
    # sell_total = other_info["total_sell"]
    # Get Page View
    # view_count = other_info["view"]
    # -------------------------------------------------------------------
    this_shop_market = other_info["this_shop_market"]
    this_shop_subMarket = other_info["this_shop_subMarket"]
    # -------------------------------------------------------------------
    if msg == None:
        show = False
        massege = ''
    else:
        show = True
        massege = msg

    productpaginator = Paginator (this_shop_product, 16)
    page = request.GET.get('page')

    this_shop_product = productpaginator.get_page(page)
    
    context = {
        'This_User_Profile':this_profile,
        'This_User_Inverntory': this_inverntory,
        'Options': options,
        'MenuList':navbar,
        'This_Shop_First_SubMarket_Market': this_shop_market,
        'This_Shop_First_SubMarket': this_shop_subMarket,
        'Comments':this_shop_publish_comments,
        'Shop':shop,
        'DateNow':delta.days,
        'Products':this_shop_product,
        'ShopBanner':pubshopbanner,
        # 'View_Count':view_count,
        # 'Sell_Count':sell_total,
        'ShowAlart':show,
        'AlartMessage':massege,
    }

    return render(request, 'nakhll_market/pages/shop_detail.html', context)

# Show All Shops
def AllShop(request):
    # Get User Info
    if request.user.is_authenticated:
        
        this_profile = Profile.objects.get(FK_User=request.user)
        this_inverntory = request.user.WalletManager.Inverntory
    else:
        this_profile = None
        this_inverntory = None
    # Get Menu Item
    options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
    # Get Nav Bar Menu Item
    navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
    # ---------------------------------------------------------------------
    # Build Class
    class Shop_item:
        def __init__(self, item, item_market, item_submarket):
            self.Shop = item
            self.Market = item_market
            self.SubMarket = item_submarket
    # Get All Shops
    shops = []
    for item in Shop.objects.filter(Publish = True, Available = True).order_by('-DateCreate'):
        if Product.objects.filter(FK_Shop = item, Publish = True, Available = True).exists():
            if item.FK_SubMarket.all().count() != 0:
                # Get Shop First SubMarket
                this_shop_subMarket = item.FK_SubMarket.all()[0]
                # Get Shop First SubMarket Market
                this_shop_market = item.FK_SubMarket.all()[0].FK_Market
            else:
                # Get Shop First SubMarket
                this_shop_subMarket = None
                # Get Shop First SubMarket Market
                this_shop_market = None
            shops.append(Shop_item(item, this_shop_market, this_shop_subMarket))
    # Set Paginator
    shoppaginator = Paginator (shops, 12)
    page = request.GET.get('page')
    shops = shoppaginator.get_page(page)

    context = {
        'This_User_Profile':this_profile,
        'This_User_Inverntory': this_inverntory,
        'Options': options,
        'MenuList':navbar,
        'Shops':shops,
    }

    return render(request, 'nakhll_market/pages/allshops.html', context)

# Get Category Detail
def category(request, slug, status, delta_price):
    if request.user.is_authenticated:
        
        this_profile = Profile.objects.get(FK_User=request.user)
        this_inverntory = request.user.WalletManager.Inverntory
    else:
        this_profile = None
        this_inverntory = None
    # Get Menu Item
    options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
    # Get Nav Bar Menu Item
    navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
    # -------------------------------------------------------------------
    # Get Category
    all_category = slug.split('&')
    category_list_id = []
    all_category_ = ''
    all_category_title = ''
    allproducts = []
    if len(all_category) != 0:
        for item in all_category:
            if Category.objects.filter(Slug = item).exists():
                category_list_id.append(str(Category.objects.get(Slug = item).id))
        # Get Publish Products
        for item in Product.objects.filter(Available = True, Publish = True, Status__in = ['1', '2', '3'], FK_Category__in = category_list_id).order_by('-DateCreate'):
            allproducts.append(item) 
        for item in Product.objects.filter(Available = True, Publish = True, Status = '4', FK_Category__in = category_list_id).order_by('-DateCreate'):
            allproducts.append(item)
    # Get Category Title
    if len(all_category) != 0:
        for item in all_category:
            if Category.objects.filter(Slug = item).exists():
                all_category_ += Category.objects.get(Slug = item).Title + ' '
                all_category_title += Category.objects.get(Slug = item).Title + '-'
    # --------------------------------------------------------------------
    Max = None
    Min = None
    sort = None
    # Get Product Price
    def GetPrice(item):
        return int(item.Price)

    # Get Product Create Date
    def GetDate(item):
        return item.DateCreate

    # Product Add To List
    Product_List = []
    for item in allproducts:
        Product_List.append(item)

    if delta_price != 'none':
        # Get Price Detial
        price = delta_price.split('-')
        Max = str(price[1])
        Min = str(price[0])

        this_list =  []
        for item in Product_List:
            if (Min != '100000') and (Max == '50000000'):
                if int(item.Price) >= int(Min):
                    this_list.append(item)
            elif (Min == '100000') and (Max != '50000000'):
                if int(item.Price) <= int(Max):
                    this_list.append(item)
            else:
                if (int(item.Price) >= int(Min)) and (int(item.Price) <= int(Max)):
                    this_list.append(item)
            
            Product_List = this_list
    else:
        Max = '50000000'
        Min = '100000'

    # Get Sort Status
    if status == 'newest':
        Product_List.sort(reverse = True, key = GetDate)
    elif status == 'oldest':
        Product_List.sort(key = GetDate)
    elif status == 'down_price':
        Product_List.sort(reverse = True, key = GetPrice)
    elif status == 'up_price':
        Product_List.sort(key = GetPrice)
  
    sort = status
    # ------------------------------------------------------------------
    # Build Class
    class Item:
        def __init__(self, item, sub_item, item_status):
            self.Category = item
            self.SubCategory = sub_item
            self.Status = item_status
    
    # Build Class
    class Sub_Item:
        def __init__(self, item, item_status):
            self.Category = item
            self.Status = item_status

    this_category = []

    for item in Category.objects.filter(Publish = True):
        if item.FK_SubCategory == None:
            this_sub = []
            for user in Category.objects.filter(Publish = True, FK_SubCategory = item):
                if str(user.id) in category_list_id:
                    this_sub.append(Sub_Item(user, True))
                else:
                    this_sub.append(Sub_Item(user, False))

            if str(item.id) in category_list_id:
                this_category.append(Item(item, this_sub, True))
            else:
                this_category.append(Item(item, this_sub, False))

    Product_List = list(dict.fromkeys(Product_List))
    
    productpaginator = Paginator (Product_List, 15)
    page = request.GET.get('page')

    Product_List = productpaginator.get_page(page)

    context = {
        'This_User_Profile':this_profile,
        'This_User_Inverntory': this_inverntory,
        'Options': options,
        'MenuList':navbar,
        'all_category':all_category_,
        'all_category_title':all_category_title,
        'Products':Product_List,
        'Categories':this_category,
        'Sort':sort,
        'MaxValue':Max,
        'MinValue':Min,
    }

    return render(request, 'nakhll_market/pages/category.html', context)

# Get Tag Detail
def TagDetail(request, tag_slug):
    #Get User Info
    user=User.objects.all()
    # Get User Profile
    profile=Profile.objects.all()
    # Get Wallet Inverntory
    wallets=Wallet.objects.all()
    # Get Markets
    markets=Market.objects.all()
    # Get Publish Markets
    pubmarkets=markets.filter(Publish=True)
    # Get All Products
    products=Product.objects.all()
    # Get Publish Products
    pubproducts=products.filter(Publish=True)
    # Get All Shops
    shops=Shop.objects.all()
    # Get Publish Shops
    pubshops=shops.filter(Publish=True)
    # Get Tag
    tag=Tag.objects.get(Slug=tag_slug)
    # Get Menu Item
    options=Option_Meta.objects.filter(Title='index_page_menu_items')
    # Get Nav Bar Menu Item
    navbar=Option_Meta.objects.filter(Title='nav_menu_items')

    context = {
        'Users':user,
        'Profile':profile,
        'Wallet': wallets,
        'Tag':tag,
        'Markets':pubmarkets,
        'Products':pubproducts,
        'Shops':pubshops,
        'Options': options,
        'MenuList':navbar,
    }

    return render(request, 'nakhll_market/pages/tag.html', context)


# Get Product Total Sell
class Product_Total_Sell:
    def run(self, product):
        # Total Sell
        total_sell = 0
        # Get All Factor Item Is Product = This Product
        sell_list = FactorPost.objects.filter(FK_Product = product, ProductStatus__in = ['2', '3'])
        for item in sell_list:
            total_sell += item.ProductCount
        return total_sell


# Get Related products
class get_related_products:
    def run(self, product):
        # Get Product
        this_product = product.get_related_products()
        if len(this_product) > 0:
            if len(this_product) < 12:
                return this_product
            else:
                # Get Random Product
                random_related_product = []
                i = 0
                while(i < 12):
                    random_product = random.randint(0, len(this_product))
                    if random_product == len(this_product):
                        random_related_product.append(this_product[random_product - 1])
                        this_product.remove(this_product[random_product - 1])
                    else:
                        random_related_product.append(this_product[random_product])
                        this_product.remove(this_product[random_product])
                    i += 1
                return random_related_product
            return this_product



# Get Products
def ProductsDetail(request, shop_slug, product_slug, status = None, msg = None):
    # Get User Info
    if request.user.is_authenticated:
        
        this_profile = Profile.objects.get(FK_User=request.user)
        this_inverntory = request.user.WalletManager.Inverntory
    else:
        this_profile = None
        this_inverntory = None
    # Get Menu Item
    options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
    # Get Nav Bar Menu Item
    navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
    # -----------------------------------------------------------------------
    # Get All Products
    this_product = get_object_or_404(Product, Slug = product_slug)
    # Get Product`s Shop
    this_shop = get_object_or_404(Shop, Slug = shop_slug)
    # Get All AttrbitProduct
    attarproduct = AttrProduct.objects.filter(FK_Product = this_product, Available = True)
    # Get All AttributePrice
    attrprice = AttrPrice.objects.filter(FK_Product = this_product, Publish = True)
    # Get All Product Comment
    pubcomments = Comment.objects.filter(FK_Product = this_product, Available = True)
    # Get All Product Review
    pubreviews = Review.objects.filter(FK_Product = this_product, Available = True)
    # Get All Product Banner
    pubbanner = ProductBanner.objects.filter(FK_Product = this_product, Available = True, Publish = True)
    # Get Related products
    try:
        this_product_related = get_related_products().run(this_product)
    except:
        this_product_related = []
    # -----------------------------------------------------------------
    # Get Page View
    # view_count = 
    CheckView(request, this_product.Slug, '1')
    # Get Total Sell
    # total_sell = Product_Total_Sell().run(this_product)
    # -------------------------------------------------------------------------------------------------------
    if status == None:
        show = False
        massege = ''
    else:
        show = True
        massege = msg

    # most discount
    most_discounts = Product.objects.get_most_discount_precentage_available_product()
    most_discount = Product.objects.get_one_most_discount_precenetage_available_product_random()

    # other products bought by other user
    factors = Factor.objects.filter(FK_FactorPost__FK_Product=this_product)
    other_products = Product.objects.filter(Factor_Product__Factor_Products__in=factors).exclude(ID = this_product.ID).distinct()


    context = {
        'This_User_Profile':this_profile,
        'This_User_Inverntory': this_inverntory,
        'Options': options,
        'MenuList':navbar,
        'Product':this_product,
        'Shop':this_shop,
        'AttrProduct':attarproduct,
        'AttrPrice':attrprice,
        'Banners':pubbanner,
        'Comments':pubcomments,
        'Reviews':pubreviews,
        # 'View_Count':view_count,
        # 'Sell_Count':total_sell,
        'RelatedProduct':this_product_related,
        'ShowAlart':show,
        'AlartMessage':massege,
        'MostDiscount':most_discount,
        'MostDiscounts':most_discounts,
        'OtherProducts':other_products,
    }
    context['google_analytics_event1'] = (
        'view_item', 
        {
            "items": [
                {
                "id": this_product.ID,
                "name": this_product.Title,
                "list_name": this_product.FK_SubMarket,
                "brand": this_shop.Title,
                "category": this_product.FK_SubMarket,
                "variant": "",
                "list_position": 1,
                "quantity": this_product.Inventory,
                "price": this_product.Price
                }
            ]
        }
    )

    return render(request, 'nakhll_market/pages/productpage.html', context)




# # Show All Products
# def AllProduct(request):

#     # Get User Info
#     user = User.objects.all()
#     # Get User Profile
#     profile = Profile.objects.all()
#     # Get Wallet Inverntory
#     wallets = Wallet.objects.all()
#     # Get Menu Item
#     options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
#     # Get Nav Bar Menu Item
#     navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
#     # --------------------------------------------------------------------
#     # Get All Products
#     products = Product.objects.filter(Available = True, Publish = True).order_by('-DateCreate')
#     # Get All Category
#     allcategories = Category.objects.filter(Publish = True)

#     productpaginator = Paginator (products, 24)
#     page = request.GET.get('page')

#     products = productpaginator.get_page(page)

#     context = {
#         'Users':user,
#         'Profile':profile,
#         'Wallet': wallets,
#         'Options': options,
#         'MenuList':navbar,
#         'Products':products,
#         'Category':allcategories,
#     }

#     return render(request, 'nakhll_market/pages/allproducts.html', context)

# WebSite Pages
#---------------------------------------------------------------------------------------------------------------------------------   

# Statict Page
def StaticPage(request, name):
    # Get User Info
    user=User.objects.all()
    # Get User Profile
    profile=Profile.objects.all()
    # Get Wallet Inverntory
    wallets=Wallet.objects.all()
    # Get Menu Item
    options=Option_Meta.objects.filter(Title='index_page_menu_items')
    # Get Nav Bar Menu Item
    navbar=Option_Meta.objects.filter(Title='nav_menu_items')
    # Get Page
    page=Pages.objects.get(Slug = name, Publish =True)

    context = {
        'Users':user,
        'Profile':profile,
        'Wallet': wallets,
        'Options': options,
        'MenuList':navbar,
        'ShowAlart':False,
        'Page':page,
    }

    return render(request, 'nakhll_market/pages/pages.html', context)

# Connect Us Page
def connectus(request):
    Road = []
    #Get User Info
    user=User.objects.all()
    # Get User Profile
    profile=Profile.objects.all()
    # Get Wallet Inverntory
    wallets=Wallet.objects.all()
    # Get Menu Item
    options=Option_Meta.objects.filter(Title='index_page_menu_items')
    # Get Nav Bar Menu Item
    navbar=Option_Meta.objects.filter(Title='nav_menu_items')
    #---------------------------------------------------------------------
    # Build Connect Class
    class ConnectToSite:
        def __init__(self, TitleSection, PhoneNumbers, icon):
            self.Title = TitleSection
            self.Icon = icon
            self.PhoneNumber = PhoneNumbers

    # Get Connect Us
    connect = Option_Meta.objects.filter(Title = 'connect_us')

    for con in connect:
        phones = con.Description.split('-')
        CTS = ConnectToSite(con.Value_1, phones, con.Value_2)
        Road.append(CTS)

    context = {
        'Users':user,
        'Profile':profile,
        'Wallet': wallets,
        'Options': options,
        'MenuList':navbar,
        'ShowAlart':False,
        'ConnectRoad':Road,
    }

    return render(request, 'nakhll_market/pages/connect.html', context)

# Advanced Search Page
def Advanced_Search(request):
    # Get User Info
    if request.user.is_authenticated:
        
        this_profile = Profile.objects.get(FK_User=request.user)
        this_inverntory = request.user.WalletManager.Inverntory
    else:
        this_profile = None
        this_inverntory = None
    # Get Menu Item
    options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
    # Get Nav Bar Menu Item
    navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
    # ---------------------------------------------------------------------

    context = {
        'This_User_Profile':this_profile,
        'This_User_Inverntory': this_inverntory,
        'Options': options,
        'MenuList':navbar,
    }
    return render(request, 'nakhll_market/pages/advanced-search.html', context)

# search Page
def search(request):
    if request.method == 'POST':
        similarity_bound = 0.1
        try:
            init_words = request.POST["search"]
            words = init_words.split(' ')
            words = list(filter(lambda i: i!='', words))
            search_words = []
            for word in words:
                search_word = list(map(lambda x: x + '\s*', word.replace(' ','')[:-1]))
                search_word = ''.join(search_word) + word[-1]
                search_words.append(search_word)
            search_word = r'.*'.join(search_words)
            word = ' '.join(words)
        except:
            word = False
            init_words = False
        # ----------------------------------------------------------------
        # Get User Info
        if request.user.is_authenticated:
            this_profile = Profile.objects.get(FK_User=request.user)
            this_inverntory = request.user.WalletManager.Inverntory
        else:
            this_profile = None
            this_inverntory = None
        # Get Menu Item
        options=Option_Meta.objects.filter(Title='index_page_menu_items')
        # Get Nav Bar Menu Item
        navbar=Option_Meta.objects.filter(Title='nav_menu_items')
        # ----------------------------------------------------------------
        # Build Search_In_Shop Class
        class Search_In_Shop:
            def __init__(self, item, item_market, item_submarket):
                self.Shop = item
                self.Market = item_market
                self.Submarket = item_submarket
        # Get Shops
        all_shop_in_query = []
        for item in\
            Shop.objects\
            .annotate(similarity=TrigramSimilarity('Title', init_words))\
            .filter(
                similarity__gt=similarity_bound, Available = True, Publish = True
            ).order_by('-similarity'):
            all_shop_in_query.append(item)
        # Set Data In Class
        all_shop_in_query_objects = []
        for item in all_shop_in_query:
            if item.FK_SubMarket.all().count() != 0:
                all_shop_in_query_objects.append(Search_In_Shop(item, item.FK_SubMarket.all()[0].FK_Market, item.FK_SubMarket.all()[0]))
            else:
                all_shop_in_query_objects.append(Search_In_Shop(item, None, None))

        # Get Product
        all_product_in_query = []
        for item in\
            Product.objects\
            .annotate(similarity=TrigramSimilarity('Title', init_words))\
            .filter(similarity__gt=similarity_bound, Available = True, Publish = True, Status__in = ['1', '2', '3'])\
            .order_by('-similarity'):
            all_product_in_query.append(item)
        for item in\
            Product.objects\
            .annotate(similarity=TrigramSimilarity('Title', init_words))\
            .filter(similarity__gt=similarity_bound, Available = True, Publish = True, Status__in = ['4'])\
            .order_by('-similarity'):
            all_product_in_query.append(item)

        context = {
            'This_User_Profile':this_profile,
            'This_User_Inverntory': this_inverntory,
            'Options': options,
            'MenuList':navbar,
            'Result_In_Shop':all_shop_in_query_objects,
            'Result_In_Product':all_product_in_query,
            'Word':word,
        }

        return render(request, 'nakhll_market/pages/searche.html', context)

    elif request.method == 'GET':
        return HttpResponse('user method is not allowed!', status=405)

# Searche With Filters Page
def FilterSearch(request):

    if request.method == 'POST':

        Categories = request.POST.getlist("Category_Select")

        SortBy = request.POST["Sort_By"]

        try:
            Max = request.POST["Max"]
        except:
            Max = False    

        try:
            Min = request.POST["Min"]
        except:
            Min = False   
        # -----------------------------------------------------------------
        # Get User Info
        if request.user.is_authenticated:
            this_profile = Profile.objects.get(FK_User=request.user)
            this_inverntory = request.user.WalletManager.Inverntory
        else:
            this_profile = None
            this_inverntory = None
        # Get Menu Item
        options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
        # Get Nav Bar Menu Item
        navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
        # ------------------------------------------------------------------
        # Get All Products
        allproducts = []
        for item in Product.objects.filter(Available = True, Publish = True, Status__in = ['1', '2', '3']).order_by('-DateCreate'):
            allproducts.append(item) 
        for item in Product.objects.filter(Available = True, Publish = True, Status = '4').order_by('-DateCreate'):
            allproducts.append(item)
        # ------------------------------------------------------------------
        # Build Class
        class Items:
            def __init__(self, category, status):
                self.Category = category
                self.Status = status

        ItemsList = []

        for cat in Category.objects.filter(Publish = True):
            item = Items(cat, False)
            ItemsList.append(item)

        for cat in Categories:
            for i in ItemsList:
                if i.Category.Title == cat:
                    i.Status = True

        if len(ItemsList) != 0:  
            for item in Categories:      
                allproducts = Product.objects.filter(FK_Category = Category.objects.get(Title = item), Available = True, Publish = True)


        # Get Product Price
        def GetPrice(item):
            return int(item.Price)

        # Get Product Create Date
        def GetDate(item):
            return item.DateCreate

        # Product Add To List
        Product_List = []
        for item in allproducts:
            Product_List.append(item)

        if (Min != '100000') or (Max != '50000000'):
            this_list =  []
            for item in Product_List:
                if (Min != '100000') and (Max == '50000000'):
                    if int(item.Price) >= int(Min):
                        this_list.append(item)
                elif (Min == '100000') and (Max != '50000000'):
                    if int(item.Price) <= int(Max):
                        this_list.append(item)
                else:
                    if (int(item.Price) >= int(Min)) and (int(item.Price) <= int(Max)):
                        this_list.append(item)
            
            Product_List = this_list

        if SortBy == 'جدید ترین ها':
            Product_List.sort(reverse = True, key = GetDate)
            sort = '0'
        elif SortBy == 'قدیمی ترین ها':
            Product_List.sort(key = GetDate)
            sort = '1'
        elif SortBy == 'قیمت نزولی':
            Product_List.sort(reverse = True, key = GetPrice)
            sort = '2'
        elif SortBy == 'قیمت صعودی':
            Product_List.sort(key = GetPrice)
            sort = '3'

        # productpaginator = Paginator (Product_List, 4)
        # page = request.GET.get('page')

        # Product_List = productpaginator.get_page(page)

        context = {
            'This_User_Profile':this_profile,
            'This_User_Inverntory': this_inverntory,
            'Options': options,
            'MenuList':navbar,
            'Categories':ItemsList,
            'Products':Product_List,
            'Sort':sort,
            'MaxValue':Max,
            'MinValue':Min,
        }

        return render(request, 'nakhll_market/pages/filter.html', context)

    else:
        # Get User Info
        if request.user.is_authenticated:
            this_profile = Profile.objects.get(FK_User=request.user)
            this_inverntory = request.user.WalletManager.Inverntory
        else:
            this_profile = None
            this_inverntory = None
        # Get Menu Item
        options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
        # Get Nav Bar Menu Item
        navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
        # --------------------------------------------------------------------
        # Get All Products
        products = []
        for item in Product.objects.filter(Available = True, Publish = True, Status__in = ['1', '2', '3']).order_by('-DateCreate'):
            products.append(item) 
        for item in Product.objects.filter(Available = True, Publish = True, Status = '4').order_by('-DateCreate'):
            products.append(item)
        # Build Class
        class Items:
            def __init__(self, category, status):
                self.Category = category
                self.Status = status

        ItemsList = []
        # Get All Category
        for cat in Category.objects.filter(Publish = True):
            item = Items(cat, False)
            ItemsList.append(item)

        productpaginator = Paginator (products, 24)
        page = request.GET.get('page')

        products = productpaginator.get_page(page)

        sort = '0'
        Max = '50000000'
        Min = '100000'

        context = {
            'This_User_Profile':this_profile,
            'This_User_Inverntory': this_inverntory,
            'Options': options,
            'MenuList':navbar,
            'Products':products,
            'Categories':ItemsList,
            'Sort':sort,
            'MaxValue':Max,
            'MinValue':Min,
        }

        return render(request, 'nakhll_market/pages/filter.html', context)


# Complaint Page
def Complaint(request):
        
    Road = []    
    #Get User Info
    user=User.objects.all()
    # Get User Profile
    profile=Profile.objects.all()
    # Get Wallet Inverntory
    wallets=Wallet.objects.all()
    # Get Menu Item
    options=Option_Meta.objects.filter(Title='index_page_menu_items')
    # Get Nav Bar Menu Item
    navbar=Option_Meta.objects.filter(Title='nav_menu_items')
    #---------------------------------------------------------------------
    # Build Connect Class
    class ConnectToSite:
        def __init__(self, TitleSection, PhoneNumbers, icon):
            self.Title = TitleSection
            self.Icon = icon
            self.PhoneNumber = PhoneNumbers

    # Get Connect Us
    connect = Option_Meta.objects.filter(Title = 'connect_us')

    for con in connect:
        phones = con.Description.split('-')
        CTS = ConnectToSite(con.Value_1, phones, con.Value_2)
        Road.append(CTS)

    context = {
        'Users':user,
        'Profile':profile,
        'Wallet': wallets,
        'Options': options,
        'MenuList':navbar,
        'ShowAlart':False,
        'ConnectRoad':Road,
    }

    return render(request, 'nakhll_market/pages/complaint.html', context)

# Product Comment ---------------------------------------------------------------------------------------------------------------------


# Add Comment And Show Message
def AddNewCommentInProduct(request, this_product):
    # Check User Status
    if request.user.is_authenticated :

        if request.method == 'POST':

            Comment_Type = request.POST['comment_type']
            CommentDescription = request.POST["comment_description"]
            CommentProduct = Product.objects.get(Slug = this_product)
     
            if Comment_Type == '1':
                CommentType = True
            elif Comment_Type == '0':
                CommentType = False

            if CommentDescription != '':

                if Comment.objects.filter(Type = CommentType, FK_UserAdder = request.user, FK_Product = CommentProduct, Description = CommentDescription).count() != 0:

                    return redirect('nakhll_market:Re_ProductsDetail',
                    shop_slug = CommentProduct.FK_Product.FK_Shop.Slug,
                    product_slug = CommentProduct.Slug,
                    status = True,
                    msg =  'نظر شما قبلا ثبت شده است!')

                else:

                    comment = Comment.objects.create(Type = CommentType, FK_UserAdder = request.user, FK_Product = CommentProduct, Description = CommentDescription)
                    Alert.objects.create(Part = '14', FK_User = request.user, Slug = comment.id)

                    return redirect('nakhll_market:Re_ProductsDetail',
                    shop_slug = comment.FK_Product.FK_Shop.Slug,
                    product_slug = comment.FK_Product.Slug,
                    status = True,
                    msg =  'نظر شما با موفقیت ثبت شد بعد از تایید کارشناسان در سایت قرار خواهد گرفت .')

            else:

                return redirect('nakhll_market:Re_ProductsDetail',
                shop_slug = CommentProduct.FK_Product.FK_Shop.Slug,
                product_slug = CommentProduct.Slug,
                status = True,
                msg =  'متن نظر نمی تواند خالی باشد!')

    else:

        return redirect("auth:login")


# Add Replay Comment And Show Message In Product Page
def AddReplayCommentInProduct(request, id):
    # Check User Status
    if request.user.is_authenticated :

        if request.method == 'POST':

            father_comment = get_object_or_404(Comment, id = id)
            CommentDescription = request.POST["comment_description"]
            CommentProduct = father_comment.FK_Product
            father_comment = get_object_or_404(Comment, id = id)
    
            if CommentDescription != '':

                if Comment.objects.filter(FK_UserAdder = request.user, FK_Product = CommentProduct, Description = CommentDescription, FK_Pater = father_comment).count() != 0:
                    return redirect('nakhll_market:Re_ProductsDetail',
                    shop_slug = CommentProduct.FK_Product.FK_Shop.Slug,
                    product_slug = CommentProduct.Slug,
                    status = True,
                    msg =  'نظر شما قبلا ثبت شده است!')

                else:
                    comment = Comment.objects.create(FK_UserAdder = request.user, FK_Product = CommentProduct, Description = CommentDescription, FK_Pater = father_comment)
                    Alert.objects.create(Part = '14', FK_User = request.user, Slug = comment.id)

                    return redirect('nakhll_market:Re_ProductsDetail',
                    shop_slug = comment.FK_Product.FK_Shop.Slug,
                    product_slug = comment.FK_Product.Slug,
                    status = True,
                    msg =  'نظر شما با موفقیت ثبت شد بعد از تایید کارشناسان در سایت قرار خواهد گرفت .')

            else:
                return redirect('nakhll_market:Re_ProductsDetail',
                shop_slug = CommentProduct.FK_Product.FK_Shop.Slug,
                product_slug = CommentProduct.Slug,
                status = True,
                msg =  'متن نظر نمی تواند خالی باشد!')

    else:

        return redirect("auth:login")


# End ---------------------------------------------------------------------------------------------------------------------------------






# Shop Comment ---------------------------------------------------------------------------------------------------------------------


# Add Comment In Shop Page
def AddNewCommentInShop(request, this_shop):
    # Check User Status
    if request.user.is_authenticated :

        if request.method == 'POST':

            Comment_Type = request.POST['comment_type']
            CommentDescription = request.POST["comment_description"]
            CommentShop = get_object_or_404(Shop, Slug = this_shop)
     
            if Comment_Type == '1':
                CommentType = True
            elif Comment_Type == '0':
                CommentType = False

            if CommentDescription != '':

                if ShopComment.objects.filter(Type = CommentType, FK_UserAdder = request.user, FK_Shop = CommentShop, Description = CommentDescription).count() != 0:

                    return redirect('nakhll_market:Re_ShopsDetail',
                    shop_slug = CommentShop.Slug,
                    msg =  'نظر شما قبلا ثبت شده است!')

                else:

                    comment = ShopComment.objects.create(Type = CommentType, FK_UserAdder = request.user, FK_Shop = CommentShop, Description = CommentDescription)
                    Alert.objects.create(Part = '30', FK_User = request.user, Slug = comment.id)

                    return redirect('nakhll_market:Re_ShopsDetail',
                    shop_slug = CommentShop.Slug,
                    msg =  'نظر شما با موفقیت ثبت شد بعد از تایید کارشناسان در سایت قرار خواهد گرفت .')

            else:

                return redirect('nakhll_market:Re_ShopsDetail',
                shop_slug = CommentShop.Slug,
                msg =  'متن نظر نمی تواند خالی باشد!')

    else:

        return redirect("auth:login")


# Add Replay Comment In Shop Page
def AddReplayCommentInShop(request, id):
    # Check User Status
    if request.user.is_authenticated :

        if request.method == 'POST':

            father_comment = get_object_or_404(ShopComment, id = id)
            CommentDescription = request.POST["comment_description"]
            CommentShop = father_comment.FK_Shop
    
            if CommentDescription != '':

                if ShopComment.objects.filter(FK_UserAdder = request.user, FK_Shop = CommentShop, Description = CommentDescription, FK_Pater = father_comment).count() != 0:
                    return redirect('nakhll_market:Re_ShopsDetail',
                    shop_slug = CommentShop.Slug,
                    msg =  'نظر شما قبلا ثبت شده است!')

                else:
                    comment = ShopComment.objects.create(FK_UserAdder = request.user, FK_Shop = CommentShop, Description = CommentDescription, FK_Pater = father_comment)
                    Alert.objects.create(Part = '30', FK_User = request.user, Slug = comment.id)

                    return redirect('nakhll_market:Re_ShopsDetail',
                    shop_slug = CommentShop.Slug,
                    msg =  'نظر شما با موفقیت ثبت شد بعد از تایید کارشناسان در سایت قرار خواهد گرفت .')

            else:
                return redirect('nakhll_market:Re_ShopsDetail',
                shop_slug = CommentShop.Slug,
                msg =  'متن نظر نمی تواند خالی باشد!')

    else:

        return redirect("auth:login")


# End ---------------------------------------------------------------------------------------------------------------------------------


# Add Review And Show Message In Product Page
def AddNewReviewInProduct(request, this_product):
    # Check User Status
    if request.user.is_authenticated :

        if request.method == 'POST':

            try:
                Review_Title = request.POST["Review_Title"]
            except MultiValueDictKeyError:
                Review_Title = False

            try:
                Review_Description = request.POST["Review_Description"]
            except MultiValueDictKeyError:
               Review_Description = False

            Review_Positive = request.POST.getlist("field-up")

            Review_Negative = request.POST.getlist("field-down")

            profileduct = get_object_or_404(Product, Slug = this_product)

            if (Review_Title != '') and (Review_Description != ''):

                review_check = Review.objects.filter(Title = Review_Title, FK_UserAdder = request.user, FK_Product = profileduct, Description = Review_Description)
                if review_check.count() != 0:

                    pos_note_check = False
                    for item in Review_Positive:
                        for Pos_Note in review_check[0].FK_PositiveNote.all():
                            if Pos_Note.Item == item:
                                pos_note_check = True

                    neg_note_check = False
                    for item in Review_Negative:
                        for Neg_Note in review_check[0].FK_NegativeNote.all():
                            if Neg_Note.Item == item:
                                neg_note_check = True

                    if (pos_note_check) and (neg_note_check):

                        return redirect('nakhll_market:Re_ProductsDetail',
                        shop_slug = profileduct.FK_Shop.Slug,
                        product_slug = profileduct.Slug,
                        status = True,
                        msg = 'نظر شما قبلا ثبت شده است!')

                else:

                    review = Review.objects.create(Title = Review_Title, FK_UserAdder = request.user, Description = Review_Description, FK_Product = profileduct)

                    if len(Review_Positive) != 0:
                        for item in Review_Positive:
                            if item != '':
                                New_Note = Note.objects.create(Item = item)
                                review.FK_PositiveNote.add(New_Note)

                    if len(Review_Negative) != 0:
                        for item in Review_Negative:
                            if item != '':
                                New_Note = Note.objects.create(Item = item)
                                review.FK_NegativeNote.add(New_Note)

                    # Set Alert
                    Alert.objects.create(Part = '15', FK_User = request.user, Slug = review.id)
                    # -----------------------------------------------------------------------------------------
                    return redirect('nakhll_market:Re_ProductsDetail',
                    shop_slug = profileduct.FK_Shop.Slug,
                    product_slug = profileduct.Slug,
                    status = True,
                    msg = 'نقد شما با موفقیت ثبت شد، و پس از بررسی کارشناسان در سایت قرار خواهد گرفت.')

            else:

                return redirect('nakhll_market:Re_ProductsDetail',
                shop_slug =profileduct.FK_Shop.Slug,
                product_slug = profileduct.Slug,
                status = True,
                msg = 'عنوان و توضیحات برای ثیت نقد و بررسی اجباریست!')

    else:

        return redirect("auth:login")


# Product Like
def ContentLike(request, id, type):

    if request.user.is_authenticated :

        if type == 1: # Like Product

            # Get This Product Comment
            this_comment = Comment.objects.get(id = id)
            # Chech User
            check_user = False
            for item in this_comment.FK_Like.all():
                if item == request.user:
                    check_user = True
                    break
            
            if check_user:

                this_comment.FK_Like.remove(request.user)
                return redirect("nakhll_market:ProductsDetail", shop_slug = this_comment.FK_Product.FK_Shop.Slug, product_slug = this_comment.FK_Product.Slug)
                
            else:

                this_comment.FK_Like.add(request.user)
                return redirect("nakhll_market:ProductsDetail", shop_slug = this_comment.FK_Product.FK_Shop.Slug, product_slug = this_comment.FK_Product.Slug)

        elif type == 0: # Like Review

            # Get This Product Review
            this_review = Review.objects.get(id = id)
            # Chech User
            check_user = False
            for item in this_review.FK_Like.all():
                if item == request.user:
                    check_user = True
                    break
            
            if check_user:
                
                this_review.FK_Like.remove(request.user)
                return redirect("nakhll_market:ProductsDetail", shop_slug = this_review.FK_Product.FK_Shop.Slug, product_slug = this_review.FK_Product.Slug)
                
            else:

                this_review.FK_Like.add(request.user)
                return redirect("nakhll_market:ProductsDetail", shop_slug = this_review.FK_Product.FK_Shop.Slug, product_slug = this_review.FK_Product.Slug)

    else:

        return redirect("auth:login")


# Shop Comment Like
def ShopCommentLike(request, id):

    if request.user.is_authenticated :

        # Get This Shop Comment
        this_comment = get_object_or_404(ShopComment, id = id)
        # Chech User
        check_user = False
        for item in this_comment.FK_Like.all():
            if item == request.user:
                check_user = True
                break
    
        if check_user:
            this_comment.FK_Like.remove(request.user)
            return redirect("nakhll_market:ShopsDetail", shop_slug = this_comment.FK_Shop.Slug)
        else:
            this_comment.FK_Like.add(request.user)
            return redirect("nakhll_market:ShopsDetail", shop_slug = this_comment.FK_Shop.Slug)

    else:

        return redirect("auth:login")


# -------------------------------------------------------------------------------------------------------------------------------

# Choise Random Product Function
class Choise_Random_Product:
    def run(self):
        FinalList = []
        ProductList = []
        # Get Coupon 
        coupon = get_object_or_404(Coupon, SerialNumber = 'dokhtar99')
        # Get Random Product
        for item in coupon.FK_Shops.all():
            if Product.objects.filter(Status__in = ['1', '2', '3']).count() != 0:
                for product in Product.objects.filter(FK_Shop = item, Publish = True, Available = True, Status__in = ['1', '2', '3']):
                    ProductList.append(product)
                # Get Random
                if len(ProductList) != 0:
                    random_index = random.randint(0, len(ProductList))
                    if random_index == len(ProductList):
                        FinalList.append(ProductList[(len(ProductList) - 1)])
                    else:
                        FinalList.append(ProductList[random_index])
                    ProductList.clear()
                

        FinalList = FinalList[:18]

        return FinalList


# Show Campaing
def ShowCampaing(request):

    # Get User Info
    if request.user.is_authenticated:
        
        this_profile = Profile.objects.get(FK_User=request.user)
        this_inverntory = request.user.WalletManager.Inverntory
    else:
        this_profile = None
        this_inverntory = None
    # Get Menu Item
    options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
    # Get Nav Bar Menu Item
    navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
    # ---------------------------------------------------------------------
    # Get Camp Detail
    camp_detail = Option_Meta.objects.get(Title = 'camp_detail')
    # Get Coupon 
    coupon = get_object_or_404(Coupon, SerialNumber = 'dokhtar99')
    # Get Random Product For Show
    products = Choise_Random_Product().run()

    context = {
        'This_User_Profile':this_profile,
        'This_User_Inverntory': this_inverntory,
        'Options': options,
        'MenuList':navbar,
        'Coupon':coupon,
        'Products':products,
        'Detail':camp_detail,
    }

    return render(request, 'nakhll_market/pages/campaing_page.html', context)


    
# Show Campaing
def ShowCampProducts(request):

    # Get User Info
    if request.user.is_authenticated:
        
        this_profile = Profile.objects.get(FK_User=request.user)
        this_inverntory = request.user.WalletManager.Inverntory
    else:
        this_profile = None
        this_inverntory = None
    # Get Menu Item
    options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
    # Get Nav Bar Menu Item
    navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
    # ---------------------------------------------------------------------
    # Get Camp Detail
    camp_detail = Option_Meta.objects.get(Title = 'camp_detail')
    # Get Coupon 
    coupon = get_object_or_404(Coupon, SerialNumber = 'dokhtar99')
    # Get All Campain Product
    product_campain = []
    for item in coupon.FK_Shops.all():
        for product in Product.objects.filter(FK_Shop = item, Publish = True, Available = True, Status__in = ['1', '2', '3']):
            product_campain.append(product)

    context = {
        'This_User_Profile':this_profile,
        'This_User_Inverntory': this_inverntory,
        'Options': options,
        'MenuList':navbar,
        'Coupon':coupon,
        'Products':product_campain,
        'Detail':camp_detail,
    }

    return render(request, 'nakhll_market/pages/camp_product.html', context)