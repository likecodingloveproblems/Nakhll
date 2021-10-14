from django.http.response import Http404
from nakhll.settings import KAVENEGAR_KEY
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator
from django.urls import reverse
from django.views import generic
from ipware import get_client_ip
import jdatetime
from datetime import date
from datetime import datetime
from django.contrib import messages
from django.utils.datastructures import MultiValueDictKeyError
from kavenegar import *
import threading
import requests


from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import user_passes_test

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin

from django.contrib.auth.models import User
from django.contrib.auth.models import Group 

from .models import Tag
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
from .models import AttrPrice, OptinalAttribute
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
from .models import User_Message_Status
from .models import Option_Meta
from .models import Alert
from .models import Field 

from Payment.models import PostTrackingCode, Wallet, Transaction, Factor, FactorPost, PostBarCode, Coupon

from Ticketing.models import Ticketing, TicketingMessage, Complaint

from .forms import Login, CheckEmail

# -----------------------------------------------------------------------------------------------------------------------------------

# Send Alert SMS
class SendMessage:

    def __init__(self, user_id, title, description, sender_id):
        self.user = User.objects.get(id = user_id)
        self.msg_title = title
        self.msg_des = description
        self.msg_sender = User.objects.get(id = sender_id)

    # Check User Message
    def CheckUserMessage(self):
        # Message Count
        msg_count = 0
        # Get This User
        this_user = self.user
        # Check
        if Message.objects.all().exists():
            for item in Message.objects.all():
                for It in item.FK_Users.all():
                    if (It.FK_User == this_user) and (It.SeenStatus == False):
                        msg_count += 1
            if msg_count != 0:
                return msg_count
            else:
                return msg_count
        else:
            return msg_count

    def run(self):

        # Save New Message
        new_message = Message.objects.create(Title = self.msg_title, Text = self.msg_des, FK_Sender = self.msg_sender)
        new_obj = User_Message_Status.objects.create(FK_User = self.user)
        new_message.FK_Users.add(new_obj)
        # User Message Count
        msg_count = self.CheckUserMessage()
        # Get User Phone Number
        PhoneNumber = Profile.objects.get(FK_User = self.user).MobileNumber
        # Send SMS
        url = 'https://api.kavenegar.com/v1/{}/verify/lookup.json'.format(KAVENEGAR_KEY) 
        params = {'receptor': PhoneNumber, 'token' : msg_count, 'template' : 'nakhll-message'}
        requests.post(url, params = params)


# Send Alert SMS
def SendAlertResponse(Title, Description, PhoneNumber):
    # Change Text
    des_list = Description.split(' ')
    final_des = ''
    count = 0
    for item in des_list:
        if (count + 1) == len(des_list):
            final_des += item
            count += 1
        else:
            final_des += item + '-'
            count += 1

    url = 'https://api.kavenegar.com/v1/{}/verify/lookup.json'.format(KAVENEGAR_KEY) 
    params = {'receptor': PhoneNumber, 'token' : Title, 'token2' : final_des, 'template' : 'nakhll-alert'}
    requests.post(url, params = params)


# Send Post Code
def SendPostCode(Shop, FactorNum, PostCode, PhoneNumber):
    # Change Text
    des_list = Shop.split(' ')
    final_des = ''
    count = 0
    for item in des_list:
        if (count + 1) == len(des_list):
            final_des += item
            count += 1
        else:
            final_des += item + '-'
            count += 1

    url = 'https://api.kavenegar.com/v1/{}/verify/lookup.json'.format(KAVENEGAR_KEY) 
    params = {'receptor': PhoneNumber, 'token' : final_des, 'token2' : FactorNum, 'token3' : PostCode, 'template' : 'nakhll-sendpostcode'}
    requests.post(url, params = params)


# Send Push notification
class send_push_notification:
    def run(self, title, description, push_id):
        try:
            TOKEN = '70c66e5fcb993ac51a432617941d5694c03c4943'

            # set header
            headers = {
                'Authorization': 'Token ' + TOKEN,
                'Content-Type': 'application/json'
            }

            data = {
                'app_ids': ['5dn66jy6p2zk358e', ],
                'data': {
                    'title': title,
                    'content': description,
                    'wake_screen':'True',
                    'action_type':'A',
                    'led_color':'8206336',
                },
                'filters': {
                    'phone_number': [push_id,]
                },
            }

            # send request
            response = requests.post(
                'https://api.pushe.co/v2/messaging/notifications/',
                json = data,
                headers = headers,
            )

            if response.status_code == 201:
                print('Success!')
        except Exception as e:
            print(str(e))


# ------------------------------------------------------------------------------------------------------------------------------------
# Comment Alert
@login_required
@staff_member_required
def CommentAlert(request, id):
    # Get User Info
    this_profile = Profile.objects.get(FK_User=request.user)
    this_inverntory = request.user.WalletManager.Inverntory
    # Get Menu Item
    options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
    # Get Nav Bar Menu Item
    navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
    # --------------------------------------------------------------------
    # Get Comment
    comment = Comment.objects.get(id = id)

    context = {
        'This_User_Profile':this_profile,
        'This_User_Inverntory': this_inverntory,
        'Options': options,
        'MenuList':navbar,
        'Comment':comment,
    }
    return render(request, 'nakhll_market/alert/pages/commentalert.html', context)


# Comment Alert
@login_required
@staff_member_required
def ReviewAlert(request, id):
    # Get User Info
    this_profile = Profile.objects.get(FK_User=request.user)
    this_inverntory = request.user.WalletManager.Inverntory
    # Get Menu Item
    options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
    # Get Nav Bar Menu Item
    navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
    # -----------------------------------------------------------------------
    # get this review
    review = get_object_or_404(Review, id = id)

    context = {
        'This_User_Profile':this_profile,
        'This_User_Inverntory': this_inverntory,
        'Options': options,
        'MenuList':navbar,
        'Review':review,
    }

    return render(request, 'nakhll_market/alert/pages/reviewalert.html', context)


# Alert Shop
@login_required
@staff_member_required
def ShopAlert(request, id):
    # Get User Info
    this_profile = Profile.objects.get(FK_User=request.user)
    this_inverntory = request.user.WalletManager.Inverntory
    # Get Menu Item
    options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
    # Get Nav Bar Menu Item
    navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
    # --------------------------------------------------------------------
    # Get This Shop
    this_shop = get_object_or_404(Shop, ID = id)

    context = {
        'This_User_Profile':this_profile,
        'This_User_Inverntory': this_inverntory,
        'Options': options,
        'MenuList':navbar,
        'This_Shop':this_shop,
    }

    return render(request, 'nakhll_market/alert/pages/shopalert.html', context)


# Alert Add New Shop Banner
@login_required
@staff_member_required
def ShopBannerAlert(request, id):
    # Get User Info
    this_profile = Profile.objects.get(FK_User=request.user)
    this_inverntory = request.user.WalletManager.Inverntory
    # Get Menu Item
    options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
    # Get Nav Bar Menu Item
    navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
    # --------------------------------------------------------------------
    # Get This Shop Banner
    thid_banner = get_object_or_404(ShopBanner, id = id)

    context = {
        'This_User_Profile':this_profile,
        'This_User_Inverntory': this_inverntory,
        'Options': options,
        'MenuList':navbar,
        'UserBanner':thid_banner,
    }
    return render(request, 'nakhll_market/alert/pages/shopbanneralert.html', context)

# Product Alert
@login_required
@staff_member_required
def ProductAlert(request, id):
    this_profile = Profile.objects.get(FK_User=request.user)
    this_inverntory = request.user.WalletManager.Inverntory
    # Get Menu Item
    options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
    # Get Nav Bar Menu Item
    navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
    # --------------------------------------------------------------------
    this_product = get_object_or_404(Product, ID = id)

    context = {
        'This_User_Profile':this_profile,
        'This_User_Inverntory': this_inverntory,
        'Options': options,
        'MenuList':navbar,
        'Product':this_product,
    }
    return render(request, 'nakhll_market/alert/pages/productalert.html', context)


# Product Banner Alert
@login_required
@staff_member_required
def ProductBannerAlert(request, id):
    this_profile = Profile.objects.get(FK_User=request.user)
    this_inverntory = request.user.WalletManager.Inverntory
    # Get Menu Item
    options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
    # Get Nav Bar Menu Item
    navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
    # --------------------------------------------------------------------
    this_banner = get_object_or_404(ProductBanner, id = id)

    context = {
        'This_User_Profile':this_profile,
        'This_User_Inverntory': this_inverntory,
        'Options': options,
        'MenuList':navbar,
        'UserBanner':this_banner,
    }
        
    return render(request, 'nakhll_market/alert/pages/producbannertalert.html', context)


# Attribute Alert
@login_required
@staff_member_required
def AttributeAlert(request, id):
    this_profile = Profile.objects.get(FK_User=request.user)
    this_inverntory = request.user.WalletManager.Inverntory
    # Get Menu Item
    options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
    # Get Nav Bar Menu Item
    navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
    # --------------------------------------------------------------------
    this_attribute = get_object_or_404(Attribute, id = id)

    context = {
        'This_User_Profile':this_profile,
        'This_User_Inverntory': this_inverntory,
        'Options': options,
        'MenuList':navbar,
        'Attr':this_attribute,
    }
        
    return render(request, 'nakhll_market/alert/pages/attributealert.html', context)


# Product Attribute Alert
@login_required
@staff_member_required
def ProductAttributeAlert(request, id):
    this_profile = Profile.objects.get(FK_User=request.user)
    this_inverntory = request.user.WalletManager.Inverntory
    # Get Menu Item
    options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
    # Get Nav Bar Menu Item
    navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
    # --------------------------------------------------------------------
    attrprod = get_object_or_404(AttrProduct, id = id)

    context = {
        'This_User_Profile':this_profile,
        'This_User_Inverntory': this_inverntory,
        'Options': options,
        'MenuList':navbar,
        'AttrProd':attrprod,
    }
        
    return render(request, 'nakhll_market/alert/pages/attributeproductalert.html', context)


# Edite Shop Banner Alert
@login_required
@staff_member_required
def EditeShopBannerAlert(request, id):
    # Get User Info
    this_profile = Profile.objects.get(FK_User=request.user)
    this_inverntory = request.user.WalletManager.Inverntory
    # Get Menu Item
    options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
    # Get Nav Bar Menu Item
    navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
    # --------------------------------------------------------------------
    # Get This Alert
    this_alert = get_object_or_404(Alert, Slug = id, Part = '5', Seen = False)
    # Get This Shop Banner
    this_banner = get_object_or_404(ShopBanner, id = id)

    context = {
        'This_User_Profile':this_profile,
        'This_User_Inverntory': this_inverntory,
        'Options': options,
        'MenuList':navbar,
        'Alert':this_alert,
        'Banner':this_banner,
    }
        
    return render(request, 'nakhll_market/alert/pages/editeshopbanneralert.html', context)


# edit product banner alert
@login_required
@staff_member_required
def EditeProductBannerAlert(request, id):
     # Get User Info
    this_profile = Profile.objects.get(FK_User=request.user)
    this_inverntory = request.user.WalletManager.Inverntory
    # Get Menu Item
    options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
    # Get Nav Bar Menu Item
    navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
    # --------------------------------------------------------------------
    alert = get_object_or_404(Alert, Slug = id, Part = '9', Seen = False)
    banner = get_object_or_404(ProductBanner, id = id)

    context = {
        'This_User_Profile':this_profile,
        'This_User_Inverntory': this_inverntory,
        'Options': options,
        'MenuList':navbar,
        'Alert':alert,
        'Banner':banner,
    }
        
    return render(request, 'nakhll_market/alert/pages/editeproductbanner.html', context)


# Edite Shop Alert
@login_required
@staff_member_required
def EditeShopAlert(request, id):
    # Get User Info
    this_profile = Profile.objects.get(FK_User=request.user)
    this_inverntory = request.user.WalletManager.Inverntory
    # Get Menu Item
    options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
    # Get Nav Bar Menu Item
    navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
    # --------------------------------------------------------------------
    alert = get_object_or_404(Alert, Slug = id, Part = '3', Seen = False)
    shop = get_object_or_404(Shop, ID = id)

    holidays = []
    # Get Filed
    for item in alert.FK_Field.all():
        if item.Title == 'SubMarket':
            submarket_list = []
            submarkets = item.Value.split('~')
            try:
                for item in submarkets:
                    if SubMarket.objects.filter(ID = item).exists():
                        submarket_list.append(SubMarket.objects.get(ID = item))
            except:
                continue

        elif item.Title == 'Holidays':
            holidaysobject = item.Value.split('-')
            for item in holidaysobject:
                if item == '0':
                    holidays.append('شنبه')
                elif item == '1':
                    holidays.append('یک شنبه')
                elif item == '2':
                    holidays.append('دو شنبه')
                elif item == '3':
                    holidays.append('سه شنبه')
                elif item == '4':
                    holidays.append('چهار شنبه')
                elif item == '5':
                    holidays.append('پنج شنبه')
                elif item == '6':
                    holidays.append('جمعه')

    context = {
        'This_User_Profile':this_profile,
        'This_User_Inverntory': this_inverntory,
        'Options': options,
        'MenuList':navbar,
        'Alert':alert,
        'Shop':shop,
        'Submarkets':submarket_list,
        'Holidays':holidays,
    }
    
    return render(request, 'nakhll_market/alert/pages/editeshop.html', context)


# Edit Product Alert
@login_required
@staff_member_required
def EditeProductAlert(request, id):
    this_profile = Profile.objects.get(FK_User=request.user)
    this_inverntory = request.user.WalletManager.Inverntory
    # Get Menu Item
    options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
    # Get Nav Bar Menu Item
    navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
    # --------------------------------------------------------------------
    alert = get_object_or_404(Alert, Slug = id, Part = '7', Seen = False)
    this_product = get_object_or_404(Product, ID = id)

    # Get Shop Title
    this_shop = None
    this_submarket = None
    pfiled = None
    Epfiled = None
    all_category = []

    # Get Filed
    for item in alert.FK_Field.all():
        if item.Title == 'PostRange':
            if item.Value != 'remove':
                pfiled = item.Value
        elif item.Title == 'ExePostRange':
            if item.Value != 'remove':
                Epfiled = item.Value
        elif item.Title == 'Shop':
            this_shop = get_object_or_404(Shop, ID = item.Value).Title
        elif item.Title == 'SubMarket':
            this_submarket = get_object_or_404(SubMarket, ID = item.Value).Title
        elif item.Title == 'Category':
            Category_List = item.Value.split('-')
            for item in Category_List:
                try:
                    if Category.objects.filter(Title = item).exists():
                        all_category.append(Category.objects.get(Title = item))
                    elif Category.objects.filter(id = item).exists():
                        all_category.append(Category.objects.get(id = item))
                except:
                    continue
    # Get Product Post Range
    PostRangeList = []
    if pfiled != None:
        postrange_str = pfiled.split('-')
        for item in postrange_str:
            try:
                if PostRange.objects.filter(id = item).exists():
                    PostRangeList.append(PostRange.objects.get(id = item))
            except:
                continue
    # Get Product Exe Post Range
    ExePostRangeList = []
    if Epfiled != None:
        exepostrange_str = Epfiled.split('-')
        for item in exepostrange_str:
            try:
                if PostRange.objects.filter(id = item).exists():
                    ExePostRangeList.append(PostRange.objects.get(id = item))
            except:
                continue

    context = {
        'This_User_Profile':this_profile,
        'This_User_Inverntory': this_inverntory,
        'Options': options,
        'MenuList':navbar,
        'Alert':alert,
        'Product':this_product,
        'PostRange':PostRangeList,
        'ExePostRange':ExePostRangeList,
        'This_Shop':this_shop,
        'This_Submarket':this_submarket,
        'Categories':all_category,
    }
        
    return render(request, 'nakhll_market/alert/pages/editeproduct.html', context)


# Ticket Alert
@login_required
@staff_member_required
def TicketAlert(request, id):
    # Get User Info
    this_profile = Profile.objects.get(FK_User=request.user)
    this_inverntory = request.user.WalletManager.Inverntory
    # Get Menu Item
    options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
    # Get Nav Bar Menu Item
    navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
    # -------------------------------------------------------------------
    # Get This Ticket
    ticket = get_object_or_404(Ticketing, ID = id)
    # Build Class
    class Replay:
        def __init__(self, id, username, userimage, des, date_create, father_id):
            self.ID = id
            self.name = username
            self.image = userimage
            self.descriptino = des
            self.date = date_create
            self.father = father_id
    # Get All Ticket`s Message
    ticket_replay_list = []
    for item in TicketingMessage.objects.filter(FK_Replay_id = ticket.ID).order_by('Date'):
        name = item.FK_Importer.first_name + ' ' + item.FK_Importer.last_name
        image = Profile.objects.get(FK_User = item.FK_Importer).Image_thumbnail_url
        new_item = Replay(item.ID, name, image, item.Description, item.Date, item.FK_Replay.ID)
        ticket_replay_list.append(new_item)

    context = {
        'This_User_Profile':this_profile,
        'This_User_Inverntory': this_inverntory,
        'Options': options,
        'MenuList':navbar,
        'ThisTicket':ticket,
        'ReplayTicket':ticket_replay_list,
    }
    return render(request, 'nakhll_market/alert/pages/ticketalert.html', context)


# Attribute Price Alert
@login_required
@staff_member_required
def AttributePriceAlert(request, id):
    # Get User Info
    this_profile = Profile.objects.get(FK_User=request.user)
    this_inverntory = request.user.WalletManager.Inverntory
    # Get Menu Item
    options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
    # Get Nav Bar Menu Item
    navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
    # -------------------------------------------------------------------
    # get this attribute price
    this_attribute_price = AttrPrice.objects.get(id = id)

    context = {
        'This_User_Profile':this_profile,
        'This_User_Inverntory': this_inverntory,
        'Options': options,
        'MenuList':navbar,
        'AttrPrice':this_attribute_price,
    }
        
    return render(request, 'nakhll_market/alert/pages/attributepricealert.html', context)



# Connect Us Alert
@login_required
@staff_member_required
def ConnectUsAlert(request, id):
    # Get User Info
    this_profile = Profile.objects.get(FK_User=request.user)
    this_inverntory = request.user.WalletManager.Inverntory
    # Get Menu Item
    options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
    # Get Nav Bar Menu Item
    navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
    # -------------------------------------------------------------------
    # Get User Connect Massage
    meg = Complaint.objects.get(id = id)

    context = {
        'This_User_Profile':this_profile,
        'This_User_Inverntory': this_inverntory,
        'Options': options,
        'MenuList':navbar,
        'Complint':meg,
    }
        
    return render(request, 'nakhll_market/alert/pages/connectusalert.html', context)


# Factor Alert
@login_required
@staff_member_required
def FactorAlert(request, id):
    # Get User Info
    this_profile = Profile.objects.get(FK_User=request.user)
    this_inverntory = request.user.WalletManager.Inverntory
    # Get Menu Item
    options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
    # Get Nav Bar Menu Item
    navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
    # -------------------------------------------------------------------
    # get thid factor
    this_factor = get_object_or_404(Factor, ID = id)

    context = {
        'This_User_Profile':this_profile,
        'This_User_Inverntory': this_inverntory,
        'Options': options,
        'MenuList':navbar,
        'factor':this_factor,
    }
        
    return render(request, 'nakhll_market/alert/pages/factoralert.html', context)


# Delete Shop Banner Alert
@login_required
@staff_member_required
def DeleteShopBannerAlert(request, id):
    # Get User Info
    this_profile = Profile.objects.get(FK_User=request.user)
    this_inverntory = request.user.WalletManager.Inverntory
    # Get Menu Item
    options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
    # Get Nav Bar Menu Item
    navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
    # --------------------------------------------------------------------
    # Get This Banner
    this_banner = get_object_or_404(ShopBanner, id = id)

    context = {
        'This_User_Profile':this_profile,
        'This_User_Inverntory': this_inverntory,
        'Options': options,
        'MenuList':navbar,
        'Banner':this_banner,
    }
        
    return render(request, 'nakhll_market/alert/pages/deleteshopbanneralert.html', context)


# Delete Product Banner Alert
@login_required
@staff_member_required
def DeleteProductBannerAlert(request, id):
    # Get User Info
    this_profile = Profile.objects.get(FK_User=request.user)
    this_inverntory = request.user.WalletManager.Inverntory
    # Get Menu Item
    options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
    # Get Nav Bar Menu Item
    navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
    # --------------------------------------------------------------------
    # get this banner
    banner = get_object_or_404(ProductBanner, id = id)

    context = {
        'This_User_Profile':this_profile,
        'This_User_Inverntory': this_inverntory,
        'Options': options,
        'MenuList':navbar,
        'Banner':banner,
    }
        
    return render(request, 'nakhll_market/alert/pages/deleteproductbanneralert.html', context)


# Delete Attribute Product Alert
@login_required
@staff_member_required
def DeleteAttributeProductAlert(request, id):
    # Get User Info
    this_profile = Profile.objects.get(FK_User=request.user)
    this_inverntory = request.user.WalletManager.Inverntory
    # Get Menu Item
    options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
    # Get Nav Bar Menu Item
    navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
    # --------------------------------------------------------------------
    # get this attribute product
    attrpro = get_object_or_404(AttrProduct, id = id)

    context = {
        'This_User_Profile':this_profile,
        'This_User_Inverntory': this_inverntory,
        'Options': options,
        'MenuList':navbar,
        'AttrPro':attrpro,
    }
        
    return render(request, 'nakhll_market/alert/pages/deleteattrproduct.html', context)


# Delete Attribute Price Alert
@login_required
@staff_member_required
def DeleteAttributePriceAlert(request, id):
    # Get User Info
    this_profile = Profile.objects.get(FK_User=request.user)
    this_inverntory = request.user.WalletManager.Inverntory
    # Get Menu Item
    options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
    # Get Nav Bar Menu Item
    navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
    # --------------------------------------------------------------------
    # get this product attribute price
    thid_product_attribute_price = get_object_or_404(AttrPrice, id = id)

    context = {
        'This_User_Profile':this_profile,
        'This_User_Inverntory': this_inverntory,
        'Options': options,
        'MenuList':navbar,
        'AttrPrice':thid_product_attribute_price,
    }
        
    return render(request, 'nakhll_market/alert/pages/deleteattrprice.html', context)


# Order Alert
@login_required
@staff_member_required
def OrderAlert(request, id):
    # Get User Info
    this_profile = Profile.objects.get(FK_User=request.user)
    this_inverntory = request.user.WalletManager.Inverntory
    # Get Menu Item
    options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
    # Get Nav Bar Menu Item
    navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
    # --------------------------------------------------------------------
    # get this alert
    alert = get_object_or_404(Alert, id = id)
    # get this factor
    factor = get_object_or_404(Factor, ID = alert.Slug)

    context = {
        'This_User_Profile':this_profile,
        'This_User_Inverntory': this_inverntory,
        'Options': options,
        'MenuList':navbar,
        'factor':factor,
    }
        
    return render(request, 'nakhll_market/alert/pages/orderalert.html', context)


# Send Info Alert
@login_required
@staff_member_required
def SendInfoAlert(request, id):
    # Get User Info
    this_profile = Profile.objects.get(FK_User=request.user)
    this_inverntory = request.user.WalletManager.Inverntory
    # Get Menu Item
    options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
    # Get Nav Bar Menu Item
    navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
    # --------------------------------------------------------------------
    # get this alert
    alert = get_object_or_404(Alert, id = id)
    # get thid barcode
    bar = get_object_or_404(PostBarCode, id = alert.Slug)
    # get thid factor
    factor = bar.FK_Factor

    context = {
        'This_User_Profile':this_profile,
        'This_User_Inverntory': this_inverntory,
        'Options': options,
        'MenuList':navbar,
        'factor':factor,
        'Barcode':bar,
        'SendDate':str(bar.SendDate),
    }
        
    return render(request, 'nakhll_market/alert/pages/sendinfoalert.html', context)


# Cansel Order Alert
@login_required
@staff_member_required
def CanselOrderAlert(request, id):
    # Get User Info
    this_profile = Profile.objects.get(FK_User=request.user)
    this_inverntory = request.user.WalletManager.Inverntory
    # Get Menu Item
    options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
    # Get Nav Bar Menu Item
    navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
    # --------------------------------------------------------------------
    # get alert
    alert = get_object_or_404(Alert, id = id)
    # Get Factor Number
    factor = get_object_or_404(Factor, ID = alert.Slug)

    context = {
        'This_User_Profile':this_profile,
        'This_User_Inverntory': this_inverntory,
        'Options': options,
        'MenuList':navbar,
        'factor':factor,
        'Alert':alert,
    }
        
    return render(request, 'nakhll_market/alert/pages/canselorder.html', context)



# Delete Coupon Alert
@login_required
@staff_member_required
def DeleteCouponAlert(request, id):
    # Get User Info
    this_profile = Profile.objects.get(FK_User=request.user)
    this_inverntory = request.user.WalletManager.Inverntory
    # Get Menu Item
    options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
    # Get Nav Bar Menu Item
    navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
    # --------------------------------------------------------------------
    # get this coupon
    coupon = get_object_or_404(Coupon, id = id)

    context = {
        'This_User_Profile':this_profile,
        'This_User_Inverntory': this_inverntory,
        'Options': options,
        'MenuList':navbar,
        'Coupon':coupon,
    }
        
    return render(request, 'nakhll_market/alert/pages/deletecouponalert.html', context)



# Add Coupon Alert
@login_required
@staff_member_required
def AddCouponAlert(request, id):
    # Get User Info
    this_profile = Profile.objects.get(FK_User=request.user)
    this_inverntory = request.user.WalletManager.Inverntory
    # Get Menu Item
    options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
    # Get Nav Bar Menu Item
    navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
    # --------------------------------------------------------------------
    # get this coupon
    coupon = get_object_or_404(Coupon, id = id)
    print(coupon.FK_Shops.count())

    context = {
        'This_User_Profile':this_profile,
        'This_User_Inverntory': this_inverntory,
        'Options': options,
        'MenuList':navbar,
        'Coupon':coupon,
    }

    return render(request, 'nakhll_market/alert/pages/couponalert.html', context)


# Record Shop Comment Alert
@login_required
@staff_member_required
def RecordShopCommentAlert(request, id):
    if request.method == 'POST':
        try:
            Type = request.POST["accept-btn"]
        except MultiValueDictKeyError:
            Type = False
        try:
            Dec = request.POST["Des"]
        except MultiValueDictKeyError:
            Dec = False
        if Type == '1': 
            if Dec != False:
                # get this alert
                this_alert = get_object_or_404(Alert, id = id)
                # get this comment
                this_comment = get_object_or_404(ShopComment, id = this_alert.Slug)
                # get Uuser profile
                profile = get_object_or_404(Profile, FK_User = this_alert.FK_User)
                # send sms
                SendAlertResponse('ثبت-کامنت-حجره', Dec, profile.MobileNumber)
                # change alert data
                this_alert.Seen = True
                this_alert.Status = True
                this_alert.FK_Staff = request.user
                this_alert.save()
                # change comment
                this_comment.Available = True
                this_comment.FK_User = request.user
                this_comment.save()
        else:
            if Dec != False:
                # get this alert
                this_alert = get_object_or_404(Alert, id = id)
                # get this comment
                this_comment = get_object_or_404(ShopComment, id = this_alert.Slug)
                # get Uuser profile
                profile = get_object_or_404(Profile, FK_User = this_alert.FK_User)
                # send sms
                SendAlertResponse('عدم-ثبت-کامنت-حجره', Dec, profile.MobileNumber)
                # change alert data
                this_alert.Seen = True
                this_alert.Status = False
                this_alert.FK_Staff = request.user
                this_alert.save()
                # change comment
                this_comment.Available = False
                this_comment.FK_User = request.user
                this_comment.save()

        return redirect("nakhll_market:Alert")
    else:
        # Get User Info
        this_profile = Profile.objects.get(FK_User=request.user)
        this_inverntory = request.user.WalletManager.Inverntory
        # Get Menu Item
        options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
        # Get Nav Bar Menu Item
        navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
        # --------------------------------------------------------------------
        # Get Alert
        this_alert = get_object_or_404(Alert, id = id)
        # Get Comment
        this_comment = get_object_or_404(ShopComment, id = this_alert.Slug) 

        context = {
            'This_User_Profile':this_profile,
            'This_User_Inverntory': this_inverntory,
            'Options': options,
            'MenuList':navbar,
            'Comment':this_comment,
        }
            
        return render(request, 'nakhll_market/alert/pages/shopcommentalert.html', context)


# Checkout By User Alert
@login_required
@staff_member_required
def Checkout_By_User_Alert(request, id):
   # Check User Status
    if request.user.is_authenticated :
        if request.method == 'POST':
            try:
                Type = request.POST["accept-btn"]
            except MultiValueDictKeyError:
                Type = False
            try:
                Dec = request.POST["Des"]
            except MultiValueDictKeyError:
                Dec = False

            if Type == '1': 
                if Dec != False:
                    # Get Alert
                    this_alert = get_object_or_404(Alert, id = id)
                    # Change Alert Data
                    this_alert.Seen = True
                    this_alert.Status = True
                    this_alert.FK_Staff = request.user
                    this_alert.save()
            else:
                if Dec != False:
                    # Get Alert
                    this_alert = get_object_or_404(Alert, id = id)
                    # Change Alert Data
                    this_alert.Seen = True
                    this_alert.Status = False
                    this_alert.FK_Staff = request.user
                    this_alert.save()
            return redirect("nakhll_market:Alert")
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
            # ----------------------------------------------------------------
            # Get Alert
            this_alert = get_object_or_404(Alert, id = id)

            context = {
                'This_User_Profile':this_profile,
                'This_User_Inverntory': this_inverntory,
                'Options': options,
                'MenuList':navbar,
                'Alert':this_alert,
            }
                
            return render(request, 'nakhll_market/alert/pages/checkoutalert.html', context)
    else:
        return redirect("auth:get-phone")



# Add New Optional Attribute Alert
@login_required
@staff_member_required
def Add_New_Optional_Attribute(request, id):
    if request.method == 'POST':
        try:
            Type = request.POST["accept-btn"]
        except MultiValueDictKeyError:
            Type = False

        try:
            Dec = request.POST["Des"]
        except MultiValueDictKeyError:
            Dec = False

        if Type == '1': 
            if Dec != False:
                # Get Alert
                this_alert = get_object_or_404(Alert, id = id)
                # get this optional attribute
                this_optional_attribute = get_object_or_404(OptinalAttribute, id = this_alert.Slug)
                # Change Alert Data
                this_alert.Seen = True
                this_alert.Status = True
                this_alert.FK_Staff = request.user
                this_alert.save()
                # publish true
                this_optional_attribute.Publish = True
                this_optional_attribute.save()
        else:
            if Dec != False:
                # Get Alert
                this_alert = get_object_or_404(Alert, id = id)
                # get this optional attribute
                this_optional_attribute = get_object_or_404(OptinalAttribute, id = this_alert.Slug)
                # get this product
                this_product = None
                user_shop = list(Shop.objects.filter(FK_ShopManager = this_alert.FK_User))
                for item in Product.objects.filter(FK_Shop__in = user_shop):
                    if this_optional_attribute in list(item.FK_OptinalAttribute.all()):
                        this_product = item
                # Change Alert Data
                this_alert.Seen = True
                this_alert.Status = False
                this_alert.FK_Staff = request.user
                this_alert.save()
                # delete data
                this_product.FK_OptinalAttribute.remove(this_optional_attribute)
                this_optional_attribute.delete()

        return redirect("nakhll_market:Alert")
    else:
        # Get User Info
        this_profile = Profile.objects.get(FK_User=request.user)
        this_inverntory = request.user.WalletManager.Inverntory
        # Get Menu Item
        options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
        # Get Nav Bar Menu Item
        navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
        # ----------------------------------------------------------------
        # Get Alert
        this_alert = get_object_or_404(Alert, id = id)
        # get optional attribute object
        this_optional_attribute = get_object_or_404(OptinalAttribute, id = this_alert.Slug)
        # get this product
        this_product = None
        user_shop = list(Shop.objects.filter(FK_ShopManager = this_alert.FK_User))
        for item in Product.objects.filter(FK_Shop__in = user_shop):
            if this_optional_attribute in list(item.FK_OptinalAttribute.all()):
                this_product = item

        context = {
            'This_User_Profile':this_profile,
            'This_User_Inverntory': this_inverntory,
            'Options': options,
            'MenuList':navbar,
            'ThisOptionalAttribute':this_optional_attribute,
            'ThisProduct':this_product,
            'ThisAlert':this_alert,
        }
            
        return render(request, 'nakhll_market/alert/pages/optionalattribute.html', context)



# Delete New Optional Attribute Alert
@login_required
@staff_member_required
def Delete_Optional_Attribute(request, id):
    if request.method == 'POST':

        # Get Alert
        this_alert = get_object_or_404(Alert, id = id)
        # get this optional attribute
        this_optional_attribute = get_object_or_404(OptinalAttribute, id = this_alert.Slug)
        # get this product
        this_product = None
        user_shop = list(Shop.objects.filter(FK_ShopManager = this_alert.FK_User))
        for item in Product.objects.filter(FK_Shop__in = user_shop):
            if this_optional_attribute in list(item.FK_OptinalAttribute.all()):
                this_product = item
        # Change Alert Data
        this_alert.Seen = True
        this_alert.Status = False
        this_alert.FK_Staff = request.user
        this_alert.save()
        # delete optional attribute
        for item in this_optional_attribute.FK_Details.all():
            this_optional_attribute.FK_Details.remove(item)
            item.delete()
        this_product.FK_OptinalAttribute.remove(this_optional_attribute)
        this_optional_attribute.delete()

        return redirect("nakhll_market:Alert")
    else:
        # Get User Info
        this_profile = Profile.objects.get(FK_User=request.user)
        this_inverntory = request.user.WalletManager.Inverntory
        # Get Menu Item
        options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
        # Get Nav Bar Menu Item
        navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
        # ----------------------------------------------------------------
        # Get Alert
        this_alert = get_object_or_404(Alert, id = id)
        # get optional attribute object
        this_optional_attribute = get_object_or_404(OptinalAttribute, id = this_alert.Slug)
        # get this product
        this_product = None
        user_shop = list(Shop.objects.filter(FK_ShopManager = this_alert.FK_User))
        for item in Product.objects.filter(FK_Shop__in = user_shop):
            if this_optional_attribute in list(item.FK_OptinalAttribute.all()):
                this_product = item

        context = {
            'This_User_Profile':this_profile,
            'This_User_Inverntory': this_inverntory,
            'Options': options,
            'MenuList':navbar,
            'ThisOptionalAttribute':this_optional_attribute,
            'ThisProduct':this_product,
            'ThisAlert':this_alert,
        }
            
        return render(request, 'nakhll_market/alert/pages/deleteoptionalattribute.html', context)







































# Record Add Coupon Alert
@login_required
@staff_member_required
def RecordAddCouponAlert(request, id):
    if request.method == 'POST':
        
        try:
            Type = request.POST["accept-btn"]
        except MultiValueDictKeyError:
            Type = False

        try:
            Dec = request.POST["Des"]
        except MultiValueDictKeyError:
            Dec = False

        # Get Coupon
        coupon = Coupon.objects.get(id = id)
        # Get User Profile
        profile = Profile.objects.get(FK_User = coupon.FK_Creator)

        if Type == '1': 

            if Dec != False:

                alert = Alert.objects.get(Slug = id, Part ='26', Seen = False)
                alert.Seen = True
                alert.Status = True
                alert.Description = Dec
                alert.FK_Staff = request.user
                alert.save()
                coupon.Publish = True
                coupon.FK_User = request.user
                coupon.save()

                SendAlertResponse('ایجاد-کوپن', Dec, profile.MobileNumber)
            
        else:

            if Dec != False:

                SendAlertResponse('ایجاد-کوپن', Dec, profile.MobileNumber)

                alert = Alert.objects.get(Slug = id, Part ='26', Seen = False)
                alert.Seen = True
                alert.Status = False
                alert.Description = Dec
                alert.FK_Staff = request.user
                alert.save()
                coupon.Available = False
                coupon.save()

        # ----------------------------------------------------------------
        return redirect("nakhll_market:Alert")



# Record Delete Coupon Alert
@login_required
@staff_member_required
def RecordDeleteCouponAlert(request, id):
    if request.method == 'POST':
        alert = Alert.objects.get(Slug = id, Part ='27', Seen = False)
        alert.Seen = True
        alert.Status = True
        alert.FK_Staff = request.user
        alert.save()

        # Get Coupon
        coupon = Coupon.objects.get(id = id)
        # Change Coupon Status
        coupon.Available = False
        coupon.save()
        return redirect("nakhll_market:Alert")


# Record Cansel Order Alert
@login_required
@staff_member_required
def RecordCanselOrderAlert(request, id):
    if request.method == 'POST':
        alert = Alert.objects.get(id = id, Part ='13', Seen = False)
        alert.Seen = True
        alert.Status = True
        alert.FK_Staff = request.user
        alert.save()
        # get this factor
        this_factor = get_object_or_404(Factor, ID = alert.Slug)
        # get user profile
        this_user_profile = Profile.objects.get(FK_User = this_factor.FK_User)
        # send sms
        url = 'https://api.kavenegar.com/v1/{}/verify/lookup.json'.format(KAVENEGAR_KEY) 
        params = {'receptor': this_user_profile.MobileNumber, 'token' : this_factor.FactorNumber, 'template' : 'cansel-factore'}
        requests.post(url, params = params)
        return redirect("nakhll_market:Alert")


# Record Send Info Alert
@login_required
@staff_member_required
def RecordSendInfoAlert(request, id):
    if request.method == 'POST':
        
        try:
            Type = request.POST["accept-btn"]
        except MultiValueDictKeyError:
            Type = False

        try:
            Dec = request.POST["Des"]
        except MultiValueDictKeyError:
            Dec = False

        if Type == '1': 

            if Dec != False:

                alert = get_object_or_404(Alert, Slug = id, Part ='21', Seen = False)
                alert.Seen = True
                alert.Status = True
                alert.Description = Dec
                alert.FK_Staff = request.user
                alert.save()

                # Get Barcode
                bar = get_object_or_404(PostBarCode, id = id)
                # Get Factor
                factor = bar.FK_Factor
                # This Profile
                profile = get_object_or_404(Profile, FK_User = alert.FK_User)
                # Factor Item
                factor_item = []

                # موقت تا درست شده آپ موبایل
                if bar.FK_Products.all().count() != 0:
                    for item in factor.FK_FactorPost.all():
                        if item.FK_Product in bar.FK_Products.all():
                            factor_item.append(item)
                else:
                    for item in factor.FK_FactorPost.all():
                        if item.FK_Product.FK_Shop.FK_ShopManager == alert.FK_User:
                            factor_item.append(item)

                factor_item = list(dict.fromkeys(factor_item))
                # Change Factor Item Status
                for item in factor_item:
                    item.ProductStatus = '3'
                    item.save()
                # Get All Factor Item Status Is Not = 0
                items = []
                for item in bar.FK_Factor.FK_FactorPost.all():
                    if item.ProductStatus != '0':
                        items.append(item)
                # Get Factor Status
                factor_status = True
                # Chech All Factor Item Status
                for item in items:
                    if item.ProductStatus != '3':
                        factor_status = False
                # Check Factor Status
                if factor_status == True:
                    factor.OrderStatus = '5'
                    factor.save()

                SendAlertResponse('تایید-بارکدپستی', Dec, profile.MobileNumber)
                # Send Push notification
                title = 'تایید ارسال مرسوله'
                description = 'گزارش ارسال مرسوله برای صورت حساب  به شماره ' + factor.FactorNumber + 'تایید شده است.'
                # send_push_notification().run(title, description, profile.MobileNumber)
                SendPostCode(bar.User_Sender, factor.FactorNumber, bar.BarCode, Profile.objects.get(FK_User = factor.FK_User).MobileNumber)
        
        else:

            if Dec != False:

                # Get Alert
                alert = get_object_or_404(Alert, Slug = id, Part ='21', Seen = False)
                # Get Barcode
                bar = get_object_or_404(PostBarCode, id = id)
                # Get Factor
                factor = bar.FK_Factor
                # Get User Profile
                profile = get_object_or_404(Profile, FK_User = alert.FK_User)
                
                SendAlertResponse('عدم-تایید-بارکدپستی', Dec, profile.MobileNumber)
                # Send Push notification
                title = 'عدم تایید ارسال مرسوله'
                description = 'گزارش ارسال مرسوله برای صورت حساب  به شماره ' + factor.FactorNumber + 'تایید نشده است.'
                # send_push_notification().run(title, description, profile.MobileNumber)

                alert.Seen = True
                alert.Status = False
                alert.Description = Dec
                alert.FK_Staff = request.user
                alert.save()
                bar.delete()

        # ----------------------------------------------------------------
        return redirect("nakhll_market:Alert")


# Record Order Alert
@login_required
@staff_member_required
def RecordOrderAlert(request, id):
        if request.method == 'POST':
            alert = Alert.objects.get(Slug = id, Part ='20', Seen = False)
            alert.Seen = True
            alert.Status = True
            alert.FK_Staff = request.user
            alert.save()
          
            return redirect("nakhll_market:Alert")



# Record Delete Attribute Price  Alert
@login_required
@staff_member_required
def RecordDeleteAttributePrice(request, id):
    if request.method == 'POST':

        # Get AttrProduct
        attrprice = AttrPrice.objects.get(id = id)
        
        # Set Info 
        Des = str(attrprice.FK_Product.Title) + '|' + str(attrprice.Description) + '|' + str(attrprice.Value) + '|' + str(attrprice.ExtraPrice) + '|' + str(attrprice.Unit)
        # Delete AttrProduct
        attrprice.delete()

        alert = Alert.objects.get(Slug = id, Part ='25', Seen = False)
        alert.Seen = True
        alert.Status = True
        alert.Description = Des
        alert.FK_Staff = request.user
        alert.save()
        
        return redirect("nakhll_market:Alert")


# Record Delete Attribute Product  Alert
@login_required
@staff_member_required
def RecordDeleteAttributeProduct(request, id):
    if request.method == 'POST':

        # Get AttrProduct
        attrpro = AttrProduct.objects.get(id = id)
        # Get Attribute
        attr = Attribute.objects.get(id = attrpro.FK_Attribute.id)
        # Set Info 
        Des = str(attr.Title) + '|' + str(attr.Unit) + '|' + str(attrpro.Value)
        # Delete AttrProduct
        attrpro.delete()

        alert = Alert.objects.get(Slug = id, Part ='24', Seen = False)
        alert.Seen = True
        alert.Status = True
        alert.Description = Des
        alert.FK_Staff = request.user
        alert.save()
        
        return redirect("nakhll_market:Alert")


# Record Delete Product Banner Alert
@login_required
@staff_member_required
def RecordDeleteProductBanner(request, id):
    if request.method == 'POST':

        # Get Banner
        banner = ProductBanner.objects.get(id = id)
        # Set Info 
        Des = str(banner.Title) + '|' + str(banner.Description) + '|' + str(banner.URL) + '|' + str(banner.BannerBuilder) + '|' + str(banner.BannerURL) + '|' + str(banner.Image)
        # Delete Banner
        banner.delete()

        alert = Alert.objects.get(Slug = id, Part ='23', Seen = False)
        alert.Seen = True
        alert.Status = True
        alert.Description = Des
        alert.FK_Staff = request.user
        alert.save()
        
        return redirect("nakhll_market:Alert")


# Record Delete Shop Banner Alert
@login_required
@staff_member_required
def RecordDeleteShopBanner(request, id):
    if request.method == 'POST':
        # Get This Shop Banner
        this_banner = ShopBanner.objects.get(id = id)
        # Set Info 
        Des = str(this_banner.Title) + '|' + str(this_banner.Description) + '|' + str(this_banner.URL) + '|' + str(this_banner.BannerBuilder) + '|' + str(this_banner.BannerURL) + '|' + str(this_banner.Image)
        # Delete This Shop Banner
        this_banner.delete()

        alert = Alert.objects.get(Slug = id, Part ='22', Seen = False)
        alert.Seen = True
        alert.Status = True
        alert.FK_Staff = request.user
        alert.Description = Des
        alert.save()
        return redirect("nakhll_market:Alert")

# Recor Factor Alert
@login_required
@staff_member_required
def RecorFactorAlert(request, id):
    if request.method == 'POST':

        try:
            Type = request.POST["accept-btn"]
        except MultiValueDictKeyError:
            Type = False

        try:
            Dec = request.POST["Des"]
        except MultiValueDictKeyError:
            Dec = False

        alert = get_object_or_404(Alert, Slug = id, Part = '12', Seen = False)
        factor = Factor.objects.get(ID = id)
        profile = Profile.objects.get(FK_User = factor.FK_User)

        if Type == '1': 

            # Shop Profile List
            ShopPeofileList = []
            # Get All Shoper In Factor
            for FactorPost_item in factor.FK_FactorPost.all():
                this_profile = Profile.objects.get(FK_User = FactorPost_item.FK_Product.FK_Shop.FK_ShopManager)
                ShopPeofileList.append(this_profile)

            ShopPeofileList = list(dict.fromkeys(ShopPeofileList))

            if Dec != False:

                factor.Publish = True
                factor.FK_Staff = request.user
                factor.save()
                alert = Alert.objects.get(Slug = id, Part ='12', Seen = False)
                alert.Seen = True
                alert.Status = True
                alert.Description = Dec
                alert.FK_Staff = request.user
                alert.save()

                SendAlertResponse('ثبت-سفارش', Dec, profile.MobileNumber)

                for item in ShopPeofileList:
                    url = 'https://api.kavenegar.com/v1/{}/verify/lookup.json'.format(KAVENEGAR_KEY) 
                    params = {'receptor': item.MobileNumber, 'token' : factor.FactorNumber, 'template' : 'nakhll-order'}
                    requests.post(url, params = params)
                    # Send Push notification
                    title = 'سفارش جدید'
                    description = 'سفارش جدیدی به شماره ' + factor.FactorNumber + 'برای حجره شما ثبت شده است.'
                    # send_push_notification().run(title, description, profile.MobileNumber)
        else:

            if Dec != False:

                SendAlertResponse('عدم-ثبت-سفارش', Dec, profile.MobileNumber)

                alert = Alert.objects.get(Slug = id, Part ='12', Seen = False)
                alert.Seen = True
                alert.Status = False
                alert.Description = Dec
                alert.FK_Staff = request.user
                alert.save()
                # Change Factor Item Inventory
                for item in factor.FK_FactorPost.all():
                    if item.FK_Product.Status == '1':
                        item.FK_Product.Inventory += item.ProductCount
                        item.FK_Product.save()
                factor.Publish = False
                factor.OrderStatus = '4'
                factor.FK_Staff = request.user
                factor.save()
        
        return redirect("nakhll_market:Alert")



# Record Connect Us Alert
@login_required
@staff_member_required
def RecorConnectUsAlert(request, id):
    if request.method == 'POST':
        alert = Alert.objects.get(Slug = id, Part ='18', Seen = False)
        alert.Seen = True
        alert.Status = True
        alert.FK_Staff = request.user
        alert.save()
        
        return redirect("nakhll_market:Alert")



# Record Attribut Price Alert
@login_required
@staff_member_required
def RecorAttributePriceAlert(request, id):
    if request.method == 'POST':
        try:
            Type = request.POST["accept-btn"]
        except MultiValueDictKeyError:
            Type = False

        try:
            Dec = request.POST["Des"]
        except MultiValueDictKeyError:
            Dec = False

        alert = Alert.objects.get(Slug = id, Part = '17', Seen = False)
        attrprice = AttrPrice.objects.get(id = id)
        pro = Product.objects.get(ID = attrprice.FK_Product.ID)
        shop = Shop.objects.get(ID = pro.FK_Shop.ID)
        profile = Profile.objects.get(FK_User = shop.FK_ShopManager)

        if Type == '1': 

            attrprice.Publish = True
            attrprice.save()
            alert = Alert.objects.get(Slug = id, Part ='17', Seen = False)
            alert.Seen = True
            alert.Status = True
            alert.Description = Dec
            alert.FK_Staff = request.user
            alert.save()

            if Dec != False:

                SendAlertResponse('تایید-ارزش-ویژگی-جدید', Dec, profile.MobileNumber)
                # Send Push notification
                title = 'تایید ارزش ویژگی جدید'
                description = 'ارزش ویژگی جدید شما تایید شد.'
                # send_push_notification().run(title, description, profile.MobileNumber)

        else:

            if Dec != False:

                SendAlertResponse('عدم-تایید-ارزش-ویژگی-جدید', Dec, profile.MobileNumber)
                # Send Push notification
                title = 'عدم تایید ارزش ویژگی جدید'
                description = 'ارزش ویژگی جدید شما تایید نشد.'
                # send_push_notification().run(title, description, profile.MobileNumber)

                # Set Info 
                Des = Dec + '|' + str(attrprice.FK_Product.Title) + '|' + str(attrprice.Description) + '|' + str(attrprice.Value) + '|' + str(attrprice.ExtraPrice) + '|' + str(attrprice.Unit)

                alert = Alert.objects.get(Slug = id, Part ='17', Seen = False)
                alert.Seen = True
                alert.Status = False
                alert.Description = Des
                alert.FK_Staff = request.user
                alert.save()
                attrprice.delete()    
        
        return redirect("nakhll_market:Alert")


# Record Ticket Replay Alert
@login_required
@staff_member_required
def RecorTicketReplayAlert(request, id):
    if request.method == 'POST':
        try:
            Dec = request.POST["Ticket_Description"]
            Status = request.POST["Ticket_Status"]
            # Get This Alert
            this_alert = get_object_or_404(Alert, Slug = id, Part = '16', Seen = False)
            user_profile = get_object_or_404(Profile, FK_User = this_alert.FK_User)
            this_ticket = get_object_or_404(Ticketing, ID = id)
            this_ticket.SeenStatus = Status
            this_ticket.save()
            TicketingMessage.objects.create(Description = Dec, FK_Importer = request.user, FK_Replay = this_ticket)
            this_alert.Seen = True
            this_alert.Status = True
            this_alert.Description = Dec
            this_alert.FK_Staff = request.user
            this_alert.save()
            # Send Push notification
            title = 'تیکت جدید'
            description = 'تیکت شما پاسخ داده شد.'
            # send_push_notification().run(title, description, user_profile.MobileNumber)
            # Send SMS
            SendAlertResponse('پاسخ-تیکت', Dec, user_profile.MobileNumber)
            return redirect("nakhll_market:Alert")
        except Exception as e:
            print(str(e))


# Record Product Alert
@login_required
@staff_member_required
def RecorProductAlert(request, id):
    if request.method == 'POST':
        try:
            Type = request.POST["accept-btn"]
        except MultiValueDictKeyError:
            Type = False

        try:
            Dec = request.POST["Des"]
        except MultiValueDictKeyError:
            Dec = False

        alert = Alert.objects.get(Slug = id, Part = '7', Seen = False)
        product = Product.objects.get(ID = id)
        shop = Shop.objects.get(ID = product.FK_Shop.ID)
        profile = Profile.objects.get(FK_User = shop.FK_ShopManager)

        if Type == '1':
            
            for field in alert.FK_Field.all():
                if field.Title == 'Title':
                    product.Title = field.Value
                elif field.Title == 'Image':
                    product.Image = product.NewImage
                elif field.Title == 'Description':
                    product.Description = field.Value
                elif field.Title == 'Shop':
                    shop = Shop.objects.get(ID = field.Value)
                    product.FK_Shop = shop
                elif field.Title == 'Category':
                    for item in product.FK_Category.all():
                        product.FK_Category.remove(item)
                    categories_str = field.Value.split('-')
                    for item in categories_str:
                        try:
                            if Category.objects.filter(Title = item).exists():
                                product.FK_Category.add(Category.objects.get(Title = item))
                            elif Category.objects.filter(id = item).exists():
                                product.FK_Category.add(Category.objects.get(id = item))
                        except:
                            continue
                elif field.Title == 'PostRange':
                    if field.Value == 'remove': 
                        for item in product.FK_PostRange.all():
                                product.FK_PostRange.remove(item)
                    else:
                        for item in product.FK_PostRange.all():
                            product.FK_PostRange.remove(item)
                        try:
                            postrange_str = field.Value.split('-')
                            for item in postrange_str:
                                if PostRange.objects.filter(id = item).exists():
                                    product.FK_PostRange.add(PostRange.objects.get(id = item))
                        except:
                            continue   
                elif field.Title == 'ExePostRange':
                    if field.Value == 'remove':
                        for item in product.FK_ExceptionPostRange.all():
                            product.FK_ExceptionPostRange.remove(item)
                    else:
                        for item in product.FK_ExceptionPostRange.all():
                            product.FK_ExceptionPostRange.remove(item)
                        try:
                            exepostrange_str = field.Value.split('-')
                            for item in exepostrange_str:
                                if PostRange.objects.filter(id = item).exists():
                                    product.FK_ExceptionPostRange.add(PostRange.objects.get(id = item))
                        except:
                            continue
                elif field.Title == 'Story':
                    product.Story = field.Value
                elif field.Title == 'Price':
                    product.Price = field.Value
                elif field.Title == 'OldPrice':
                    product.OldPrice = field.Value
                elif field.Title == 'ProdRange':
                    product.PostRangeType = field.Value
                elif field.Title == 'ProdPostType':
                    product.Status = field.Value
                elif field.Title == 'ProdTypeSend':
                    product.PostType = field.Value
                elif field.Title == 'PostPriceProd':
                    product.PostPrice = field.Value
                elif field.Title == 'Bio':
                    product.Bio = field.Value
                elif field.Title == 'ProdNetWeight':
                    product.Net_Weight = field.Value
                elif field.Title == 'ProdPackingWeight':
                    product.Weight_With_Packing = field.Value
                elif field.Title == 'ProdLengthWithPackaging':
                    product.Length_With_Packaging = field.Value
                elif field.Title == 'ProdWidthWithPackaging':
                    product.Width_With_Packaging = field.Value
                elif field.Title == 'ProdHeightWithPackaging':
                    product.Height_With_Packaging = field.Value
                elif field.Title == 'SubMarket':
                    product.FK_SubMarket = SubMarket.objects.get(ID = field.Value)
                elif field.Title == 'ProdInStore':
                    product.Inventory = int(field.Value)
                
                product.save()

            alert = Alert.objects.get(Slug = id, Part ='7', Seen = False)
            alert.Seen = True
            alert.Status = True
            alert.Description = Dec
            alert.FK_Staff = request.user
            alert.save()

            if Dec != False:
                SendAlertResponse('ثبت-ویراش-محصول', Dec, profile.MobileNumber)
                # Send Push notification
                title = 'تایید ویرایش محصول'
                description = 'تغییرات محصول با شناسه ' + product.Slug + 'ثبت شد.'
                # send_push_notification().run(title, description, profile.MobileNumber)
        else:
            if Dec != False:
                SendAlertResponse('عدم-ثبت-ویراش-محصول', Dec, profile.MobileNumber)
                # Send Push notification
                title = 'عدم تایید ویرایش محصول'
                description = 'تغییرات محصول با شناسه ' + product.Slug + 'تایید نشد.'
                # send_push_notification().run(title, description, profile.MobileNumber)

                alert = Alert.objects.get(Slug = id, Part ='7', Seen = False)
                alert.Seen = True
                alert.Status = False
                alert.Description = Dec
                alert.FK_Staff = request.user
                alert.save()       
        return redirect("nakhll_market:Alert")


# Record Shop Alert
@login_required
@staff_member_required
def RecorShopAlert(request, id):
    if request.method == 'POST':
        try:
            Type = request.POST["accept-btn"]
        except MultiValueDictKeyError:
            Type = False

        try:
            Dec = request.POST["Des"]
        except MultiValueDictKeyError:
            Dec = False

        alert = Alert.objects.get(Slug = id, Part = '3', Seen = False)
        shop = Shop.objects.get(ID = id)
        profile = Profile.objects.get(FK_User = shop.FK_ShopManager)

        if Type == '1':
            
            for field in alert.FK_Field.all():
                if field.Title == 'Title':
                    shop.Title = field.Value
                elif field.Title == 'Image':
                    shop.Image = shop.NewImage
                elif field.Title == 'Description':
                    shop.Description = field.Value
                elif field.Title == 'State':
                    shop.State = field.Value
                elif field.Title == 'BigCity':
                    shop.BigCity = field.Value
                elif field.Title == 'City':
                    shop.City = field.Value
                elif field.Title == 'Bio':
                    shop.Bio = field.Value
                elif field.Title == 'SubMarket': 
                    for item in shop.FK_SubMarket.all():
                        shop.FK_SubMarket.remove(item) 
                    submarkets_list = field.Value.split('~')
                    for item in submarkets_list:
                        try:
                            if SubMarket.objects.filter(Title = item).exists():
                                shop.FK_SubMarket.add(SubMarket.objects.get(Title = item))
                            elif SubMarket.objects.filter(ID = item).exists():
                                shop.FK_SubMarket.add(SubMarket.objects.get(ID = item))
                        except:
                            continue
                elif field.Title == 'Holidays':
                    shop.Holidays = field.Value
                
                shop.save()

            alert = Alert.objects.get(Slug = id, Part ='3', Seen = False)
            alert.Seen = True
            alert.Status = True
            alert.Description = Dec
            alert.FK_Staff = request.user
            alert.save()

            if Dec != False:
                SendAlertResponse('ثبت-ویراش-حجره', Dec, profile.MobileNumber)
                # Send Push notification
                title = 'تایید ویرایش حجره'
                description = 'تغییرات حجره با شناسه ' + shop.Slug + 'ثبت شد.'
                # send_push_notification().run(title, description, profile.MobileNumber)
        else:
            if Dec != False:
                SendAlertResponse('عدم-ثبت-ویراش-حجره', Dec, profile.MobileNumber)
                # Send Push notification
                title = 'عدم تایید ویرایش حجره'
                description = 'تغییرات حجره با شناسه ' + shop.Slug + 'تایید نشد.'
                # send_push_notification().run(title, description, profile.MobileNumber)

                alert = Alert.objects.get(Slug = id, Part ='3', Seen = False)
                alert.Seen = True
                alert.Status = False
                alert.Description = Dec
                alert.FK_Staff = request.user
                alert.save()      
        
        return redirect("nakhll_market:Alert")



# Record Shop Banner Alert
@login_required
@staff_member_required
def RecordShopBannerAlert(request, id):
    if request.method == 'POST':
        try:
            Type = request.POST["accept-btn"]
        except MultiValueDictKeyError:
            Type = False

        try:
            Dec = request.POST["Des"]
        except MultiValueDictKeyError:
            Dec = False

        alert = Alert.objects.get(Slug = id, Part = '4', Seen = False)
        banner = ShopBanner.objects.get(id = id)
        shop = Shop.objects.get(ID = banner.FK_Shop.ID)
        profile = Profile.objects.get(FK_User = shop.FK_ShopManager)

        if Type == '1':     

            banner.Publish = True
            banner.save()
            alert = Alert.objects.get(Slug = id, Part ='4', Seen = False)
            alert.Seen = True
            alert.Status = True
            alert.Description = Dec
            alert.FK_Staff = request.user
            alert.save()

            if Dec != False:
                SendAlertResponse('ایجاد-بنر-حجره', Dec, profile.MobileNumber)
                # Send Push notification
                title = 'ثبت بنر حجره جدید'
                description = 'بنر جدید حجره با شناسه ' + shop.Slug + 'تایید شد.'
                # send_push_notification().run(title, description, profile.MobileNumber)

        else:
            if Dec != False:
                SendAlertResponse('عدم-ایجاد-بنر-حجره', Dec, profile.MobileNumber)
                # Send Push notification
                title = 'عدم ثبت بنر حجره جدید'
                description = 'بنر جدید حجره با شناسه ' + shop.Slug + 'تایید نشد.'
                # send_push_notification().run(title, description, profile.MobileNumber)

                # Set Info 
                Des = Dec + '|' + str(banner.Title) + '|' + str(banner.Description) + '|' + str(banner.URL) + '|' + str(banner.BannerBuilder) + '|' + str(banner.BannerURL) + '|' + str(banner.Image)

                alert = Alert.objects.get(Slug = id, Part ='4', Seen = False)
                alert.Seen = True
                alert.Status = False
                alert.Description = Des
                alert.FK_Staff = request.user
                alert.save()
                banner.delete()       
        return redirect("nakhll_market:Alert")


# Record Shop Alert
@login_required
@staff_member_required
def RecordShopAlert(request, id):
    if request.method == 'POST':
        try:
            Type = request.POST["accept-btn"]
        except MultiValueDictKeyError:
            Type = False

        try:
            Dec = request.POST["Des"]
        except MultiValueDictKeyError:
            Dec = False

        alert = Alert.objects.get(Slug = id, Part = '2', Seen = False)
        shop = Shop.objects.get(ID = id)
        profile = Profile.objects.get(FK_User = shop.FK_ShopManager)

        if Type == '1': 

            shop.Publish = True
            shop.save()
            alert = Alert.objects.get(Slug = id, Part ='2', Seen = False)
            alert.Seen = True
            alert.Status = True
            alert.Description = Dec
            alert.FK_Staff = request.user
            alert.save()

            if Dec != False:
                SendAlertResponse('ایجاد-حجره-جدید', Dec, profile.MobileNumber)
                # Send Push notification
                title = 'ثبت حجره جدید'
                description = 'حجره جدید با شناسه ' + shop.Slug + 'تایید شد.'
                # send_push_notification().run(title, description, profile.MobileNumber)
        else:
            if Dec != False:
                SendAlertResponse('عدم-ایجاد-حجره-جدید', Dec, profile.MobileNumber)
                # Send Push notification
                title = 'عدم ثبت حجره جدید'
                description = 'حجره جدید با شناسه ' + shop.Slug + 'تایید نشد.'
                # send_push_notification().run(title, description, profile.MobileNumber)

                alert = Alert.objects.get(Slug = id, Part = '2', Seen = False)
                alert.Seen = True
                alert.Status = False
                alert.Description = Dec
                alert.FK_Staff = request.user
                alert.save()
                shop.Publish = False
                shop.save()        
        
        return redirect("nakhll_market:Alert")


# Record Review Alert
@login_required
@staff_member_required
def RecordReviewAlert(request, id):
    if request.method == 'POST':

        try:
            Type = request.POST["accept-btn"]
        except MultiValueDictKeyError:
            Type = False

        try:
            Dec = request.POST["Des"]
        except MultiValueDictKeyError:
            Dec = False

        alert = Alert.objects.get(Slug = id, Part = '15', Seen = False)
        review = Review.objects.get(id = id)
        profile = Profile.objects.get(FK_User = review.FK_UserAdder)

        if Type == '1':

            review.Available = True
            review.save()
            alert = Alert.objects.get(Slug = id, Part ='15', Seen = False)
            alert.Seen = True
            alert.Status = True
            alert.Description = Dec
            alert.FK_Staff = request.user
            alert.save()

            if Dec != False:
                SendAlertResponse('ثبت-نقدوبررسی-جدید', Dec, profile.MobileNumber)
        else:
            if Dec != False:
                SendAlertResponse('عدم-ثبت-نقدوبررسی-جدید', Dec, profile.MobileNumber)

                alert = Alert.objects.get(Slug = id, Part ='15', Seen = False)
                alert.Seen = True
                alert.Status = False
                alert.Description = Dec
                alert.FK_Staff = request.user
                alert.save()
                review.Available = False
                review.save()      
        
        return redirect("nakhll_market:Alert")


# Record Comment Alert
@login_required
@staff_member_required
def RecordCommentAlert(request, id):
    if request.method == 'POST':

        try:
            Type = request.POST["accept-btn"]
        except MultiValueDictKeyError:
            Type = False

        try:
            Dec = request.POST["Des"]
        except MultiValueDictKeyError:
            Dec = False

        alert = Alert.objects.get(Slug = id, Part = '14', Seen = False)
        comment = Comment.objects.get(id = id)
        profile = Profile.objects.get(FK_User = comment.FK_UserAdder)

        if Type == '1':   

            comment.Available = True
            comment.save()
            alert = Alert.objects.get(Slug = id, Part ='14', Seen = False)
            alert.Seen = True
            alert.Status = True
            alert.Description = Dec
            alert.FK_Staff = request.user
            alert.save()

            if Dec != False:

                SendAlertResponse('ثبت-کامنت-جدید', Dec, profile.MobileNumber)
                # SendMessage(alert.FK_User.id, 'ثبت کامنت جدید', Dec, request.user.id).run()

        else:

            if Dec != False:

                SendAlertResponse('ثبت-کامنت-جدید', Dec, profile.MobileNumber)

                alert = Alert.objects.get(Slug = id, Part ='14', Seen = False)
                alert.Seen = True
                alert.Status = False
                alert.Description = Dec
                alert.FK_Staff = request.user
                alert.save()
                comment.Available = False
                comment.save()        
        
        return redirect("nakhll_market:Alert")


# Record Edite Product Banner Alert
@login_required
@staff_member_required
def RecordEditeProductBannerAlert(request, id):
    if request.method == 'POST':
        try:
            Type = request.POST["accept-btn"]
        except MultiValueDictKeyError:
            Type = False

        try:
            Dec = request.POST["Des"]
        except MultiValueDictKeyError:
            Dec = False

        alert = get_object_or_404(Alert, Slug = id, Part = '9', Seen = False)
        banner = get_object_or_404(ProductBanner, id = id)
        pro = get_object_or_404(Product, ID = banner.FK_Product.ID)
        shop = get_object_or_404(Shop, ID = pro.FK_Shop.ID)
        profile = get_object_or_404(Profile, FK_User = shop.FK_ShopManager)

        if Type == '1':
            for field in alert.FK_Field.all():
                if field.Title == 'Title':
                    banner.Title = field.Value
                elif field.Title == 'Image':
                    banner.Image = banner.NewImage
                elif field.Title == 'Description':
                    banner.Description = field.Value
                elif field.Title == 'URL':
                    banner.URL = field.Value
                elif field.Title == 'BannerBuilder':
                    banner.BannerBuilder = field.Value
                elif field.Title == 'BannerURL':
                    banner.BannerURL = field.Value
                
                banner.Edite = False
                banner.save()

            alert = get_object_or_404(Alert, Slug = id, Part = '9', Seen = False)
            alert.Seen = True
            alert.Status = True
            alert.Description = Dec
            alert.FK_Staff = request.user
            alert.save()

            if Dec != False:
                SendAlertResponse('ثبت-ویراش-بنر-محصول', Dec, profile.MobileNumber)
                # Send Push notification
                title = 'ثبت ویرایش بنر محصول'
                description = 'ویرایش بنر محصول با شناسه ' + pro.Slug + 'تایید شد.'
                # send_push_notification().run(title, description, profile.MobileNumber)
        else:
            if Dec != False:
                SendAlertResponse('عدم-ثبت-ویراش-بنر-محصول', Dec, profile.MobileNumber)
                # Send Push notification
                title = 'عدم ثبت ویرایش بنر محصول'
                description = 'ویرایش بنر محصول با شناسه ' + pro.Slug + 'تایید نشد.'
                # send_push_notification().run(title, description, profile.MobileNumber)

                alert = get_object_or_404(Alert, Slug = id, Part = '9', Seen = False)
                alert.Seen = True
                alert.Status = False
                alert.Description = Dec
                alert.FK_Staff = request.user
                alert.save()
                banner.Edite = False
                banner.save()   
        
        return redirect("nakhll_market:Alert")

# Record Edite Shop Banner Alert
@login_required
@staff_member_required
def RecordEditeShopBannerAlert(request, id):
    if request.method == 'POST':
        try:
            Type = request.POST["accept-btn"]
        except MultiValueDictKeyError:
            Type = False

        try:
            Dec = request.POST["Des"]
        except MultiValueDictKeyError:
            Dec = False

        alert = Alert.objects.get(Slug = id, Part = '5', Seen = False)
        banner = ShopBanner.objects.get(id = id)
        shop = Shop.objects.get(ID = banner.FK_Shop.ID)
        profile = Profile.objects.get(FK_User = shop.FK_ShopManager)

        if Type == '1':
            
            for field in alert.FK_Field.all():
                if field.Title == 'Title':
                    banner.Title = field.Value
                elif field.Title == 'Image':
                    banner.Image = banner.NewImage
                elif field.Title == 'Description':
                    banner.Description = field.Value
                elif field.Title == 'URL':
                    banner.URL = field.Value
                elif field.Title == 'BannerBuilder':
                    banner.BannerBuilder = field.Value
                elif field.Title == 'BannerURL':
                    banner.BannerURL = field.Value
                
                banner.Edite = 0
                banner.save()

            alert = Alert.objects.get(Slug = id, Part ='5', Seen = False)
            alert.Seen = True
            alert.Status = True
            alert.Description = Dec
            alert.FK_Staff = request.user
            alert.save()

            if Dec != False:
                SendAlertResponse('ثبت-ویرایش-بنر-حجره', Dec, profile.MobileNumber)
                # Send Push notification
                title = 'ثبت ویرایش بنر حجره'
                description = 'ویرایش بنر حجره با شناسه ' + shop.Slug + 'تایید شد.'
                # send_push_notification().run(title, description, profile.MobileNumber)
        else:
            if Dec != False:
                SendAlertResponse('عدم-ثبت-ویرایش-بنر-حجره', Dec, profile.MobileNumber)
                # Send Push notification
                title = 'عدم ثبت ویرایش بنر حجره'
                description = 'ویرایش بنر حجره با شناسه ' + shop.Slug + 'تایید نشد.'
                # send_push_notification().run(title, description, profile.MobileNumber)

                alert = Alert.objects.get(Slug = id, Part ='5', Seen = False)
                alert.Seen = True
                alert.Status = False
                alert.Description = Dec
                alert.FK_Staff = request.user
                alert.save()
                banner.Edite = 0
                banner.save()      
        
        return redirect("nakhll_market:Alert")


# Record Product Attribute Alert
@login_required
@staff_member_required
def RecordProductAttributeAlert(request, id):
    if request.method == 'POST':
        try:
            Type = request.POST["accept-btn"]
        except MultiValueDictKeyError:
            Type = False

        try:
            Dec = request.POST["Des"]
        except MultiValueDictKeyError:
            Dec = False

        attrprod = AttrProduct.objects.get(id = id)
        pro = Product.objects.get(ID = attrprod.FK_Product.ID)
        shop = Shop.objects.get(ID = pro.FK_Shop.ID)
        profile = Profile.objects.get(FK_User = shop.FK_ShopManager)

        if Type == '1':

            attrprod.Available = True
            attrprod.save()
            alert = Alert.objects.get(Slug = id, Part ='11', Seen = False)
            alert.Seen = True
            alert.Status = True
            alert.Description = Dec
            alert.FK_Staff = request.user
            alert.save()

            if Dec != False:
                SendAlertResponse('ثبت-ویژگی-جدید-برای-محصول', Dec, profile.MobileNumber)
                # Send Push notification
                title = 'ثبت ویژگی جدید محصول'
                description = 'ویژگی جدید برای محصول با شناسه ' + pro.Slug + 'تایید شد.'
                # send_push_notification().run(title, description, profile.MobileNumber)
        else:
            if Dec != False:
                SendAlertResponse('عدم-ثبت-ویژگی-جدید-برای-محصول', Dec, profile.MobileNumber)
                # Send Push notification
                title = 'عدم ثبت ویژگی جدید محصول'
                description = 'ویژگی جدید برای محصول با شناسه ' + pro.Slug + 'تایید نشد.'
                # send_push_notification().run(title, description, profile.MobileNumber)

                # Set Info 
                Des = Dec + '|' + str(attrprod.FK_Product.Title) + '|' + str(attrprod.FK_Attribute.Title) + '|' + str(attrprod.FK_Attribute.Unit) + '|' + str(attrprod.Value)

                alert = Alert.objects.get(Slug = id, Part ='11', Seen = False)
                alert.Seen = True
                alert.Status = False
                alert.Description = Des
                alert.FK_Staff = request.user
                alert.save()
                attrprod.delete()      
        
        return redirect("nakhll_market:Alert")


# Record Attribute Alert
@login_required
@staff_member_required
def RecordAttributeAlert(request, id):
    if request.method == 'POST':
        try:
            Type = request.POST["accept-btn"]
        except MultiValueDictKeyError:
            Type = False
        try:
            Dec = request.POST["Des"]
        except MultiValueDictKeyError:
            Dec = False

        attr = get_object_or_404(Attribute, id = id)
        if Type == '1':
            if Dec != False:
                attr.Publish = True
                attr.FK_User = request.user
                attr.save()
                alert = get_object_or_404(Alert, Slug = id, Part ='10', Seen = False)
                alert.Seen = True
                alert.Status = True
                alert.Description = Dec
                alert.FK_Staff = request.user
                alert.save()
                # SendAlertResponse('ایجاد-ویژگی-جدید', Dec, profile.MobileNumber)  
        else:
            if Dec != False:
                # Set Info 
                Des = Dec + '|' + str(attr.Title) + '|' + str(attr.Unit)
                alert = get_object_or_404(Alert, Slug = id, Part ='10', Seen = False)
                alert.Seen = True
                alert.Status = False
                alert.Description = Des
                alert.FK_Staff = request.user
                alert.save()
                attr.delete()
                # SendAlertResponse('ایجاد-ویژگی-جدید', Dec, profile.MobileNumber) 
        return redirect("nakhll_market:Alert")


# Record Product Banner Alert
@login_required
@staff_member_required
def RecordProducBannertAlert(request, id):
    if request.method == 'POST':
        try:
            Type = request.POST["accept-btn"]
        except MultiValueDictKeyError:
            Type = False

        try:
            Dec = request.POST["Des"]
        except MultiValueDictKeyError:
            Dec = False

        banner = ProductBanner.objects.get(id = id)
        pro = Product.objects.get(ID = banner.FK_Product.ID)
        shop = Shop.objects.get(ID = pro.FK_Shop.ID)
        profile = Profile.objects.get(FK_User = shop.FK_ShopManager)

        if Type == '1':

            banner.Publish = True
            banner.FK_User = request.user
            banner.save()
            alert = Alert.objects.get(Slug = id, Part ='8', Seen = False)
            alert.Seen = True
            alert.Status = True
            alert.Description = Dec
            alert.FK_Staff = request.user
            alert.save()

            if Dec != False:
                SendAlertResponse('ایجاد-بنر-محصول', Dec, profile.MobileNumber)
                # Send Push notification
                title = 'ایجاد بنر محصول جدید'
                description = 'بنر جدید برای محصول با شناسه ' + pro.Slug + 'ایجاد شد.'
                # send_push_notification().run(title, description, profile.MobileNumber)
        else:
            if Dec != False:
                SendAlertResponse('عدم-ایجاد-بنر-محصول', Dec, profile.MobileNumber)
                # Send Push notification
                title = 'عدم ایجاد بنر محصول جدید'
                description = 'بنر جدید برای محصول با شناسه ' + pro.Slug + 'ایجاد نشد.'
                # send_push_notification().run(title, description, profile.MobileNumber)

                # Set Info 
                Des = Dec + '|' + str(banner.Title) + '|' + str(banner.Description) + '|' + str(banner.URL) + '|' + str(banner.BannerBuilder) + '|' + str(banner.BannerURL) + '|' + str(banner.Image) 

                alert = Alert.objects.get(Slug = id, Part ='8', Seen = False)
                alert.Seen = True
                alert.Status = False
                alert.Description = Des
                alert.FK_Staff = request.user
                alert.save()
                banner.delete()     
        
        return redirect("nakhll_market:Alert")


# Record Product Alert
@login_required
@staff_member_required
def RecordProductAlert(request, id):
    if request.method == 'POST':
        # get data
        try:
            Type = request.POST["accept-btn"]
        except MultiValueDictKeyError:
            Type = False
        try:
            Dec = request.POST["Des"]
        except MultiValueDictKeyError:
            Dec = False
        # get object
        pro = get_object_or_404(Product, ID = id)
        shop = get_object_or_404(Shop, ID = pro.FK_Shop.ID)
        profile = get_object_or_404(Profile, FK_User = shop.FK_ShopManager)

        if Type == '1':
            pro.Publish = True
            pro.FK_User = request.user
            pro.save()
            alert = get_object_or_404(Alert, Slug = id, Part ='6', Seen = False)
            alert.Seen = True
            alert.Status = True
            alert.Description = Dec
            alert.FK_Staff = request.user
            alert.save()

            if Dec != False:
                SendAlertResponse('ایجاد-محصول-جدید', Dec, profile.MobileNumber)
                # Send Push notification
                title = 'ایجاد محصول جدید'
                description = 'محصول جدیدی با شناسه ' + pro.Slug + 'ایجاد شد.'
                # send_push_notification().run(title, description, profile.MobileNumber)
        else:
            if Dec != False:
                SendAlertResponse('عدم-ایجاد-محصول-جدید', Dec, profile.MobileNumber)
                # Send Push notification
                title = 'عدم ایجاد محصول جدید'
                description = 'محصول جدیدی با شناسه ' + pro.Slug + 'تایید نشد.'
                # send_push_notification().run(title, description, profile.MobileNumber)

                alert = get_object_or_404(Alert, Slug = id, Part ='6', Seen = False)
                alert.Seen = True
                alert.Status = False
                alert.Description = Dec
                alert.FK_Staff = request.user
                alert.save()
                pro.Publish = False
                pro.FK_User = request.user
                pro.save()

        return redirect("nakhll_market:Alert")




# Edite Shop Alert
@login_required
@staff_member_required
def EditeNationalCardImageAlert(request, user_id):
    
    # Get User Info
    this_profile = Profile.objects.get(FK_User=request.user)
    this_inverntory = request.user.WalletManager.Inverntory
    # Get Menu Item
    options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
    # Get Nav Bar Menu Item
    navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
    # --------------------------------------------------------------------
    user = User.objects.get(id=user_id)
    profile = user.User_Profile
    alert = Alert.objects.get(Part='1', Slug=user.id, Seen=False)
    title = 'ویرایش تصویر کارت ملی'

    if request.method == 'POST':
        Type = request.POST.get("accept-btn", None)
        Dec = request.POST.get("Des", None)
        alert.Seen = True
        alert.Description = Dec
        alert.FK_Staff = request.user

        if Type == '1': # Accept incomming changes
            alert.Status = True
            profile.ImageNationalCard = profile.ImageNationalCardUnverified 
            description = 'تصویر کارت ملی شما تایید شد!'
            SendAlertResponse(title, Dec, profile.MobileNumber)
            # send_push_notification().run(title, description, profile.MobileNumber)
        else: # Deny changes
            profile.ImageNationalCardUnverified = None
            alert.Status = False
            description = f'تصویر کارت ملی شما تایید نشد! {Dec}'
            SendAlertResponse(title, Dec, profile.MobileNumber)
            # send_push_notification().run(title, description, profile.MobileNumber)
        # Save changes
        profile.save()
        alert.save()
        return redirect("nakhll_market:Alert")

    context = {
        'This_User_Profile':this_profile,
        'This_User_Inverntory': this_inverntory,
        'Options': options,
        'MenuList':navbar,
        'Alert': alert,
        'image': user.User_Profile.ImageNationalCardUnverified,
    }
    
    return render(request, 'nakhll_market/alert/pages/editenationalcardimage.html', context)

# Factor Alert
@login_required
@staff_member_required
def PostTrackingCodeAlert(request, id):
    # Get User Info
    this_profile = Profile.objects.get(FK_User=request.user)
    this_inverntory = request.user.WalletManager.Inverntory
    # Get Menu Item
    options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
    # Get Nav Bar Menu Item
    navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
    # -------------------------------------------------------------------
    # get PostTracking with barcode
    alert = Alert.objects.get(id=id)
    tracking = PostTrackingCode.objects.filter(barcode=alert.Slug).first()
    if tracking:
        slug = tracking.factor_post.Factor_Products.all()[0].id 
    else:
        slug = alert.Slug
    factor = get_object_or_404(Factor, ID=slug)
    # TODO: Many issue in this part related to business logic
    user_profile = factor.FK_User.User_Profile
    shop_profile = factor.FK_FactorPost.all()[0].FK_Product.FK_Shop.FK_ShopManager.User_Profile
    title = 'ارسال-محصول'
    post_tracking = PostTrackingCode.objects.filter(factor_post__Factor_Products__ID=slug).first()
    if request.method == 'GET':
        products = FactorPost.objects.filter(barcodes__barcode=post_tracking.barcode)
        context = {
            'This_User_Profile':this_profile,
            'This_User_Inverntory': this_inverntory,
            'Options': options,
            'MenuList':navbar,
            'post_tracking': post_tracking,
            'products': products,
        }
            
        return render(request, 'nakhll_market/alert/pages/posttracking.html', context)
    else:
        Type = request.POST.get("accept-btn", None)
        Dec = request.POST.get("Des", None)
        alert.Seen = True
        Dec = f'فاکتور {factor.FactorNumber}: {Dec}'
        alert.Description = Dec
        alert.FK_Staff = request.user
        if Type == '1': # Accept incomming changes
            alert.Status = True
            user_message = f'محصول خریداری شده شما با کد رهگیری {post_tracking.barcode} ارسال شد'
            SendAlertResponse(title, Dec, shop_profile.MobileNumber)
            SendAlertResponse(title, user_message, user_profile.MobileNumber)
        else: # Deny changes
            shop_profile_message = f'بارکد ثبت شده برای فاکتور {factor.FactorNumber} مورد تایید نیست. توضیحات: {Dec}'
            alert.Status = False
            SendAlertResponse(title, shop_profile_message, shop_profile.MobileNumber)
        # Save changes
        alert.save()
        return redirect("nakhll_market:Alert")

       

