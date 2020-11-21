from django.shortcuts import render_to_response
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator
from django.urls import reverse
from django.views import generic
from ipware import get_client_ip
from datetime import datetime
from django.db.models import Q
import jdatetime
from django.contrib import messages
import datetime
from django.utils.datastructures import MultiValueDictKeyError
from django.http import JsonResponse
from jdatetime import date as jdate
from datetime import date
from kavenegar import *
import threading
import jdatetime
import requests

from django.contrib.auth.decorators import login_required
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
from .models import Message, User_Message_Status
from .models import Option_Meta
from .models import Newsletters 
from .models import Alert
from .models import Field
from .models import OptinalAttribute

from Payment.models import Wallet, Transaction, Factor, FactorPost, Coupon, Campaign

from Ticketing.models import Ticketing, TicketingMessage, Complaint

from .forms import Login, CheckEmail


# Profile Page And Sub Pages
#---------------------------------------------------------------------------------------------------------------------------------

# Send Pushnotification
class SendPushnotif(threading.Thread):
    def run(self, title, description, user_id):
        try:
            TOKEN = '70c66e5fcb993ac51a432617941d5694c03c4943'

            # Get User Mobile Number
            mobile_number = Profile.objects.get(FK_User_id = user_id).MobileNumber

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
                    'phone_number': [mobile_number,]
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

# Send Alert SMS
class SendMessage(threading.Thread):

    def __init__(self, user_id):
        self.user = User.objects.get(id = user_id)
        
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

        # User Message Count
        msg_count = self.CheckUserMessage()
        # Get User Phone Number
        PhoneNumber = Profile.objects.get(FK_User = self.user).MobileNumber
        # Send SMS
        url = 'https://api.kavenegar.com/v1/4E41676D4B514A4143744C354E6135314E4F47686B33594B747938794D30426A784A692F3579596F3767773D/verify/lookup.json' 
        params = {'receptor': PhoneNumber, 'token' : msg_count, 'template' : 'nakhll-message'}
        requests.post(url, params = params)



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

# ---------------------------------------------------- User Profile Pages ---------------------------------------------------------


# Get User Dashbord Info
def ProfileDashbord(request):
    # Check User Status
    if request.user.is_authenticated :
        # Get User Info
        This_User_Info = GetUserInfo().run(request)
        this_profile = This_User_Info["user_profiel"]
        this_inverntory = This_User_Info["user_inverntory"]
        # Get Menu Item
        options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
        # Get Nav Bar Menu Item
        navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
        # -------------------------------------------------------------------

        context = {
            'This_User_Profile':this_profile,
            'This_User_Inverntory': this_inverntory,
            'Options': options,
            'MenuList':navbar,
        }

        return render(request, 'nakhll_market/profile/pages/profile.html', context)

    else:
        
        return redirect("nakhll_market:AccountLogin")

# Get User Wallet Info And Charge It
def ProfileWallet(request):
    # Check User Status
    if request.user.is_authenticated:
        # Get User Info
        This_User_Info = GetUserInfo().run(request)
        this_profile = This_User_Info["user_profiel"]
        this_inverntory = This_User_Info["user_inverntory"]
        # Get Menu Item
        options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
        # Get Nav Bar Menu Item
        navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
        # -------------------------------------------------------------------

        context = {
            'This_User_Profile':this_profile,
            'This_User_Inverntory': this_inverntory,
            'Options': options,
            'MenuList':navbar,
            'Message':None,
        }

        return render(request, 'nakhll_market/profile/pages/wallet.html', context)

    else:
        
        return redirect("nakhll_market:AccountLogin")

# Get User Message
def ProfileMessage(request, status = None, start = None, end = None):
    # Check User Status
    if request.user.is_authenticated :
        # Get User Info
        This_User_Info = GetUserInfo().run(request)
        this_profile = This_User_Info["user_profiel"]
        this_inverntory = This_User_Info["user_inverntory"]
        # Get Menu Item
        options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
        # Get Nav Bar Menu Item
        navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
        # ------------------------------------------------------------------
        # Get All Message
        User_Message_List = []
        # Build Message Class
        class MessageClass:
            def __init__(self, item, status):
                self.Message = item
                self.Status = status
        
        if (status == None) and (start == None) and (end == None):
            # Search In All Message
            messages = Message.objects.filter(Type = True)
            for msg_item in messages:
                for item in msg_item.FK_Users.all():
                    if item.FK_User == request.user:
                        new = MessageClass(msg_item, item.SeenStatus)
                        User_Message_List.append(new)

        elif (start != '') and (end != ''):
            messages = Message.objects.filter(Type = True, Date__range = [start, end])
            for msg_item in messages:
                for item in msg_item.FK_Users.all():
                    if item.FK_User == request.user:
                        if status == '1':
                            if item.SeenStatus == False:
                                new = MessageClass(msg_item, item.SeenStatus)
                                User_Message_List.append(new)
                        elif status == '2':
                            if item.SeenStatus == True:
                                new = MessageClass(msg_item, item.SeenStatus)
                                User_Message_List.append(new)
                        else:
                            new = MessageClass(msg_item, item.SeenStatus)
                            User_Message_List.append(new)

        # Get Message Create Date
        def GetDate(item):
            return item.Message.Date

        User_Message_List.sort(reverse = True, key = GetDate)

        context = {
            'This_User_Profile':this_profile,
            'This_User_Inverntory': this_inverntory,
            'Options': options,
            'MenuList':navbar,
            'Messages':User_Message_List,
            'Status':'0',
        }

        return render(request, 'nakhll_market/profile/pages/message.html', context)
    else:
        return redirect("nakhll_market:AccountLogin")

  
# Get User Factors Info
def ProfileFactor(request):
    # Check User Status
    if request.user.is_authenticated :
        # Get User Info
        This_User_Info = GetUserInfo().run(request)
        this_profile = This_User_Info["user_profiel"]
        this_inverntory = This_User_Info["user_inverntory"]
        # Get Menu Item
        options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
        # Get Nav Bar Menu Item
        navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
        # --------------------------------------------------------------------
        # Get All User Factor
        this_user_factors = Factor.objects.filter(FK_User = request.user, PaymentStatus = True).order_by('-OrderDate')
        # Factor List
        factor_items_wait = []
        factor_items_ready = []
        factor_items_send = []
        factor_items_cansel = []
        for item in Factor.objects.filter(PaymentStatus = True, Publish = True, Checkout = False).order_by('-OrderDate'):
            # Get Factor When Factor Post Is Status == 1
            if item.get_wait_user_factor(request):
                factor_items_wait.append(item)
                continue
            elif item.get_inpreparation_factor(request):
                # Get Factor When Factor Post Is Status == 2
                factor_items_ready.append(item)
                continue
            elif item.get_send_user_factor(request):
                # Get Factor When Factor Post Is Status == 3
                factor_items_send.append(item)
                continue
            elif item.get_cancel_factor(request):
                # Get Factor When Factor Post Is Status == 4
                factor_items_cansel.append(item)
                continue

        context = {
            'This_User_Profile':this_profile,
            'This_User_Inverntory': this_inverntory,
            'Options': options,
            'MenuList':navbar,
            'This_User_Factor':this_user_factors,
            'ShopFactors':factor_items_wait,
            'ShopRedyFactors':factor_items_ready,
            'ShopSendFactors':factor_items_send,
            'ShopCanselFactors':factor_items_cansel,
        }
     
        return render(request, 'nakhll_market/profile/pages/factor.html', context)
    else: 
        return redirect("nakhll_market:AccountLogin")



# Get User Transactiones
def ProfileTransactione(request):
    # Check User Status
    if request.user.is_authenticated :
        # Get User Info
        This_User_Info = GetUserInfo().run(request)
        this_profile = This_User_Info["user_profiel"]
        this_inverntory = This_User_Info["user_inverntory"]
        # Get Menu Item
        options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
        # Get Nav Bar Menu Item
        navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
        # -------------------------------------------------------------------
        # Get All User Transaction
        transaction = Transaction.objects.filter(FK_User = request.user).order_by('-Date')

        context = {
            'This_User_Profile':this_profile,
            'This_User_Inverntory': this_inverntory,
            'Options': options,
            'MenuList':navbar,
            'Transactions':transaction,
        }
     
        return render(request, 'nakhll_market/profile/pages/transaction.html', context)
    else:
        return redirect("nakhll_market:AccountLogin")



# Get User Reviews
def ProfileReview(request):
   # Check User Status
    if request.user.is_authenticated :
        # Get User Info
        This_User_Info = GetUserInfo().run(request)
        this_profile = This_User_Info["user_profiel"]
        this_inverntory = This_User_Info["user_inverntory"]
        # Get Menu Item
        options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
        # Get Nav Bar Menu Item
        navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
        # --------------------------------------------------------------------
        # Build Class
        class Comments:
            def __init__(self, this_type, this_text, this_content, likecount, datecreate, status):
                self.type = this_type
                self.text = this_text
                self.content = this_content
                self.like = likecount
                self.date = datecreate
                self.status = status
        # Get All User Comments
        user_comments = []
        for item in Comment.objects.filter(FK_UserAdder = request.user).order_by('-DateCreate'):
            new_item = Comments(item.get_type, item.Description, item.get_object_name, item.get_like_count, item.DateCreate, item.get_status)
            user_comments.append(new_item)
        for item in ShopComment.objects.filter(FK_UserAdder = request.user).order_by('-DateCreate'):
            new_item = Comments(item.get_type, item.Description, item.get_object_name, item.get_like_count, item.DateCreate, item.get_status)
            user_comments.append(new_item)

        # Get Product Create Date
        def GetDate(item):
            return item.date
        
        user_comments.sort(reverse = True, key = GetDate)

        context = {
            'This_User_Profile':this_profile,
            'This_User_Inverntory': this_inverntory,
            'Options': options,
            'MenuList':navbar,
            'Comments':user_comments,
        }
     
        return render(request, 'nakhll_market/profile/pages/review.html', context)
    else:
        return redirect("nakhll_market:AccountLogin")


    
# Get User Shops
def ProfileShops(request):
    # Check User Status
    if request.user.is_authenticated :
        # Get User Info
        This_User_Info = GetUserInfo().run(request)
        this_profile = This_User_Info["user_profiel"]
        this_inverntory = This_User_Info["user_inverntory"]
        # Get Menu Item
        options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
        # Get Nav Bar Menu Item
        navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
        # --------------------------------------------------------------------
        # Get All User`s Shops
        user_shop_list = []
        class Shop_item:
            def __init__(self, item, item_market, item_submarket):
                self.Shop = item
                self.Market = item_market
                self.SubMarket = item_submarket
        # Get All Shops
        for item in this_profile.get_user_shops():
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
            user_shop_list.append(Shop_item(item, this_shop_market, this_shop_subMarket))
        # Get All User Products
        user_product_list = this_profile.get_user_products

        context = {
            'This_User_Profile':this_profile,
            'This_User_Inverntory': this_inverntory,
            'Options': options,
            'MenuList':navbar,
            'UserShops':user_shop_list,
            'UserProducts':user_product_list,
        }
        return render(request, 'nakhll_market/profile/pages/shops.html', context)
    else:
        return redirect("nakhll_market:AccountLogin")

# ----------------------------------------------------- End User Profile Pages ----------------------------------------------------------



# -----------------------------------------------------------------------------------------------------------------------------------------


# New Message
def AddNewMessage(request, msg = None):
    # Check User Status
    if request.user.is_authenticated:
        if request.method == 'POST' :
            try:
                Message_Title = request.POST["msg_title"]
            except:
                Message_Title = None
            try:
                Message_Des = request.POST["msg_des"]
            except:
                Message_Des = None

            Message_User = request.POST.getlist("msg_user")

            if ((Message_Title != None) and (Message_Title != '')) and ((Message_Des != None) and (Message_Des != '')):
                if len(Message_User) != 0:
                    new_message =  Message.objects.create(Title = Message_Title, Text = Message_Des, FK_Sender = request.user)
                    for item in Message_User:
                        new = User_Message_Status.objects.create(FK_User = User.objects.get(id = item))
                        new_message.FK_Users.add(new)
                    for item in new_message.FK_Users.all():
                        SendMessage(item.FK_User.id).run()
                        # Send Push notification
                        title = 'پیغام جدید'
                        description = new_message.Title + '...'
                        SendPushnotif().run(title, description, item.FK_User.id)
                else:
                    new_message =  Message.objects.create(Title = Message_Title, Text = Message_Des, FK_Sender = request.user)
                    for item in Profile.objects.all():
                        new = User_Message_Status.objects.create(FK_User = item.FK_User)
                        new_message.FK_Users.add(new)
                return redirect('nakhll_market:Re_AddNewMessage',
                msg = 'پیام شما ثبت شد...')
            else:  
                return redirect('nakhll_market:Re_AddNewMessage',
                msg = 'عنوان و متن پیام نمی تواند خالی باشد!')
        else:
            # Get User Info
            This_User_Info = GetUserInfo().run(request)
            this_profile = This_User_Info["user_profiel"]
            this_inverntory = This_User_Info["user_inverntory"]
            # Get Menu Item
            options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
            # Get Nav Bar Menu Item
            navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
            # -------------------------------------------------------------------
            # get all active user
            user_list = User.objects.filter(is_active = True)

            if msg != None:
                show = True
                message = msg
            else:
                show = False
                message = None

            context = {
                'This_User_Profile':this_profile,
                'This_User_Inverntory': this_inverntory,
                'Options': options,
                'MenuList':navbar,
                'User':user_list,
                'ShowAlart':show,
                'AlartMessage':message,
            }

            return render(request, 'nakhll_market/profile/pages/newmessage.html', context)
    else:
        return redirect("nakhll_market:AccountLogin")


# Send Push
def SendPush(request):
    SendPushnotif().run()
    return redirect('nakhll_market:AddNewMessage')
    



# Show Invate Page
def ShowInvatePage(request):
    # Check User Status
    if request.user.is_authenticated :
        # Get User Info
        user = User.objects.all()
        # Get User Profile
        profile = Profile.objects.all()
        # Get Wallet Inverntory
        wallets = Wallet.objects.all()
        # Get Menu Item
        options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
        # Get Nav Bar Menu Item
        navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
        # ------------------------------------------------------------------

        context = {
            'Users':user,
            'Profile':profile,
            'Wallet': wallets,
            'Options': options,
            'MenuList':navbar,
        }

        return render(request, 'nakhll_market/profile/pages/invitation.html', context)

    else:
        
        return redirect("nakhll_market:AccountLogin")






# -----------------------------------------------------------------------------------------------------------------------------------------
   

# Add And Show User`s Shop And Peoduct
#--------------------------------------------------------------------------------------------------------------------------------

# Add User Bank Account Info In Shop-Manage
def add_user_bank_account_info(request):
    # Check User Status
    if request.user.is_authenticated :
        if request.method == 'POST': 
            try :
                # get data
                try:
                    CreditCardNumber = request.POST["Shop_CreditCardNumber"]
                except:
                    CreditCardNumber = None

                try:
                    ShabaBankNumber = request.POST["Shop_ShabaBankNumber"]
                except:
                    ShabaBankNumber = None

                try:
                    AccountOwner = request.POST["Shop_AccountOwner"]
                except:
                    AccountOwner = None
                # check data
                if ((CreditCardNumber != None) and (CreditCardNumber != '')) and ((ShabaBankNumber != None) and (ShabaBankNumber != '')) and ((AccountOwner != None) and (AccountOwner != '')):
                    BankAccount.objects.create(FK_Profile = Profile.objects.get(FK_User = request.user), CreditCardNumber = CreditCardNumber, ShabaBankNumber = ShabaBankNumber, AccountOwner = AccountOwner)
                    return redirect("nakhll_market:UserShops")
                else:
                    return redirect("nakhll_market:UserShops")
            except Exception as e:
                return redirect("nakhll_market:error_500", error_text = str(e))
    else:    
        return redirect("nakhll_market:AccountLogin")




# Add New Shop In Shop-Manage
def add_new_shop(request):
    # Check User Status
    if request.user.is_authenticated:
        if request.method == 'POST':
            # Get Data
            Title = request.POST["Shop_Title"]
            Slug = request.POST["Shop_Slug"]
            Description = request.POST["Shop_Des"]
            State = request.POST["Shop_State"]
            BigCity = request.POST["Shop_BigCity"]
            City = request.POST["Shop_City"]
            SubMarkets = request.POST.getlist("Shop_SubMarket")
            try:
                Bio = request.POST["Shop_Bio"]
            except:
                Bio = False

            try:
                Saturday = request.POST["SATCheck"]
            except:
                Saturday = False

            try:
                Sunday = request.POST["SUNCheck"]
            except:
                Sunday = False

            try:
                Monday = request.POST["MONCheck"]
            except:
                Monday = False

            try:
                Tuesday = request.POST["TUECheck"]
            except:
                Tuesday = False

            try:
                Wednesday = request.POST["WEDCheck"]
            except:
                Wednesday = False

            try:
                Thursday = request.POST["THUCheck"]
            except:
                Thursday = False

            try:
                Friday = request.POST["FRICheck"]
            except:
                Friday = False

            try:
                Image = request.FILES["Shop_Image"]
            except MultiValueDictKeyError:
                Image = ''

            # Set Data
            try:
                holidays = ''
                # Check Day
                if Saturday != False:
                    if holidays != '':
                        holidays += '-'
                    holidays += '0'
                if Sunday != False:
                    if holidays != '':
                        holidays += '-'
                    holidays += '1'
                if Monday != False:
                    if holidays != '':
                        holidays += '-'
                    holidays += '2'
                if Tuesday != False:
                    if holidays != '':
                        holidays += '-'
                    holidays += '3'
                if Wednesday != False:
                    if holidays != '':
                        holidays += '-'
                    holidays += '4'
                if Thursday != False:
                    if holidays != '':
                        holidays += '-'
                    holidays += '5'
                if Friday != False:
                    if holidays != '':
                        holidays += '-'
                    holidays += '6'
                # Add New Record
                this_shop = Shop.objects.create(FK_ShopManager = request.user, Title = Title, Slug = Slug, Description = Description, Bio = Bio, State = State, BigCity = BigCity, City = City)
                if holidays != '':
                    this_shop.Holidays = holidays
                if Image != '':
                    this_shop.Image = Image
                for item in SubMarkets:
                    this_shop.FK_SubMarket.add(SubMarket.objects.get(ID = item))
                this_shop.save()

                Alert.objects.create(Part = '2', FK_User = request.user, Slug = this_shop.ID)
                # -----------------------------------------------------------------------------
                # Get User Info
                This_User_Info = GetUserInfo().run(request)
                this_profile = This_User_Info["user_profiel"]
                this_inverntory = This_User_Info["user_inverntory"]
                # Get Menu Item
                options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
                # Get Nav Bar Menu Item
                navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
                # -------------------------------------------------------------------
                # Get All Submarkets
                submarkets = SubMarket.objects.filter(Publish = True)

                context = {
                    'This_User_Profile':this_profile,
                    'This_User_Inverntory': this_inverntory,
                    'Options': options,
                    'MenuList':navbar,
                    'Submarkets':submarkets,
                    'ShowAlart':True,
                    'AlartMessage':'حجره "' + this_shop.Title + '" ثبت شد، و پس از تایید کارشناسان سایت منتشر می شود.',
                }

                return render(request, 'nakhll_market/profile/pages/newshop.html', context)
            except Exception as e:
                # Get User Info
                This_User_Info = GetUserInfo().run(request)
                this_profile = This_User_Info["user_profiel"]
                this_inverntory = This_User_Info["user_inverntory"]
                # Get Menu Item
                options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
                # Get Nav Bar Menu Item
                navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
                # -------------------------------------------------------------------
                # Get All Submarkets
                submarkets = SubMarket.objects.filter(Publish = True)

                context = {
                    'This_User_Profile':this_profile,
                    'This_User_Inverntory': this_inverntory,
                    'Options': options,
                    'MenuList':navbar,
                    'Submarkets':submarkets,
                    'ShowAlart':True,
                    'AlartMessage':str(e),
                }

                return render(request, 'nakhll_market/profile/pages/newshop.html', context)
        else:
            # Get User Info
            This_User_Info = GetUserInfo().run(request)
            this_profile = This_User_Info["user_profiel"]
            this_inverntory = This_User_Info["user_inverntory"]
            # Get Menu Item
            options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
            # Get Nav Bar Menu Item
            navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
            # -------------------------------------------------------------------
            # Get All Submarkets
            submarkets = SubMarket.objects.filter(Publish = True)

            context = {
                'This_User_Profile':this_profile,
                'This_User_Inverntory': this_inverntory,
                'Options': options,
                'MenuList':navbar,
                'Submarkets':submarkets,
            }

            return render(request, 'nakhll_market/profile/pages/newshop.html', context)
    else:    
        return redirect("nakhll_market:AccountLogin")




# Edit Shop In Shop-Manage
def edit_shop_info(request, shop_slug):
    # Check User Status
    if request.user.is_authenticated :
        if request.method == 'POST':
            # Get Data
            Title = request.POST["Shop_Title"]
            Description = request.POST["Shop_Des"]
            State = request.POST["Shop_State"]
            BigCity = request.POST["Shop_BigCity"]
            City = request.POST["Shop_City"]
            SubMarkets = request.POST.getlist("Shop_SubMarket")

            try:
                Bio = request.POST["Shop_Bio"]
            except:
                Bio = ''

            try:
                Saturday = request.POST["SATCheck"]
            except:
                Saturday = False

            try:
                Sunday = request.POST["SUNCheck"]
            except:
                Sunday = False

            try:
                Monday = request.POST["MONCheck"]
            except:
                Monday = False

            try:
                Tuesday = request.POST["TUECheck"]
            except:
                Tuesday = False

            try:
                Wednesday = request.POST["WEDCheck"]
            except:
                Wednesday = False

            try:
                Thursday = request.POST["THUCheck"]
            except:
                Thursday = False

            try:
                Friday = request.POST["FRICheck"]
            except:
                Friday = False

            try:
                Image = request.FILES["Shop_Image"]
            except MultiValueDictKeyError:
                Image = ''
            # Get This Shop
            this_shop = get_object_or_404(Shop, ID = id)
            # Set Data
            try:
                holidays = ''
                # Check Day
                if Saturday != False:
                    if holidays != '':
                        holidays += '-'
                    holidays += '0'
                if Sunday != False:
                    if holidays != '':
                        holidays += '-'
                    holidays += '1'
                if Monday != False:
                    if holidays != '':
                        holidays += '-'
                    holidays += '2'
                if Tuesday != False:
                    if holidays != '':
                        holidays += '-'
                    holidays += '3'
                if Wednesday != False:
                    if holidays != '':
                        holidays += '-'
                    holidays += '4'
                if Thursday != False:
                    if holidays != '':
                        holidays += '-'
                    holidays += '5'
                if Friday != False:
                    if holidays != '':
                        holidays += '-'
                    holidays += '6'
                # Shop Edit Alert
                global edit_shop_alert
                if not Alert.objects.filter(Part = '3', Slug = this_shop.ID, Seen = False).exists():
                    edit_shop_alert = Alert.objects.create(FK_User = request.user, Part = '3', Slug = this_shop.ID)
                else:
                    edit_shop_alert = Alert.objects.get(Part = '3', Slug = this_shop.ID, Seen = False)
                    edit_shop_alert.FK_Field.all().delete()
                # Check Change Dtat
                if SubMarkets:
                    new_shop_submarket_list = ''
                    for item in SubMarkets:
                        new_shop_submarket_list += item + '~' 
                    shop_submarket_field = Field.objects.create(Title = 'SubMarket', Value = new_shop_submarket_list)
                    edit_shop_alert.FK_Field.add(shop_submarket_field)
                
                if Image != '':
                    this_shop.NewImage = Image
                    this_shop.save()
                    new_image_string = 'NewImage' + '#' + str(this_shop.NewImage)
                    shop_image_field = Field.objects.create(Title = 'Image', Value = new_image_string)
                    edit_shop_alert.FK_Field.add(shop_image_field)
                    
                if Title != this_shop.Title:
                    shop_title_field = Field(Title = 'Title', Value = Title)
                    edit_shop_alert.FK_Field.add(shop_title_field)

                if Description != this_shop.Description:
                    shop_description_field = Field(Title = 'Description', Value = Description)
                    edit_shop_alert.FK_Field.add(shop_description_field)

                if Bio != this_shop.Bio:
                    shop_bio_field = Field(Title = 'Bio', Value = Bio)
                    edit_shop_alert.FK_Field.add(shop_bio_field)

                if State != this_shop.State:
                    shop_state_field = Field.objects.create(Title = 'State', Value = State)
                    edit_shop_alert.FK_Field.add(shop_state_field)

                if BigCity != this_shop.BigCity:
                    shop_bigcity_field = Field.objects.create(Title = 'BigCity', Value = BigCity)
                    edit_shop_alert.FK_Field.add(shop_bigcity_field)

                if City != this_shop.City:
                    shop_city_field = Field.objects.create(Title = 'City', Value = City)
                    edit_shop_alert.FK_Field.add(shop_city_field)

                if holidays != this_shop.Holidays:
                    shop_holidays_field = Field.objects.create(Title = 'Holidays', Value = holidays)
                    edit_shop_alert.FK_Field.add(shop_holidays_field)
                    
                if edit_shop_alert.FK_Field.all().count() != 0:
                    # Get User Info
                    This_User_Info = GetUserInfo().run(request)
                    this_profile = This_User_Info["user_profiel"]
                    this_inverntory = This_User_Info["user_inverntory"]
                    # Get Menu Item
                    options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
                    # Get Nav Bar Menu Item
                    navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
                    # --------------------------------------------------------------------
                    # Get This Shop
                    this_shop = get_object_or_404(Shop, Slug = shop_slug)
                    # Build Class
                    class submarket:
                        def __init__(self, item, status):
                            self.SubMarket = item
                            self.Status = status
                    # Submarket List
                    this_shop_submarket_list = []
                    this_shop_submarket = []
                    # Get Shop Submarkets
                    for item in this_shop.FK_SubMarket.all():
                        this_shop_submarket.append(item)
                    # Select Submarket
                    for item in SubMarket.objects.filter(Publish = True):
                        if item in this_shop_submarket:
                            new_object = submarket(item, True)
                        else:
                            new_object = submarket(item, False)
                        this_shop_submarket_list.append(new_object)

                    context = {
                        'This_User_Profile':this_profile,
                        'This_User_Inverntory': this_inverntory,
                        'Options': options,
                        'MenuList':navbar,
                        'UserShop':this_shop,
                        'Submarkets':this_shop_submarket_list,
                        'ShowAlart':True,
                        'AlartMessage':'اطلاعات حجره "' + this_shop.Title +'" تغییر پیدا کرده است، و پس از تایید کارشناسان اعمال می شود.',
                    }

                    return render(request, 'nakhll_market/profile/pages/shopdetails.html', context)
                else:
                    edit_shop_alert.delete()
                    return redirect("nakhll_market:UserShops")   
            except Exception as e:
                # Get User Info
                This_User_Info = GetUserInfo().run(request)
                this_profile = This_User_Info["user_profiel"]
                this_inverntory = This_User_Info["user_inverntory"]
                # Get Menu Item
                options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
                # Get Nav Bar Menu Item
                navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
                # --------------------------------------------------------------------
                # Get This Shop
                this_shop = get_object_or_404(Shop, Slug = shop_slug)
                # Build Class
                class submarket:
                    def __init__(self, item, status):
                        self.SubMarket = item
                        self.Status = status
                # Submarket List
                this_shop_submarket_list = []
                this_shop_submarket = []
                # Get Shop Submarkets
                for item in this_shop.FK_SubMarket.all():
                    this_shop_submarket.append(item)
                # Select Submarket
                for item in SubMarket.objects.filter(Publish = True):
                    if item in this_shop_submarket:
                        new_object = submarket(item, True)
                    else:
                        new_object = submarket(item, False)
                    this_shop_submarket_list.append(new_object)

                context = {
                    'This_User_Profile':this_profile,
                    'This_User_Inverntory': this_inverntory,
                    'Options': options,
                    'MenuList':navbar,
                    'UserShop':this_shop,
                    'Submarkets':this_shop_submarket_list,
                    'ShowAlart':True,
                    'AlartMessage':str(e),
                }

                return render(request, 'nakhll_market/profile/pages/shopdetails.html', context)
        else:
            # Get User Info
            This_User_Info = GetUserInfo().run(request)
            this_profile = This_User_Info["user_profiel"]
            this_inverntory = This_User_Info["user_inverntory"]
            # Get Menu Item
            options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
            # Get Nav Bar Menu Item
            navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
            # --------------------------------------------------------------------
            # Get This Shop
            this_shop = get_object_or_404(Shop, Slug = shop_slug)
            # Build Class
            class submarket:
                def __init__(self, item, status):
                    self.SubMarket = item
                    self.Status = status
            # Submarket List
            this_shop_submarket_list = []
            this_shop_submarket = []
            # Get Shop Submarkets
            for item in this_shop.FK_SubMarket.all():
                this_shop_submarket.append(item)
            # Select Submarket
            for item in SubMarket.objects.filter(Publish = True):
                if item in this_shop_submarket:
                    new_object = submarket(item, True)
                else:
                    new_object = submarket(item, False)
                this_shop_submarket_list.append(new_object)

            context = {
                'This_User_Profile':this_profile,
                'This_User_Inverntory': this_inverntory,
                'Options': options,
                'MenuList':navbar,
                'UserShop':this_shop,
                'Submarkets':this_shop_submarket_list,
            }

            return render(request, 'nakhll_market/profile/pages/shopdetails.html', context)
    else:
        return redirect("nakhll_market:AccountLogin")





# Shop Banners List
def shop_banner_list(request, shop_slug):
    if request.user.is_authenticated:
        # Get User Info
        This_User_Info = GetUserInfo().run(request)
        this_profile = This_User_Info["user_profiel"]
        this_inverntory = This_User_Info["user_inverntory"]
        # Get Menu Item
        options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
        # Get Nav Bar Menu Item
        navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
        # --------------------------------------------------------------------
        # Get Shop
        this_shop = get_object_or_404(Shop, Slug = shop_slug)
        # Get This Shop Banners
        this_shop_banners = ShopBanner.objects.filter(FK_Shop = this_shop)

        context = {
            'This_User_Profile':this_profile,
            'This_User_Inverntory': this_inverntory,
            'Options': options,
            'MenuList':navbar,
            'ShopID':this_shop.ID,
            'ShopBanners':this_shop_banners,
        }
     
        return render(request, 'nakhll_market/profile/pages/shopbannerlist.html', context)
    else:
        return redirect("nakhll_market:AccountLogin")





# Change Shop Banner Status
def change_shop_banner_status(request, banner_id):
    # Check User Status
    if request.user.is_authenticated :
        # Get This Banner
        this_banner = ShopBanner.objects.get(id = banner_id)
        # Change Status
        if this_banner.Available:
            this_banner.Available = False
            this_banner.save()
        else:
            this_banner.Available = True
            this_banner.save()

        return redirect("nakhll_market:Shop_Manager_ShopBannerList", shop_slug = this_banner.FK_Shop.Slug)
    else:
        return redirect("nakhll_market:AccountLogin")





# Edit Shop Banner Info
def edit_shop_banner(request, banner_id):
    # Check User Status
    if request.user.is_authenticated:
        if request.method == 'POST':
            # Get Data
            try:
                Image = request.FILES["Banner_Image"]
            except MultiValueDictKeyError:
                Image = ''

            try:
                Title = request.POST["Banner_Title"]
            except:
                Title = None

            try:
                URL = request.POST["Banner_URL"]
            except:
                URL = None
            
            try:
                Description = request.POST["Banner_Description"]
            except:
                Description = None
            
            try:
                Builder_Name = request.POST["Banner_Builder"]
            except:
                Builder_Name = None

            try:
                Builder_URL = request.POST["Banner_URL_Builder"]
            except:
                Builder_URL = None
            # Get This Shop Banner
            this_banner = get_object_or_404(ShopBanner, id = banner_id)
            try:
                # Shop Banner Edit Alert
                global edit_shop_banner_alert
                if not Alert.objects.filter(Part = '5', Slug = this_banner.id, Seen = False).exists():
                    edit_shop_banner_alert = Alert.objects.create(FK_User = request.user, Part = '5', Slug = this_banner.id)
                else:
                    edit_shop_banner_alert = Alert.objects.get(Part = '5', Slug = this_banner.id, Seen = False)
                    edit_shop_banner_alert.FK_Field.all().delete()
                # Check Change Info
                if (Title != None) and (Title != ''):
                    if Title != this_banner.Title:
                        shop_banner_title_field = Field.objects.create(Title = 'Title', Value = Title)
                        edit_shop_banner_alert.FK_Field.add(shop_banner_title_field)
                    if Image != '':
                        this_banner.NewImage = Image
                        this_banner.save()
                        new_image_string = 'NewImage' + '#' + str(this_banner.NewImage)
                        shop_banner_image_field = Field.objects.create(Title = 'Image', Value = new_image_string)
                        edit_shop_banner_alert.FK_Field.add(shop_banner_image_field)
                    if Description != this_banner.Description:
                        shop_banner_description_field = Field(Title = 'Description', Value = Description)
                        edit_shop_banner_alert.FK_Field.add(shop_banner_description_field)
                    if (URL != this_banner.URL):
                        shop_banner_url_field = FieldField.objects.create(Title = 'URL',Value = URL)
                        edit_shop_banner_alert.FK_Field.add(shop_banner_url_field)
                    if Builder_Name != this_banner.BannerBuilder:
                        shop_banner_builder_name_field = FieldField.objects.create(Title = 'BannerBuilder', Value = Builder_Name)
                        edit_shop_banner_alert.FK_Field.add(shop_banner_builder_name_field)
                    if Builder_URL != this_banner.BannerURL:
                        shop_banner_builder_name_field = Field(Title = 'BannerURL',Value = Builder_URL)
                        edit_shop_banner_alert.FK_Field.add(shop_banner_builder_name_field)
                    if edit_shop_banner_alert.FK_Field.all().count() != 0:
                        # Get User Info
                        This_User_Info = GetUserInfo().run(request)
                        this_profile = This_User_Info["user_profiel"]
                        this_inverntory = This_User_Info["user_inverntory"]
                        # Get Menu Item
                        options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
                        # Get Nav Bar Menu Item
                        navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
                        # --------------------------------------------------------------------
                        # Get Shop
                        this_shop = get_object_or_404(Shop, Slug = this_banner.FK_Shop.Slug)
                        # Get This Shop Banners
                        this_shop_banners = ShopBanner.objects.filter(FK_Shop = this_shop)
                        # Change Banner Status
                        this_banner.Edite = True
                        this_banner.save()

                        context = {
                            'This_User_Profile':this_profile,
                            'This_User_Inverntory': this_inverntory,
                            'Options': options,
                            'MenuList':navbar,
                            'ThisShop':this_shop,
                            'ShopBanners':this_shop_banners,
                            'ShowAlart':True,
                            'AlartMessage':'اطلاعات بنر حجره مورد نظر شما تغییر کرده است، و پس از تایید کارشناسان اعمال می گردد.',
                        }
                    
                        return render(request, 'nakhll_market/profile/pages/shopbannerlist.html', context)
                    else:
                        # Get User Info
                        This_User_Info = GetUserInfo().run(request)
                        this_profile = This_User_Info["user_profiel"]
                        this_inverntory = This_User_Info["user_inverntory"]
                        # Get Menu Item
                        options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
                        # Get Nav Bar Menu Item
                        navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
                        # --------------------------------------------------------------------
                        # Get This Shop Banner
                        this_banner = get_object_or_404(ShopBanner, id = banner_id)

                        context = {
                            'This_User_Profile':this_profile,
                            'This_User_Inverntory': this_inverntory,
                            'Options': options,
                            'MenuList':navbar,
                            'ThisShopBanner':this_banner,
                            'ShowAlart':True,
                            'AlartMessage':'شما تغییر ایجاد نکرده اید.'
                        }

                        return render(request, 'nakhll_market/profile/pages/editeshopbanner.html', context)
                else:
                    # Get User Info
                    This_User_Info = GetUserInfo().run(request)
                    this_profile = This_User_Info["user_profiel"]
                    this_inverntory = This_User_Info["user_inverntory"]
                    # Get Menu Item
                    options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
                    # Get Nav Bar Menu Item
                    navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
                    # --------------------------------------------------------------------
                    # Get This Shop Banner
                    this_banner = get_object_or_404(ShopBanner, id = banner_id)

                    context = {
                        'This_User_Profile':this_profile,
                        'This_User_Inverntory': this_inverntory,
                        'Options': options,
                        'MenuList':navbar,
                        'ThisShopBanner':this_banner,
                        'ShowAlart':True,
                        'AlartMessage':'فیلد "عنوان بنر" نمی تواند خالی باشد.'
                    }

                    return render(request, 'nakhll_market/profile/pages/editeshopbanner.html', context)
            except Exception as e:
                # Get User Info
                This_User_Info = GetUserInfo().run(request)
                this_profile = This_User_Info["user_profiel"]
                this_inverntory = This_User_Info["user_inverntory"]
                # Get Menu Item
                options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
                # Get Nav Bar Menu Item
                navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
                # --------------------------------------------------------------------
                # Get Shop
                this_shop = get_object_or_404(Shop, Slug = this_banner.FK_Shop.Slug)
                # Get This Shop Banners
                this_shop_banners = ShopBanner.objects.filter(FK_Shop = this_shop)

                context = {
                    'This_User_Profile':this_profile,
                    'This_User_Inverntory': this_inverntory,
                    'Options': options,
                    'MenuList':navbar,
                    'ThisShop':this_shop,
                    'ShopBanners':this_shop_banners,
                    'ShowAlart':True,
                    'AlartMessage':str(e),

                }
            
                return render(request, 'nakhll_market/profile/pages/shopbannerlist.html', context)
        else:
            # Get User Info
            This_User_Info = GetUserInfo().run(request)
            this_profile = This_User_Info["user_profiel"]
            this_inverntory = This_User_Info["user_inverntory"]
            # Get Menu Item
            options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
            # Get Nav Bar Menu Item
            navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
            # --------------------------------------------------------------------
            # Get This Shop Banner
            this_banner = get_object_or_404(ShopBanner, id = banner_id)

            context = {
                'This_User_Profile':this_profile,
                'This_User_Inverntory': this_inverntory,
                'Options': options,
                'MenuList':navbar,
                'ThisShopBanner':this_banner,
            }
        
            return render(request, 'nakhll_market/profile/pages/editeshopbanner.html', context)
    else:
        return redirect("nakhll_market:AccountLogin")






# Delete Shop Banner
def delete_shop_banner(request, banner_id):
    # Check User Status
    if request.user.is_authenticated:
        # Get User Info
        This_User_Info = GetUserInfo().run(request)
        this_profile = This_User_Info["user_profiel"]
        this_inverntory = This_User_Info["user_inverntory"]
        # Get Menu Item
        options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
        # Get Nav Bar Menu Item
        navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
        # --------------------------------------------------------------------
        # Get This Shop Banner
        this_banner = get_object_or_404(ShopBanner, id = banner_id)
        this_banner.Publish = False
        this_banner.save()
        # Get Shop
        this_shop = get_object_or_404(Shop, Slug = this_banner.FK_Shop.Slug)
        # Get This Shop Banners
        this_shop_banners = ShopBanner.objects.filter(FK_Shop = this_shop)
        # Set Alert
        if not Alert.objects.filter(Part = '22', FK_User = request.user, Slug = banner_id).exists():
            Alert.objects.create(Part = '22', FK_User = request.user, Slug = banner_id)

        context = {
            'This_User_Profile':this_profile,
            'This_User_Inverntory': this_inverntory,
            'Options': options,
            'MenuList':navbar,
            'ThisShop':this_shop,
            'ShopBanners':this_shop_banners,
            'ShowAlart':True,
            'AlartMessage':'درخواست حذف بنر شما ثبت شد، و پس از بررسی کارشناسان تایید می گردد.',
        }
    
        return render(request, 'nakhll_market/profile/pages/shopbannerlist.html', context)
    else:
        return redirect("nakhll_market:AccountLogin")






# Add New Shop Banner Info
def add_shop_banner(request, shop_slug):
    # Check User Status
    if request.user.is_authenticated :
        if request.method == 'POST':
            # Get Data
            try:
                Image = request.FILES["Banner_Image"]
            except:
                Image = ''

            try:
                Title = request.POST["Banner_Title"]
            except:
                Title = None

            try:
                URL = request.POST["Banner_URL"]
            except:
                URL = None
            
            try:
                Description = request.POST["Banner_Description"]
            except:
                Description = None
            
            try:
                Builder_Name = request.POST["Banner_Builder"]
            except:
                Builder_Name = None

            try:
                Builder_URL = request.POST["Banner_URL_Builder"]
            except:
                Builder_URL = None
            # Get This Shop Banner
            this_shop = get_object_or_404(Shop, Slug = shop_slug)
            try:
                # Set Data
                if (Title != None) and (Title != '') and (Image != ''):
                    # Create New Shop Banner
                    this_banner = ShopBanner.objects.create(FK_Shop = this_shop, Title = Title,  Image = Image)
                    # Set Shop Banner Description
                    if (Description != None) and (Description != ''):
                        this_banner.Description = Description
                        this_banner.save()
                    if (URL != None) and (URL != ''):
                        this_banner.URL = URL
                        this_banner.save()
                    if (Builder_Name != None) and (Builder_Name != ''):
                        this_banner.BannerBuilder = Builder_Name
                        this_banner.save()
                    if (Builder_URL != None) and (Builder_URL != ''):
                        this_banner.BannerURL = Builder_URL
                        this_banner.save()
                    # Add Shop Banner Alert
                    Alert.objects.create(FK_User = request.user, Part = '4', Slug = this_banner.id)
                    # Go To Shop Banner List
                    # Get User Info
                    This_User_Info = GetUserInfo().run(request)
                    this_profile = This_User_Info["user_profiel"]
                    this_inverntory = This_User_Info["user_inverntory"]
                    # Get Menu Item
                    options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
                    # Get Nav Bar Menu Item
                    navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
                    # --------------------------------------------------------------------
                    # Get Shop
                    this_shop = get_object_or_404(Shop, Slug = shop_slug)
                    # Get This Shop Banners
                    this_shop_banners = ShopBanner.objects.filter(FK_Shop = this_shop)

                    context = {
                        'This_User_Profile':this_profile,
                        'This_User_Inverntory': this_inverntory,
                        'Options': options,
                        'MenuList':navbar,
                        'ThisShop':this_shop,
                        'ShopBanners':this_shop_banners,
                        'ShowAlart':True,
                        'AlartMessage':'بنر جدیدی برای حجره "' + this_shop.Title + '" اضافه شده است، و پس از تایید کارشناسان منتشر می گردد.',
                    }
                
                    return render(request, 'nakhll_market/profile/pages/shopbannerlist.html', context) 
                else:
                    # Get User Info
                    This_User_Info = GetUserInfo().run(request)
                    this_profile = This_User_Info["user_profiel"]
                    this_inverntory = This_User_Info["user_inverntory"]
                    # Get Menu Item
                    options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
                    # Get Nav Bar Menu Item
                    navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
                    # --------------------------------------------------------------------
                    # Get Shop
                    this_shop = get_object_or_404(Shop, Slug = shop_slug)

                    context = {
                        'This_User_Profile':this_profile,
                        'This_User_Inverntory': this_inverntory,
                        'Options': options,
                        'MenuList':navbar,
                        'UserShop':this_shop,
                        'ShowAlart':True,
                        'AlartMessage':'فیلد های "عنوان بنر" و "تصویر بنر" نمی تواند خالی باشد.',
                    }
                
                    return render(request, 'nakhll_market/profile/pages/addshopbanner.html', context)                
            except Exception as e:
                # Get User Info
                This_User_Info = GetUserInfo().run(request)
                this_profile = This_User_Info["user_profiel"]
                this_inverntory = This_User_Info["user_inverntory"]
                # Get Menu Item
                options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
                # Get Nav Bar Menu Item
                navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
                # --------------------------------------------------------------------
                # Get Shop
                this_shop = get_object_or_404(Shop, Slug = shop_slug)

                context = {
                    'This_User_Profile':this_profile,
                    'This_User_Inverntory': this_inverntory,
                    'Options': options,
                    'MenuList':navbar,
                    'UserShop':this_shop,
                    'ShowAlart':True,
                    'AlartMessage':str(e),
                }
            
                return render(request, 'nakhll_market/profile/pages/addshopbanner.html', context)
        else:
            # Get User Info
            This_User_Info = GetUserInfo().run(request)
            this_profile = This_User_Info["user_profiel"]
            this_inverntory = This_User_Info["user_inverntory"]
            # Get Menu Item
            options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
            # Get Nav Bar Menu Item
            navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
            # --------------------------------------------------------------------
            # Get Shop
            this_shop = get_object_or_404(Shop, Slug = shop_slug)

            context = {
                'This_User_Profile':this_profile,
                'This_User_Inverntory': this_inverntory,
                'Options': options,
                'MenuList':navbar,
                'UserShop':this_shop,
            }
        
            return render(request, 'nakhll_market/profile/pages/addshopbanner.html', context)
    else:
        return redirect("nakhll_market:AccountLogin")






# <----------- product section ------------->

# add new product
def add_new_product(request):
    # Get User Info
    if request.user.is_authenticated:
        This_User_Info = GetUserInfo().run(request)
        this_profile = This_User_Info["user_profiel"]
        this_inverntory = This_User_Info["user_inverntory"]
        # Get Menu Item
        options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
        # Get Nav Bar Menu Item
        navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
        # --------------------------------------------------------------------
        # get user shops
        usershops = Shop.objects.filter(FK_ShopManager = request.user)
        # get all category
        allcategory = Category.objects.filter(Publish = True)
        # get all attribute
        attribute_list = list(Attribute.objects.filter(Publish = True))

        context = {
            'This_User_Profile':this_profile,
            'This_User_Inverntory': this_inverntory,
            'Options': options,
            'MenuList':navbar,
            'Shops':usershops,
            'Categort':allcategory,
            'Attribute':attribute_list,
        }

        return render(request, 'nakhll_market/profile/pages/newproduct.html', context)
    else:
        return redirect("nakhll_market:AccountLogin")




# edit product
def edit_product(request, product_slug):
   # Check User Status
    if request.user.is_authenticated :
        This_User_Info = GetUserInfo().run(request)
        this_profile = This_User_Info["user_profiel"]
        this_inverntory = This_User_Info["user_inverntory"]
        # Get Menu Item
        options = Option_Meta.objects.filter(Title='index_page_menu_items')
        # Get Nav Bar Menu Item
        navbar = Option_Meta.objects.filter(Title='nav_menu_items')
        # -------------------------------------------------------------------
        usershops = Shop.objects.filter(FK_ShopManager = request.user)
        this_product = get_object_or_404(Product, Slug = product_slug)
        allcategory = this_product.get_product_categories()
        allpostrange = this_product.get_product_inpostrange()
        allexepostrange = this_product.get_product_outpostrange()

        context = {
            'This_User_Profile':this_profile,
            'This_User_Inverntory': this_inverntory,
            'Options': options,
            'MenuList':navbar,
            'Shops':usershops,
            'Product':this_product,
            'Categort':allcategory,
            'ProPostRange':allpostrange,
            'ProExePostRange':allexepostrange,
        }
        
        return render(request, 'nakhll_market/profile/pages/editeproduct.html', context)
    else:
        return redirect("nakhll_market:AccountLogin")
        

# add to product gallery 
def add_to_product_gallery(request, product_slug):
    # Check User Status
    if request.user.is_authenticated :
        if request.method == 'POST':
            try:
                Banner_Image = request.FILES["Banner_Image"]
            except MultiValueDictKeyError:
                Banner_Image = False

            try:
                Banner_Title = request.POST["Banner_Title"]
            except MultiValueDictKeyError:
                Banner_Title = False

            try:
                Banner_URL = request.POST["Banner_URL"]
            except MultiValueDictKeyError:
                Banner_URL = False
            
            try:
                Banner_Description = request.POST["Banner_Description"]
            except MultiValueDictKeyError:
                Banner_Description = False
            
            try:
                Banner_Builder = request.POST["Banner_Builder"]
            except MultiValueDictKeyError:
                Banner_Builder = False

            try:
                Banner_URL_Builder = request.POST["Banner_URL_Builder"]
            except MultiValueDictKeyError:
                Banner_URL_Builder = False

            if ((Banner_Title != False) and (Banner_Title != '')) and ((Banner_Image != False) and (Banner_Image != '')):

                thisbanner = ProductBanner.objects.create(FK_Product = Product.objects.get(Slug = product_slug), Title = Banner_Title, Description = Banner_Description, Image = Banner_Image)
                Alert.objects.create(FK_User = request.user, Part = '8', Slug = thisbanner.id)

                if (Banner_URL != False) and (Banner_URL != ''):
                    thisbanner.URL = Banner_URL
                    thisbanner.save()

                if (Banner_Builder != False) and (Banner_Builder != ''):
                    thisbanner.BannerBuilder = Banner_Builder
                    thisbanner.save()
                
                if (Banner_URL_Builder != False) and (Banner_URL_Builder != ''):
                    thisbanner.BannerURL = Banner_URL_Builder
                    thisbanner.save()

                This_User_Info = GetUserInfo().run(request)
                this_profile = This_User_Info["user_profiel"]
                this_inverntory = This_User_Info["user_inverntory"]
                # Get Menu Item
                options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
                # Get Nav Bar Menu Item
                navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
                # --------------------------------------------------------------------
                # get this product
                this_product = get_object_or_404(Product, Slug = product_slug)
                # get all product banner
                banners = ProductBanner.objects.filter(FK_Product = this_product)

                context = {
                    'This_User_Profile':this_profile,
                    'This_User_Inverntory': this_inverntory,
                    'Options': options,
                    'MenuList':navbar,
                    'ShopBanners':banners,
                    'ShowAlart':True,
                    'AlartMessage':'بنر شما با موفقیت ثبت گردید و پس از تایید کارشناسان منتشر می گردد!',
                }
            
                return render(request, 'nakhll_market/profile/pages/productimagelist.html', context)
            else:
                This_User_Info = GetUserInfo().run(request)
                this_profile = This_User_Info["user_profiel"]
                this_inverntory = This_User_Info["user_inverntory"]
                # Get Menu Item
                options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
                # Get Nav Bar Menu Item
                navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
                # --------------------------------------------------------------------
                # get this product
                this_product = get_object_or_404(Product, Slug = product_slug)

                context = {
                    'This_User_Profile':this_profile,
                    'This_User_Inverntory': this_inverntory,
                    'Options': options,
                    'MenuList':navbar,
                    'UserProduct':this_product,
                    'ShowAlart':True,
                    'AlartMessage':'اطلاعات وارد شده کامل نمی باشد! (عنوان و عکس بنر اجباریست)',
                }
            
                return render(request, 'nakhll_market/profile/pages/productimage.html', context)
        else:
            This_User_Info = GetUserInfo().run(request)
            this_profile = This_User_Info["user_profiel"]
            this_inverntory = This_User_Info["user_inverntory"]
            # Get Menu Item
            options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
            # Get Nav Bar Menu Item
            navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
            # --------------------------------------------------------------------
            this_product = get_object_or_404(Product, Slug = product_slug)

            context = {
                'This_User_Profile':this_profile,
                'This_User_Inverntory': this_inverntory,
                'Options': options,
                'MenuList':navbar,
                'UserProduct':this_product,
            }
        
            return render(request, 'nakhll_market/profile/pages/productimage.html', context)
    else:
        return redirect("nakhll_market:AccountLogin")


# show product gallery
def show_product_gallery(request, product_slug):
    # Check User Status
    if request.user.is_authenticated :
        This_User_Info = GetUserInfo().run(request)
        this_profile = This_User_Info["user_profiel"]
        this_inverntory = This_User_Info["user_inverntory"]
        # Get Menu Item
        options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
        # Get Nav Bar Menu Item
        navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
        # --------------------------------------------------------------------
        # get this product
        this_product = get_object_or_404(Product, Slug = product_slug)
        # get all product banner
        banners = ProductBanner.objects.filter(FK_Product = this_product)

        context = {
            'This_User_Profile':this_profile,
            'This_User_Inverntory': this_inverntory,
            'Options': options,
            'MenuList':navbar,
            'ProductBanners':banners,
            'ProductID':this_product.ID,
        }

        return render(request, 'nakhll_market/profile/pages/productimagelist.html', context)
    else:
        return redirect("nakhll_market:AccountLogin")


# change product banner status
def change_product_banner_status(request, banner_id):
    # Check User Status
    if request.user.is_authenticated :
        # get this banner
        banner = get_object_or_404(ProductBanner, id = banner_id)
        # Change Status
        if banner.Available:
            banner.Available = False
            banner.save()
        else:
            banner.Available = True
            banner.save()

        return redirect("nakhll_market:Shop_Manager_ProductBannerList", product_slug = banner.FK_Product.Slug)
    else:
        return redirect("nakhll_market:AccountLogin")


# edit product banner
def edit_product_banner(request, banner_id):
    # Check User Status
    if request.user.is_authenticated :
        if request.method == 'POST':
            
            thisbanner = ProductBanner.objects.get(id = banner_id)

            try:
                Banner_Image = request.FILES["Banner_Image"]
            except MultiValueDictKeyError:
                Banner_Image = ''

            try:
                Banner_Title = request.POST["Banner_Title"]
            except MultiValueDictKeyError:
                Banner_Title = False

            try:
                Banner_URL = request.POST["Banner_URL"]
            except MultiValueDictKeyError:
                Banner_URL = False
            
            try:
                Banner_Description = request.POST["Banner_Description"]
            except MultiValueDictKeyError:
                Banner_Description = False
            
            try:
                Banner_Builder = request.POST["Banner_Builder"]
            except MultiValueDictKeyError:
                Banner_Builder = False

            try:
                Banner_URL_Builder = request.POST["Banner_URL_Builder"]
            except MultiValueDictKeyError:
                Banner_URL_Builder = False

            if (Banner_Title != ''):

                if (Banner_Title != thisbanner.Title) or (Banner_Image != '') or (Banner_Description != thisbanner.Description) or (Banner_URL != thisbanner.URL) or (Banner_Builder != thisbanner.BannerBuilder) or (Banner_URL_Builder != thisbanner.BannerURL):

                    if Alert.objects.filter(Part = '9', Slug = thisbanner.id, Seen = False).count() == 0:
                        alert = Alert.objects.create(FK_User = request.user, Part = '9', Slug = thisbanner.id)

                        if (Banner_Title != False) and (Banner_Title != thisbanner.Title):
                            Title_Alert = Field.objects.create(Title = 'Title', Value = Banner_Title)
                            alert.FK_Field.add(Title_Alert)

                        if (Banner_Image != False) and (Banner_Image != ''):
                            thisbanner.NewImage = Banner_Image
                            thisbanner.save()
                            img_str = 'NewImage' + '#' + str(thisbanner.NewImage)
                            Image_Alert = Field.objects.create(Title = 'Image', Value = 'img_str')
                            alert.FK_Field.add(Image_Alert)

                        if (Banner_Description != False) and (Banner_Description != thisbanner.Description):
                            Description_Alert = Field.objects.create(Title = 'Description', Value = Banner_Description)
                            alert.FK_Field.add(Description_Alert)

                        if (Banner_URL != False) and (Banner_URL != thisbanner.URL):
                            URL_Alert = Field.objects.create(Title = 'URL',Value = Banner_URL)
                            alert.FK_Field.add(URL_Alert)

                        if (Banner_Builder != False) and (Banner_Builder != thisbanner.BannerBuilder):
                            BannerBuilder_Alert = Field.objects.create(Title = 'BannerBuilder', Value = Banner_Builder)
                            alert.FK_Field.add(BannerBuilder_Alert)
                        
                        if (Banner_URL_Builder != False) and (Banner_URL_Builder != thisbanner.BannerURL):
                            BannerURL_Alert = Field.objects.create(Title = 'BannerURL',Value = Banner_URL_Builder)
                            alert.FK_Field.add(BannerURL_Alert)
                    else:
                        alert = Alert.objects.get(Part = '9', Slug = thisbanner.id, Seen = False)
                        alert.FK_Field.all().delete()

                        if (Banner_Title != False) and (Banner_Title != thisbanner.Title):
                            Title_Alert = Field.objects.create(Title = 'Title', Value = Banner_Title)
                            alert.FK_Field.add(Title_Alert)

                        if (Banner_Image != ''):
                            thisbanner.NewImage = Banner_Image
                            thisbanner.save()
                            img_str = 'NewImage' + '#' + str(thisbanner.NewImage)
                            Image_Alert = Field.objects.create(Title = 'Image', Value = img_str)
                            alert.FK_Field.add(Image_Alert)

                        if (Banner_Description != False) and (Banner_Description != thisbanner.Description):
                            Description_Alert = Field.objects.create(Title = 'Description', Value = Banner_Description)
                            alert.FK_Field.add(Description_Alert)

                        if (Banner_URL != False) and (Banner_URL != thisbanner.URL):
                            URL_Alert = Field.objects.create(Title = 'URL',Value = Banner_URL)
                            alert.FK_Field.add(URL_Alert)

                        if (Banner_Builder != False) and (Banner_Builder != thisbanner.BannerBuilder):
                            BannerBuilder_Alert = Field.objects.create(Title = 'BannerBuilder', Value = Banner_Builder)
                            alert.FK_Field.add(BannerBuilder_Alert)
                        
                        if (Banner_URL_Builder != False) and (Banner_URL_Builder != thisbanner.BannerURL):
                            BannerURL_Alert = Field.objects.create(Title = 'BannerURL',Value = Banner_URL_Builder)
                            alert.FK_Field.add(BannerURL_Alert)

                    This_User_Info = GetUserInfo().run(request)
                    this_profile = This_User_Info["user_profiel"]
                    this_inverntory = This_User_Info["user_inverntory"]
                    # Get Menu Item
                    options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
                    # Get Nav Bar Menu Item
                    navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
                    # --------------------------------------------------------------------
                    # get all product gallery
                    banners = ProductBanner.objects.filter(FK_Product = thisbanner.FK_Product)

                    thisbanner.Edite = True
                    thisbanner.save()

                    context = {
                        'This_User_Profile':this_profile,
                        'This_User_Inverntory': this_inverntory,
                        'Options': options,
                        'MenuList':navbar,
                        'ShopBanners':banners,
                        'ShowAlart':True,
                        'AlartMessage':'اطلاعات بنر شما با موفقیت تغییر کرده و پس از تایید کارشناسان ثبت می گردد!',
                    }
                
                    return render(request, 'nakhll_market/profile/pages/productimagelist.html', context)
                else:
                    This_User_Info = GetUserInfo().run(request)
                    this_profile = This_User_Info["user_profiel"]
                    this_inverntory = This_User_Info["user_inverntory"]
                    # Get Menu Item
                    options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
                    # Get Nav Bar Menu Item
                    navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
                    # --------------------------------------------------------------------
                    this_banner = get_object_or_404(ProductBanner, id = banner_id)

                    context = {
                        'This_User_Profile':this_profile,
                        'This_User_Inverntory': this_inverntory,
                        'Options': options,
                        'MenuList':navbar,
                        'Banners':this_banner,
                        'ShowAlart':True,
                        'AlartMessage':'تغییری ایجاد نکرده اید!'
                    }
                
                    return render(request, 'nakhll_market/profile/pages/editeproductbanner.html', context)

            else:
                This_User_Info = GetUserInfo().run(request)
                this_profile = This_User_Info["user_profiel"]
                this_inverntory = This_User_Info["user_inverntory"]
                # Get Menu Item
                options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
                # Get Nav Bar Menu Item
                navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
                # --------------------------------------------------------------------
                this_banner = get_object_or_404(ProductBanner, id = banner_id)

                context = {
                    'This_User_Profile':this_profile,
                    'This_User_Inverntory': this_inverntory,
                    'Options': options,
                    'MenuList':navbar,
                    'Banners':this_banner,
                    'ShowAlart':True,
                    'AlartMessage':'موارد وارد شده کامل نمی باشند! (عکس و عنوان اجباریست)'
                }
            
                return render(request, 'nakhll_market/profile/pages/editeproductbanner.html', context)

        else:
            This_User_Info = GetUserInfo().run(request)
            this_profile = This_User_Info["user_profiel"]
            this_inverntory = This_User_Info["user_inverntory"]
            # Get Menu Item
            options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
            # Get Nav Bar Menu Item
            navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
            # --------------------------------------------------------------------
            this_banner = get_object_or_404(ProductBanner, id = banner_id)

            context = {
                'This_User_Profile':this_profile,
                'This_User_Inverntory': this_inverntory,
                'Options': options,
                'MenuList':navbar,
                'Banners':this_banner,
            }
        
            return render(request, 'nakhll_market/profile/pages/editeproductbanner.html', context)

    else:
        return redirect("nakhll_market:AccountLogin")


# delete product banner
def delete_product_banner(request, banner_id):
    # Check User Status
    if request.user.is_authenticated :
        This_User_Info = GetUserInfo().run(request)
        this_profile = This_User_Info["user_profiel"]
        this_inverntory = This_User_Info["user_inverntory"]
        # Get Menu Item
        options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
        # Get Nav Bar Menu Item
        navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
        # --------------------------------------------------------------------
        # get this banner
        banner = get_object_or_404(ProductBanner, id = banner_id)
        banner.Publish = False
        banner.save()
        # get all product banner
        banners = ProductBanner.objects.filter(FK_Product = banner.FK_Product)
        # set alert
        if not Alert.objects.filter(FK_User = request.user, Part = '23', Slug = banner.id).exists():
            alert = Alert.objects.create(FK_User = request.user, Part = '23', Slug = banner.id)

        context = {
            'This_User_Profile':this_profile,
            'This_User_Inverntory': this_inverntory,
            'Options': options,
            'MenuList':navbar,
            'ShopBanners':banners,
            'ShowAlart':True,
            'AlartMessage':'بنر شما پس از بررسی کارشناسان حذف می گردد!',
        }
    
        return render(request, 'nakhll_market/profile/pages/productimagelist.html', context)
    else:
        return redirect("nakhll_market:AccountLogin")



# product attribute list
def product_attribute_list(request, product_slug):
    # Check User Status
    if request.user.is_authenticated:
        This_User_Info = GetUserInfo().run(request)
        this_profile = This_User_Info["user_profiel"]
        this_inverntory = This_User_Info["user_inverntory"]
        # Get Menu Item
        options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
        # Get Nav Bar Menu Item
        navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
        # --------------------------------------------------------------------
        # get this product
        this_product = get_object_or_404(Product, Slug = product_slug)
        # get product attribute
        product_attribute_list = AttrProduct.objects.filter(FK_Product = this_product)
        # get all attribute
        attribute_list = Attribute.objects.filter(Publish = True)

        context = {
            'This_User_Profile':this_profile,
            'This_User_Inverntory': this_inverntory,
            'Options': options,
            'MenuList':navbar,
            'AttrProduct':product_attribute_list,
            'Attributes':attribute_list,
            'NetWeight':this_product.Net_Weight,
            'WeightWithPacking':this_product.Weight_With_Packing,
            'Length_Width_Height':this_product.Length_With_Packaging + '*' + this_product.Width_With_Packaging + '*' + this_product.Height_With_Packaging,
            'ProductID':this_product.ID,
        }
     
        return render(request, 'nakhll_market/profile/pages/productattributelist.html', context)
    else:
        return redirect("nakhll_market:AccountLogin")



# add product attribute
def add_product_attribute(request, product_slug):
    # Check User Status
    if request.user.is_authenticated:
        if request.method == 'POST':
            try:
                AttrTitle = request.POST["Attribute_Title"]
            except:
                AttrTitle = None

            try:
                AttrValue = request.POST["Attribute_Value"]
            except:
                AttrValue = None

            if ((AttrTitle != None) and (AttrTitle != '')) and ((AttrValue != None) and (AttrValue != '')):
                # get this product
                this_product = get_object_or_404(Product, Slug = product_slug)
                # get this attribute
                this_attribute = get_object_or_404(Attribute, id = AttrTitle)
                if not AttrProduct.objects.filter(FK_Product = this_product, FK_Attribute = this_attribute).exists():
                    attrproduct = AttrProduct.objects.create(FK_Product = this_product, FK_Attribute = this_attribute, Value = AttrValue)

                    if not Alert.objects.filter(FK_User = request.user, Part = '11', Slug = attrproduct.id).exists():
                        Alert.objects.create(FK_User = request.user, Part = '11', Slug = attrproduct.id)

                    This_User_Info = GetUserInfo().run(request)
                    this_profile = This_User_Info["user_profiel"]
                    this_inverntory = This_User_Info["user_inverntory"]
                    # Get Menu Item
                    options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
                    # Get Nav Bar Menu Item
                    navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
                    # --------------------------------------------------------------------
                    # get all attribute
                    attribute_list = Attribute.objects.filter(Publish = True)
                    # this product
                    this_product = get_object_or_404(Product, Slug = product_slug)

                    context = {  
                        'This_User_Profile':this_profile,
                        'This_User_Inverntory': this_inverntory,
                        'Options': options,
                        'MenuList':navbar,
                        'Attributes':attribute_list,
                        'Product':this_product,
                        'ShowAlart':True,
                        'AlartMessage':'ویژگی محصول شما ثبت شد و پس از بررسی کارشناسان اضافه می شود!',
                    }
                
                    return render(request, 'nakhll_market/profile/pages/productattribute.html', context)
                else:
                    This_User_Info = GetUserInfo().run(request)
                    this_profile = This_User_Info["user_profiel"]
                    this_inverntory = This_User_Info["user_inverntory"]
                    # Get Menu Item
                    options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
                    # Get Nav Bar Menu Item
                    navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
                    # --------------------------------------------------------------------
                    # get all attribute
                    attribute_list = Attribute.objects.filter(Publish = True)
                    # this product
                    this_product = get_object_or_404(Product, Slug = product_slug)

                    context = {
                        'This_User_Profile':this_profile,
                        'This_User_Inverntory': this_inverntory,
                        'Options': options,
                        'MenuList':navbar,
                        'Attributes':attribute_list,
                        'Product':this_product,
                        'ShowAlart':True,
                        'AlartMessage':'این ویژگی قبلا برای این محصول ثبت شده است!',
                    }
                
                    return render(request, 'nakhll_market/profile/pages/productattribute.html', context)

            else:
                This_User_Info = GetUserInfo().run(request)
                this_profile = This_User_Info["user_profiel"]
                this_inverntory = This_User_Info["user_inverntory"]
                # Get Menu Item
                options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
                # Get Nav Bar Menu Item
                navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
                # --------------------------------------------------------------------
                # get all attribute
                attribute_list = Attribute.objects.filter(Publish = True)
                # this product
                this_product = get_object_or_404(Product, Slug = product_slug)

                context = { 
                    'This_User_Profile':this_profile,
                    'This_User_Inverntory': this_inverntory,
                    'Options': options,
                    'MenuList':navbar,
                    'Attributes':attribute_list,
                    'Product':this_product,
                    'ShowAlart':True,
                    'AlartMessage':'مقادیر وارد شده معتبر نمی باشد!',
                }
            
                return render(request, 'nakhll_market/profile/pages/productattribute.html', context)

        else:
            This_User_Info = GetUserInfo().run(request)
            this_profile = This_User_Info["user_profiel"]
            this_inverntory = This_User_Info["user_inverntory"]
            # Get Menu Item
            options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
            # Get Nav Bar Menu Item
            navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
            # --------------------------------------------------------------------
            # get all attribute
            attribute_list = Attribute.objects.filter(Publish = True)
            # this product
            this_product = get_object_or_404(Product, Slug = product_slug)

            context = {
                'This_User_Profile':this_profile,
                'This_User_Inverntory': this_inverntory,
                'Options': options,
                'MenuList':navbar,
                'Attributes':attribute_list,
                'Product':this_product,
            }
        
            return render(request, 'nakhll_market/profile/pages/productattribute.html', context)

    else:
        return redirect("nakhll_market:AccountLogin")


# delete product attribute
def delete_product_attribute(request, attr_id):
    # Check User Status
    if request.user.is_authenticated :
        This_User_Info = GetUserInfo().run(request)
        this_profile = This_User_Info["user_profiel"]
        this_inverntory = This_User_Info["user_inverntory"]
        # Get Menu Item
        options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
        # Get Nav Bar Menu Item
        navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
        # --------------------------------------------------------------------
        # get this attribute product
        this_attribute_product = get_object_or_404(AttrProduct, id = attr_id)
        # change status
        this_attribute_product.Available = False
        this_attribute_product.save()
        # set alert
        if not Alert.objects.filter(Part = '24', FK_User = request.user, Slug = this_attribute_product.id).exists():
            Alert.objects.create(Part = '24', FK_User = request.user, Slug = this_attribute_product.id)
        # get this product
        this_product = this_attribute_product.FK_Product
        # get product attribute
        product_attribute_list = AttrProduct.objects.filter(FK_Product = this_product)

        context = {
            'This_User_Profile':this_profile,
            'This_User_Inverntory': this_inverntory,
            'Options': options,
            'MenuList':navbar,
            'AttrProduct':product_attribute_list,
            'ShowAlart':True,
            'AlartMessage':'ویژگی شما پس از بررسی کارشناسان حذف می گردد!',
        }
     
        return render(request, 'nakhll_market/profile/pages/productattributelist.html', context)
    else:
        return redirect("nakhll_market:AccountLogin")


# add new attribute
def add_new_attribute(request, product_slug):
    # Check User Status
    if request.user.is_authenticated:
        if request.method == 'POST':
            # get data
            try:
                AttrTitle = request.POST["Attribute"]
            except:
                AttrTitle = None
            try:
                AttrUnit = request.POST["UnitAttribute"]
            except:
                AttrUnit = None
            # add new data
            if ((AttrUnit != None) and (AttrUnit != '')) and ((AttrTitle != None) and (AttrTitle != '')):

                if not (Attribute.objects.filter(Title = AttrTitle, Unit = AttrUnit)).exists():
                    # create new attribute
                    this_attribute = Attribute.objects.create(Title = AttrTitle, Unit = AttrUnit)
                    # set alert
                    Alert.objects.create(FK_User = request.user, Part = '10', Slug = this_attribute.id)

                    This_User_Info = GetUserInfo().run(request)
                    this_profile = This_User_Info["user_profiel"]
                    this_inverntory = This_User_Info["user_inverntory"]
                    # Get Menu Item
                    options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
                    # Get Nav Bar Menu Item
                    navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
                    # --------------------------------------------------------------------
                    # get all attribute
                    attribute_list = Attribute.objects.filter(Publish = True)
                    # this product
                    this_product = get_object_or_404(Product, Slug = product_slug)

                    context = {  
                        'This_User_Profile':this_profile,
                        'This_User_Inverntory': this_inverntory,
                        'Options': options,
                        'MenuList':navbar,
                        'Attributes':attribute_list,
                        'Product':this_product,
                        'ShowAlart':True,
                        'AlartMessage':'ویژگی مدنظر شما ثبت شد و پس از بررسی کارشناسان اضافه می شود!',
                    }
                
                    return render(request, 'nakhll_market/profile/pages/productattribute.html', context)
                else:
                    This_User_Info = GetUserInfo().run(request)
                    this_profile = This_User_Info["user_profiel"]
                    this_inverntory = This_User_Info["user_inverntory"]
                    # Get Menu Item
                    options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
                    # Get Nav Bar Menu Item
                    navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
                    # --------------------------------------------------------------------
                    # get all attribute
                    attribute_list = Attribute.objects.filter(Publish = True)
                    # this product
                    this_product = get_object_or_404(Product, Slug = product_slug)

                    context = {
                        'This_User_Profile':this_profile,
                        'This_User_Inverntory': this_inverntory,
                        'Options': options,
                        'MenuList':navbar,
                        'Attributes':attribute_list,
                        'Product':this_product,
                        'ShowAlart':True,
                        'AlartMessage':'ویژگی با این مشخصات موجود است!',
                    }
                
                    return render(request, 'nakhll_market/profile/pages/productattribute.html', context)
            else:
                This_User_Info = GetUserInfo().run(request)
                this_profile = This_User_Info["user_profiel"]
                this_inverntory = This_User_Info["user_inverntory"]
                # Get Menu Item
                options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
                # Get Nav Bar Menu Item
                navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
                # --------------------------------------------------------------------
                # get all attribute
                attribute_list = Attribute.objects.filter(Publish = True)
                # this product
                this_product = get_object_or_404(Product, Slug = product_slug)

                context = {
                    'This_User_Profile':this_profile,
                    'This_User_Inverntory': this_inverntory,
                    'Options': options,
                    'MenuList':navbar,
                    'Attributes':attribute_list,
                    'Product':this_product,
                    'ShowAlart':True,
                    'AlartMessage':'مقادیر وارد شده معتبر نمی باشد!',
                }
            
                return render(request, 'nakhll_market/profile/pages/productattribute.html', context)
        else:
            This_User_Info = GetUserInfo().run(request)
            this_profile = This_User_Info["user_profiel"]
            this_inverntory = This_User_Info["user_inverntory"]
            # Get Menu Item
            options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
            # Get Nav Bar Menu Item
            navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
            # --------------------------------------------------------------------
            # get all attribute
            attribute_list = Attribute.objects.filter(Publish = True)
            # this product
            this_product = get_object_or_404(Product, Slug = product_slug)

            context = {
                'This_User_Profile':this_profile,
                'This_User_Inverntory': this_inverntory,
                'Options': options,
                'MenuList':navbar,
                'Attributes':attribute_list,
                'Product':this_product,
            }
        
            return render(request, 'nakhll_market/profile/pages/productattribute.html', context)
    else:
        return redirect("nakhll_market:AccountLogin")


# product attribute price list
def product_attribute_price_list(request, product_slug):
    # Check User Status
    if request.user.is_authenticated :
        This_User_Info = GetUserInfo().run(request)
        this_profile = This_User_Info["user_profiel"]
        this_inverntory = This_User_Info["user_inverntory"]
        # Get Menu Item
        options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
        # Get Nav Bar Menu Item
        navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
        # --------------------------------------------------------------------
        # get this product
        this_product = get_object_or_404(Product, Slug = product_slug)
        # get all product optional attribute
        optional_attribute_list = this_product.FK_OptinalAttribute.filter(Publish = True)

        context = {
            'This_User_Profile':this_profile,
            'This_User_Inverntory': this_inverntory,
            'Options': options,
            'MenuList':navbar,
            'ThisProduct':this_product,
            'OptinalAttribute':optional_attribute_list,
        }
        
        return render(request, 'nakhll_market/profile/pages/showattrpricelist.html', context)
    else:    
        return redirect("nakhll_market:AccountLogin")


# change product attribute price status
def change_product_attribute_price_status(request, id):
    # Check User Status
    if request.user.is_authenticated :
        this_attrprice = get_object_or_404(AttrPrice, id = id)
        # Change Status
        if this_attrprice.Available:
            this_attrprice.Available = False
            this_attrprice.save()
        else:
            this_attrprice.Available = True
            this_attrprice.save()
        return redirect("nakhll_market:Shop_Manager_ProductPriceAttributeList", product_slug = this_attrprice.FK_Product.Slug)
    else:    
        return redirect("nakhll_market:AccountLogin")


# delete product attribute price
def delete_product_attribute_price(request, id):
    # Check User Status
    if request.user.is_authenticated :
        # get this product attribute price
        this_attrprice = get_object_or_404(AttrPrice, id = id)
        # change status
        this_attrprice.Publish = False
        this_attrprice.save()
        # set alert
        if not Alert.objects.filter(Part = '25', FK_User = request.user, Slug = this_attrprice.id).exists():
            Alert.objects.create(Part = '25', FK_User = request.user, Slug = this_attrprice.id)
        return redirect("nakhll_market:Shop_Manager_ProductPriceAttributeList", product_slug = this_attrprice.FK_Product.Slug)
    else:
        return redirect("nakhll_market:AccountLogin")



# add new product attribute price
def add_product_attribute_price(request, product_slug):
    # Check User Status
    if request.user.is_authenticated :
        if request.method == 'POST':
            # get data
            try:
                AttrPrice_Value = request.POST["AttributePrice_Value"]
            except :
                AttrPrice_Value = None
            try:
                AttrPrice_Exp = request.POST["AttributePrice_Exp"]
            except :
                AttrPrice_Exp = None
            try:
                AttrPrice_Unit = request.POST["AttributePrice_Unit"]
            except :
                AttrPrice_Unit = None
            try:
                AttrPrice_Des = request.POST["AttributePrice_Des"]
            except :
                AttrPrice_Des = None
            # set data
            if ((AttrPrice_Value != None) and (AttrPrice_Value != '')) and ((AttrPrice_Exp != None) and (AttrPrice_Exp != '')) and ((AttrPrice_Unit != None) and (AttrPrice_Unit != '')):
                # get this product
                this_product = get_object_or_404(Product, Slug = product_slug)
                if not AttrPrice.objects.filter(FK_Product = this_product, Value = AttrPrice_Value, ExtraPrice = AttrPrice_Exp, Unit = AttrPrice_Unit).exists():
                    # create new attribute price
                    attrprice = AttrPrice.objects.create(FK_Product = this_product, Value = AttrPrice_Value, ExtraPrice = AttrPrice_Exp, Unit = AttrPrice_Unit, Publish = False)
                    if AttrPrice_Des != '':
                        attrprice.Description = AttrPrice_Des
                        attrprice.save()
                    # set alert
                    Alert.objects.create(Part = '17', FK_User = request.user, Slug = attrprice.id)
            
                    # Get User Info
                    This_User_Info = GetUserInfo().run(request)
                    this_profile = This_User_Info["user_profiel"]
                    this_inverntory = This_User_Info["user_inverntory"]
                    # Get Menu Item
                    options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
                    # Get Nav Bar Menu Item
                    navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
                    # --------------------------------------------------------------------
                    # get all product attribute price
                    attribute_price_list = AttrPrice.objects.filter(FK_Product = this_product)

                    context = {
                        'This_User_Profile':this_profile,
                        'This_User_Inverntory': this_inverntory,
                        'Options': options,
                        'MenuList':navbar,
                        'Product':this_product,
                        'AttrPrice':attribute_price_list,
                        'ShowAlart':True,
                        'AlartMessage':'ارزش ویژگی شما ثبت شد و بعد از بررسی کارشناسان منتشر می گردد!',
                    }
                    
                    return render(request, 'nakhll_market/profile/pages/showattrpricelist.html', context)
                else:
                    # Get User Info
                    This_User_Info = GetUserInfo().run(request)
                    this_profile = This_User_Info["user_profiel"]
                    this_inverntory = This_User_Info["user_inverntory"]
                    # Get Menu Item
                    options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
                    # Get Nav Bar Menu Item
                    navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
                    # -------------------------------------------------------------------
                    # get this product
                    this_product = get_object_or_404(Product, Slug = product_slug)

                    context = {
                        'This_User_Profile':this_profile,
                        'This_User_Inverntory': this_inverntory,
                        'Options': options,
                        'MenuList':navbar,
                        'Product':this_product,
                        'ShowAlart':True,
                        'AlartMessage':'ارزش ویژگی با این مشخصات قبلا برای این محصول ثبت شده است!',
                    }
                    
                    return render(request, 'nakhll_market/profile/pages/showattrprice.html', context)
            else:
                # Get User Info
                This_User_Info = GetUserInfo().run(request)
                this_profile = This_User_Info["user_profiel"]
                this_inverntory = This_User_Info["user_inverntory"]
                # Get Menu Item
                options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
                # Get Nav Bar Menu Item
                navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
                # -------------------------------------------------------------------
                # get this product
                this_product = get_object_or_404(Product, Slug = product_slug)


                context = {
                    'This_User_Profile':this_profile,
                    'This_User_Inverntory': this_inverntory,
                    'Options': options,
                    'MenuList':navbar,
                    'Product':this_product,
                    'ShowAlart':True,
                    'AlartMessage':'لطفا تمامی فیلد های ستاره دار را کامل کنید!',
                }
                
                return render(request, 'nakhll_market/profile/pages/showattrprice.html', context)
        else:
            # Get User Info
            This_User_Info = GetUserInfo().run(request)
            this_profile = This_User_Info["user_profiel"]
            this_inverntory = This_User_Info["user_inverntory"]
            # Get Menu Item
            options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
            # Get Nav Bar Menu Item
            navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
            # -------------------------------------------------------------------
            # get this product
            this_product = get_object_or_404(Product, Slug = product_slug)


            context = {
                'This_User_Profile':this_profile,
                'This_User_Inverntory': this_inverntory,
                'Options': options,
                'MenuList':navbar,
                'Product':this_product,
            }
            
            return render(request, 'nakhll_market/profile/pages/showattrprice.html', context)
    else:
        return redirect("nakhll_market:AccountLogin")


# <----------- end product section ------------->




































# ---------------- Ticketin Section ----------------------------

# Get User Ticketing
def ProfileTicketing(request):
    # Check User Status
    if request.user.is_authenticated :
        # Get User Info
        This_User_Info = GetUserInfo().run(request)
        this_profile = This_User_Info["user_profiel"]
        this_inverntory = This_User_Info["user_inverntory"]
        # Get Menu Item
        options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
        # Get Nav Bar Menu Item
        navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
        # ----------------------------------------------------------------
        ticketing = Ticketing.objects.filter(FK_Importer = request.user).order_by('-Date')
        ticfani = ticketing.filter(SectionType = '2').count()
        ticposhtibani = ticketing.filter(SectionType = '0').count()
        ticmali = ticketing.filter(SectionType = '1').count()

        context = {
            'This_User_Profile':this_profile,
            'This_User_Inverntory': this_inverntory,
            'Options': options,
            'MenuList':navbar,
            'Ticketings':ticketing,
            'TicFani':ticfani,
            'TicPoshtibani':ticposhtibani,
            'TicMali':ticmali,
        }
     
        return render(request, 'nakhll_market/profile/pages/ticketing.html', context)
    else:
        return redirect("nakhll_market:AccountLogin")

# Add New Ticket
def AddNewTicket(request):
    # Check User Status
    if request.user.is_authenticated :

        if request.method == 'POST': 

            try:
                Tic_Title = request.POST["Ticket_Title"]
            except MultiValueDictKeyError:
                Tic_Title = False

            try:
               Tic_Sec = request.POST["Ticket_Section"]
            except MultiValueDictKeyError:
               Tic_Sec = False

            try:
                Tic_Des = request.POST["Ticket_Description"]
            except MultiValueDictKeyError:
               Tic_Des = False
  
            try:
                Tic_Img = request.FILES["Ticket_Image"]
            except MultiValueDictKeyError:
                Tic_Img = False
               

            if (Tic_Title != False) and (Tic_Sec != False) and (Tic_Des != False):

                if (Tic_Img != False):
                    tic = Ticketing(Title = Tic_Title, SectionType = Tic_Sec, FK_Importer = request.user, Description = Tic_Des, Image = Tic_Img)
                    tic.save()
                else:
                    tic = Ticketing(Title = Tic_Title, SectionType = Tic_Sec, FK_Importer = request.user, Description = Tic_Des)
                    tic.save()

                if Alert.objects.filter(Part = '16', FK_User = request.user, Slug = tic.ID, Seen = False).count() == 0:
                    alert = Alert(Part = '16', FK_User = request.user, Slug = tic.ID)
                    alert.save()

            else:
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
                # ----------------------------------------------------------------
                ticketing = Ticketing.objects.filter(FK_Importer = request.user).order_by('Date')
                ticfani = ticketing.filter(SectionType = '2').count()
                ticposhtibani = ticketing.filter(SectionType = '0').count()
                ticmali = ticketing.filter(SectionType = '1').count()

                context = {
                    'Users':user,
                    'Profile':profile,
                    'Wallet': wallets,
                    'Options': options,
                    'MenuList':navbar,
                    'ShowAlart':True,
                    'Ticketings':ticketing,
                    'TicFani':ticfani,
                    'TicPoshtibani':ticposhtibani,
                    'TicMali':ticmali,
                    'AlartMessage':'تیکت شما ثبت نشد!'
                }

                return render(request, 'nakhll_market/profile/pages/ticketing.html', context)

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
            # ----------------------------------------------------------------
            ticketing = Ticketing.objects.filter(FK_Importer = request.user).order_by('Date')
            ticfani = ticketing.filter(SectionType = '2').count()
            ticposhtibani = ticketing.filter(SectionType = '0').count()
            ticmali = ticketing.filter(SectionType = '1').count()

            context = {
                'Users':user,
                'Profile':profile,
                'Wallet': wallets,
                'Options': options,
                'MenuList':navbar,
                'ShowAlart':True,
                'Ticketings':ticketing,
                'TicFani':ticfani,
                'TicPoshtibani':ticposhtibani,
                'TicMali':ticmali,
                'AlartMessage':'تیکت شما ثبت شد!'
            }
        
            return render(request, 'nakhll_market/profile/pages/ticketing.html', context)

    else:    
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

        context = {
            'Users':user,
            'Profile':profile,
            'Wallet': wallets,
            'Options': options,
            'MenuList':navbar,
        }
        
        return render(request, 'registration/login.html', context)

# Ticket Detail
def ProfileTicketingDetail(request, ticket_id):
    # Check User Status
    if request.user.is_authenticated :
        # Get User Info
        This_User_Info = GetUserInfo().run(request)
        this_profile = This_User_Info["user_profiel"]
        this_inverntory = This_User_Info["user_inverntory"]
        # Get Menu Item
        options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
        # Get Nav Bar Menu Item
        navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
        # ------- Ticket --------------------------------------------------
        # Get This Tickect
        ticket = get_object_or_404(Ticketing, ID = ticket_id)
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
        # ------------------------------
        ticketing = Ticketing.objects.filter(FK_Importer = request.user).order_by('-Date')
        ticfani = ticketing.filter(SectionType = '2').count()
        ticposhtibani = ticketing.filter(SectionType = '0').count()
        ticmali = ticketing.filter(SectionType = '1').count()


        context = {
            'This_User_Profile':this_profile,
            'This_User_Inverntory': this_inverntory,
            'Options': options,
            'MenuList':navbar,
            'Ticketings':ticketing,
            'TicFani':ticfani,
            'TicPoshtibani':ticposhtibani,
            'TicMali':ticmali,
            'ThisTicket':ticket,
            'ReplayTicket':ticket_replay_list,
        }
        
        return render(request, 'nakhll_market/profile/pages/ticketdetail.html', context)



# Replay Ticket
def RepalyTicketing(request, ticket_id):
    # Check User Status
    if request.user.is_authenticated :
        if request.method == 'POST': 
            try:
                Tic_Title = request.POST["Ticket_Pasokh"]
                # Set Replay
                fatherticket = get_object_or_404(Ticketing, ID = ticket_id)
                fatherticket.SeenStatus = '0'
                fatherticket.save()
                new_ticket = TicketingMessage.objects.create(Description = Tic_Title, FK_Importer = request.user, FK_Replay = fatherticket)
                Alert.objects.create(Part = '16', FK_User = request.user, Slug = ticket_id)
                # -------------------------------------------------------------------------------------------------------------------------
                return redirect("nakhll_market:TicketinDetail", ticket_id = ticket_id)
            except Exception as e:
                return redirect("nakhll_market:error_500", error_text = str(e))  
    else:    
        return redirect("nakhll_market:AccountLogin")

# ---------------------- End Ticketin Section ----------------------


# Profile Alert
def ProfileAlert(request):
    # Check User Status
    if request.user.is_authenticated :
        # Get User Info
        This_User_Info = GetUserInfo().run(request)
        this_profile = This_User_Info["user_profiel"]
        this_inverntory = This_User_Info["user_inverntory"]
        # Get Menu Item
        options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
        # Get Nav Bar Menu Item
        navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
        # --------------------------------------------------------------------
        # get all new alert
        alert = Alert.objects.filter(Seen = False).order_by('DateCreate')
        # get user list
        user_list = []
        for item in alert:
            user_list.append(item.FK_User)
        user_list = list(dict.fromkeys(user_list))

        context = {
            'This_User_Profile':this_profile,
            'This_User_Inverntory': this_inverntory,
            'Options': options,
            'MenuList':navbar,
            'Alert':alert,
            'User':user_list,
        }
     
        return render(request, 'nakhll_market/profile/pages/alert.html', context)
    else:
        return redirect("nakhll_market:AccountLogin")


# Update Profile Values
#--------------------------------------------------------------------------------------------------------------------------------

# Update Dashboard (User Info) Values
def UpdateUserDashbord(request):
    if request.user.is_authenticated:
        try:
            # Get Data
            try:
                FirstName = request.POST["User_FirstName"]
            except:
                FirstName = ''

            try:
                LastName = request.POST["User_LastName"]
            except :
                LastName = ''

            try:
                Email = request.POST["User_Email"]
            except :
                Email = ''

            try:
                Image = request.FILES["Profile_Image"]
            except MultiValueDictKeyError:
                Image = ''

            try:
                Bio = request.POST["Profile_Bio"]
            except:
                Bio = ''

            try:
                BrithDay = request.POST["Profile_BrithDay"]
            except:
                BrithDay = ''

            try:
                State = request.POST["Profile_State"]
            except:
                State = ''

            try:
                BigCity = request.POST["Profile_BigCity"]
            except:
                BigCity = ''

            try:
                City = request.POST["Profile_City"]
            except:
                City = ''

            try:
                ZipCode = request.POST["Profile_ZipCode"]
            except:
                ZipCode = ''

            try:
                PhoneNumber = request.POST["Profile_PhoneNumber"]
            except:
                PhoneNumber = ''

            try:
                Address = request.POST["Profile_Address"]
            except:
                Address = ''

            try:
                CityPerCode = request.POST["Profile_CityPerCode"]
            except:
                CityPerCode = ''

            try:
                SexState = request.POST["Profile_SexState"]
            except:
                SexState = 'انتخاب جنسیت'

            if SexState == 'انتخاب جنسیت':
                Sex = '0'
            elif SexState == 'زن':
                Sex = '1'
            elif SexState == 'مرد':
                Sex = '2'
            elif SexState == 'سایر':
                Sex = '3'

            try:
                TutorialWebsite = request.POST["Profile_TutorialWebsite"]
            except:
                TutorialWebsite = 'هیچ کدام'

            if TutorialWebsite == 'موتور های جستجو':
                ToWeb = '0'
            elif TutorialWebsite == 'حجره داران':
                ToWeb = '1'
            elif TutorialWebsite == 'شبکه های اجتماعی':
                ToWeb = '2'
            elif TutorialWebsite == 'کاربران':
                ToWeb = '3'
            elif TutorialWebsite == 'رسانه ها':
                ToWeb = '4'
            elif TutorialWebsite == 'تبلیغات':
                ToWeb = '5'
            elif TutorialWebsite == 'نود ها':
                ToWeb = '6'
            elif TutorialWebsite == 'سایر':
                ToWeb = '7'
            elif TutorialWebsite == 'هیچ کدام':
                ToWeb = '8'
            #-------------------------------------------------------------
            # Get User
            this_user = request.user
            # Get Profile
            this_profile = get_object_or_404(Profile, FK_User = this_user)
            # Edit Status
            edit_user = False
            edit_profile = False
            # Get User State, BigCity, City Title
            state = ''
            bigcity = ''
            city = ''
            global object
            with open('Iran.json', encoding = 'utf8') as f:
                object = json.load(f)
            for i in object:
                if (i['divisionType'] == 1) and (i['id'] == int(State)):
                    state = i['name']
                if (i['divisionType'] == 2) and (i['id'] == int(BigCity)):
                    bigcity = i['name']
                if (i['divisionType'] == 3) and (i['id'] == int(City)):
                    if i['name'] == 'مرکزی':
                        for j in object:
                            if (j['divisionType'] == 2) and (j['id'] == i['parentCountryDivisionId']):
                                city = j['name']
                    else:
                        city = i['name']
            # Check Fileds
            if this_user.first_name != FirstName:
                this_user.first_name = FirstName
                edit_user = True
            if this_user.last_name != LastName:
                this_user.last_name = LastName
                edit_user = True
            if this_user.email != Email:
                this_user.email = Email
                edit_user = True
                if not Newsletters.objects.filter(Email = Email).exists():
                    New = Newsletters.objects.create(Email = Email)
            if this_profile.ZipCode != ZipCode:
                this_profile.ZipCode = ZipCode
                edit_profile = True
            if this_profile.Address != Address:
                this_profile.Address = Address
                edit_profile = True
            if this_profile.State != state:
                this_profile.State = state
                edit_profile = True
            if this_profile.BigCity != bigcity:
                this_profile.BigCity = bigcity
                edit_profile = True
            if this_profile.City != city:
                this_profile.City = city
                edit_profile = True
            if this_profile.BrithDay != BrithDay:
                this_profile.BrithDay = BrithDay
                edit_profile = True
            if this_profile.CityPerCode != CityPerCode:
                this_profile.CityPerCode = CityPerCode
                edit_profile = True
            if this_profile.PhoneNumber != PhoneNumber:
                this_profile.PhoneNumber = PhoneNumber
                edit_profile = True
            if this_profile.Bio != Bio:
                this_profile.Bio = Bio
                edit_profile = True
            if this_profile.Sex != Sex:
                this_profile.Sex = Sex
                edit_profile = True
            if this_profile.TutorialWebsite != ToWeb:
                this_profile.TutorialWebsite = ToWeb
                edit_profile = True
            if Image != '':
                this_profile.Image = Image
                edit_profile = True

            if edit_user:
                this_user.save()
            if edit_profile:
                this_profile.save()
            # -----------------------------------------
            return redirect("nakhll_market:Dashbord")
        except Exception as e:
            return redirect("nakhll_market:error_500", error_text = str(e))
    else:
        return redirect("nakhll_market:AccountLogin")


















# --------------------------------------- Add Connect Us Message ----------------------------------------

# Add New Connect
def AddNewConnect(request):

    if request.method == 'POST':

        try:
            Connect_Title = request.POST["Input_Title"]
        except :
            Connect_Title = ''

        try:
            Connect_Des = request.POST["Input_Text"]
        except :
            Connect_Des = ''

        try:
            Connect_PhoneNumber = request.POST["Input_Phone"]
        except :
            Connect_PhoneNumber = ''

        try:
            Connect_Email = request.POST["Input_Email"]
        except :
            Connect_Email = ''

        if (Connect_PhoneNumber != '') or (Connect_Email != ''):

            msg = Complaint(Title = Connect_Title, Description = Connect_Des, MobileNumber = Connect_PhoneNumber, Email = Connect_Email, Type = '1')
            msg.save()

            alert = Alert(Part = '18', FK_User = request.user, Slug = msg.id)
            alert.save()
            
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
                'ShowAlart':True,
                'AlartMessage':'پیام شما ثبت و بعد از بررسی کارشناسان نتیجه آن به شما گزارش داده می شود!',
                'ConnectRoad':Road,
            }

            return render(request, 'nakhll_market/pages/connect.html', context)

        else:

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
                'ShowAlart':True,
                'AlartMessage':'برای پاسخ دهی به پیام شما، لازم است حداقل یکی از فیلد های شماره تماس یا ایمیل را پر نمایید!',
                'ConnectRoad':Road,
            }

            return render(request, 'nakhll_market/pages/connect.html', context)
    else:

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


# Add New Complint
def AddNewComplaint(request):

    if request.method == 'POST':

        try:
            Connect_Title = request.POST["Input_Title"]
        except :
            Connect_Title = ''

        try:
            Connect_Des = request.POST["Input_Text"]
        except :
            Connect_Des = ''

        try:
            Connect_PhoneNumber = request.POST["Input_Phone"]
        except :
            Connect_PhoneNumber = ''

        try:
            Connect_Email = request.POST["Input_Email"]
        except :
            Connect_Email = ''
            
        try:
            Connect_Image = request.FILES["Input_Image"]
        except MultiValueDictKeyError:
            Connect_Image = ''

        if (Connect_PhoneNumber != '') or (Connect_Email != ''):

            if Connect_Image != '':
                msg = Complaint.objects.create(Title = Connect_Title, Description = Connect_Des, MobileNumber = Connect_PhoneNumber, Email = Connect_Email, Type = '0', Image = Connect_Image)
            else:
                msg = Complaint.objects.crete(Title = Connect_Title, Description = Connect_Des, MobileNumber = Connect_PhoneNumber, Email = Connect_Email, Type = '0')

            Alert.objects.create(Part = '18', FK_User = request.user, Slug = msg.id)
            
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
                'ShowAlart':True,
                'AlartMessage':'شکایت شما ثبت و بعد از بررسی کارشناسان نتیجه آن به شما گزارش داده می شود!',
                'ConnectRoad':Road,
            }

            return render(request, 'nakhll_market/pages/complaint.html', context)

        else:

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
                'ShowAlart':True,
                'AlartMessage':'برای پاسخ دهی به پیام شما، لازم است حداقل یکی از فیلد های شماره تماس یا ایمیل را پر نمایید!',
                'ConnectRoad':Road,
            }

            return render(request, 'nakhll_market/pages/complaint.html', context)
    else:

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

        
# Profile Show All Alert
def ProfileShowAllAlert(request):

    # Check User Status
    if request.user.is_authenticated :
   
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
        # ---------------------------------------------------------------
        # Get All Alert
        alert = Alert.objects.filter(Seen = True).order_by('-DateCreate')

        context = {
            'Users':user,
            'Profile':profile,
            'Wallet': wallets,
            'Options': options,
            'MenuList':navbar,
            'Alert':alert,
        }
        
        return render(request, 'nakhll_market/profile/pages/allalert.html', context)

    
    else:    
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

        context = {
            'Users':user,
            'Profile':profile,
            'Wallet': wallets,
            'Options': options,
            'MenuList':navbar,
        }
        
        return render(request, 'registration/login.html', context)
        
# ------------------------------------------------------------ Copun Sections ----------------------------------------------------

# add shop and product in coupon
def thread_add_object_to_coupon(this_coupon, shops, products):
    # check shops
    if len(shops) != 0:
        for item in shops:
            if Shop.objects.filter(ID = item).exists():
                this_coupon.FK_Shops.add(Shop.objects.get(ID = item))
    # check products
    if len(products) != 0:
        for item in products:
            if Product.objects.filter(ID = item).exists():
                this_coupon.FK_Products.add(Product.objects.get(ID = item))

# Add New Shop Copun
def AddShopCopun(request):
    # Check User Status
    if request.user.is_authenticated :
        if request.method == 'POST':
            # get data
            try:
                Copun_Title = request.POST["copun_title"]
            except :
                Copun_Title = None
            try:
                Copun_Des = request.POST["copun_des"]
            except :
                Copun_Des = None
            try:
                Copun_Serial = request.POST["copun_serial"]
            except :
                Copun_Serial = None
            Copun_Shops = request.POST.getlist("copun_shops")
            Copun_Products = request.POST.getlist("copun_products")
            try:
                Copun_SatrtDay = request.POST["Copun_SatatDay"]
            except :
                Copun_SatrtDay = None
            try:
                Copun_EndDay = request.POST["Copun_EndDay"]
            except :
                Copun_EndDay = None
            try:
                Copun_DiscountType = request.POST["Copun_DiscountType"]
            except :
                Copun_DiscountType = None
            try:
                Copun_DiscountRate = request.POST["Copun_DiscountRate"]
            except :
                Copun_DiscountRate = None
            try:
                Copun_MinimumAmount = request.POST["Copun_MinimumAmount"]
            except :
                Copun_MinimumAmount = None
            try:
                Copun_MaximumAmount = request.POST["Copun_MaximumAmount"]
            except :
                Copun_MaximumAmount = None
            try:
                Copun_NumberOfUse = request.POST["Copun_NumberOfUse"]
            except :
                Copun_NumberOfUse = None
            # set data
            if ((Copun_Title != None) and (Copun_Title != '')) and ((Copun_DiscountRate != None) and (Copun_DiscountRate != '')) and ((Copun_EndDay != None) and (Copun_EndDay != '')) and ((Copun_SatrtDay != None) and (Copun_SatrtDay != '')) and ((Copun_NumberOfUse != None) and (Copun_NumberOfUse != '')):
                if (len(Copun_Shops) != 0) or (len(Copun_Products) != 0):
                    # Discount Type Checking
                    DT = None
                    if Copun_DiscountType == 'درصدی':
                        DT = '1'
                    elif Copun_DiscountType == 'اعتباری':
                        DT = '2'
                    # create new coupon
                    if Copun_Serial != '':
                        copun = Coupon.objects.create(Title = Copun_Title, SerialNumber = Copun_Serial, FK_Creator = request.user, StartDate = Copun_SatrtDay, EndDate = Copun_EndDay, DiscountRate = Copun_DiscountRate, DiscountStatus = '1', NumberOfUse = Copun_NumberOfUse, DiscountType = DT)
                    else:
                        copun = CouponCoupon.objects.create(Title = Copun_Title, FK_Creator = request.user, StartDate = Copun_SatrtDay, EndDate = Copun_EndDay, DiscountRate = Copun_DiscountRate, DiscountStatus = '1', NumberOfUse = Copun_NumberOfUse, DiscountType = DT)
                    # Minimum Amount Cheking
                    if Copun_MinimumAmount != '':
                        copun.MinimumAmount = Copun_MinimumAmount
                        copun.save()
                    else:
                        copun.MinimumAmount = 0
                        copun.save()
                    # Maximum Amount Cheking
                    if Copun_MaximumAmount != '':
                        copun.MaximumAmount = Copun_MaximumAmount
                        copun.save()
                    else:
                        copun.MaximumAmount = 0
                        copun.save()
                    # Description Cheking
                    if (Copun_Des != None) and (Copun_Des != ''):
                        copun.Description = Copun_Des
                        copun.save()
                    # add shops and products in coupon
                    thread = threading.Thread(target = thread_add_object_to_coupon, args = (copun, Copun_Shops, Copun_Products))
                    thread.start()
                    # set alert
                    Alert.objects.create(Part = '26', FK_User = request.user, Slug = copun.id)
                    #-------------------------------------------------------------------------
                    # Get User Info
                    This_User_Info = GetUserInfo().run(request)
                    this_profile = This_User_Info["user_profiel"]
                    this_inverntory = This_User_Info["user_inverntory"]
                    # Get Menu Item
                    options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
                    # Get Nav Bar Menu Item
                    navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
                    # ----------------------------------------------------------------------
                    # get all user coupons
                    allcoupon = Coupon.objects.filter(DiscountStatus = '1', FK_Creator = request.user, Available = True)

                    context = {
                        'This_User_Profile':this_profile,
                        'This_User_Inverntory': this_inverntory,
                        'Options': options,
                        'MenuList':navbar,
                        'AllUserCupons':allcoupon,
                        'ShowAlert':True,
                        'AlartMessage':'کوپن شما ثبت شد و پس از تایید کارشناسان منتشر می گردد!',
                    }

                    return render(request, 'nakhll_market/profile/pages/allcuponlist.html', context)

                else:
                    # Get User Info
                    This_User_Info = GetUserInfo().run(request)
                    this_profile = This_User_Info["user_profiel"]
                    this_inverntory = This_User_Info["user_inverntory"]
                    # Get Menu Item
                    options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
                    # Get Nav Bar Menu Item
                    navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
                    # --------------------------------------------------------------------
                    # get all user`s shops
                    shop_list = list(Shop.objects.filter(FK_ShopManager = request.user, Available = True, Publish = True))
                    # get all user`s products
                    product_list = []
                    for item in shop_list:
                        product_list += list(item.get_products())

                    context = {
                        'This_User_Profile':this_profile,
                        'This_User_Inverntory': this_inverntory,
                        'Options': options,
                        'MenuList':navbar,
                        'Shops':shop_list,
                        'Products':product_list,
                        'ShowAlart':True,
                        'AlartMessage':'برای ایجاد کوپن حداقل یک حجره یا یک محصول باید وارد نمایید!',
                    }

                    return render(request, 'nakhll_market/profile/pages/addshopcupon.html', context)
            else:
                # Get User Info
                This_User_Info = GetUserInfo().run(request)
                this_profile = This_User_Info["user_profiel"]
                this_inverntory = This_User_Info["user_inverntory"]
                # Get Menu Item
                options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
                # Get Nav Bar Menu Item
                navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
                # --------------------------------------------------------------------
                # get all user`s shops
                shop_list = list(Shop.objects.filter(FK_ShopManager = request.user, Available = True, Publish = True))
                # get all user`s products
                product_list = []
                for item in shop_list:
                    product_list += list(item.get_products())

                context = {
                    'This_User_Profile':this_profile,
                    'This_User_Inverntory': this_inverntory,
                    'Options': options,
                    'MenuList':navbar,
                    'Shops':shop_list,
                    'Products':product_list,
                    'ShowAlart':True,
                    'AlartMessage':'مقادیر عنوان، تاریخ شروع، تاریخ انقضاء، میزان تخفیف و تعداد دفعات مجاز نمی تواند خالی باشد!',
                }

                return render(request, 'nakhll_market/profile/pages/addshopcupon.html', context)
        else:
            # Get User Info
            This_User_Info = GetUserInfo().run(request)
            this_profile = This_User_Info["user_profiel"]
            this_inverntory = This_User_Info["user_inverntory"]
            # Get Menu Item
            options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
            # Get Nav Bar Menu Item
            navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
            # --------------------------------------------------------------------
            # get all user`s shops
            shop_list = list(Shop.objects.filter(FK_ShopManager = request.user, Available = True, Publish = True))
            # get all user`s products
            product_list = []
            for item in shop_list:
                product_list += list(item.get_products())

            context = {
                'This_User_Profile':this_profile,
                'This_User_Inverntory': this_inverntory,
                'Options': options,
                'MenuList':navbar,
                'Shops':shop_list,
                'Products':product_list,
            }

            return render(request, 'nakhll_market/profile/pages/addshopcupon.html', context)    
    else:
        return redirect("nakhll_market:AccountLogin")


# Shop Copun List
def ShopCopunList(request):
    # Check User Status
    if request.user.is_authenticated :
        # Get User Info
        This_User_Info = GetUserInfo().run(request)
        this_profile = This_User_Info["user_profiel"]
        this_inverntory = This_User_Info["user_inverntory"]
        # Get Menu Item
        options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
        # Get Nav Bar Menu Item
        navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
        # ----------------------------------------------------------------------
        # get all user coupons
        allcoupon = Coupon.objects.filter(DiscountStatus = '1', FK_Creator = request.user, Available = True)

        context = {
            'This_User_Profile':this_profile,
            'This_User_Inverntory': this_inverntory,
            'Options': options,
            'MenuList':navbar,
            'AllUserCupons':allcoupon,
        }

        return render(request, 'nakhll_market/profile/pages/allcuponlist.html', context)

    else:
        return redirect("nakhll_market:AccountLogin")



# Delete Shop Copun
def DeleteShopCopun(request, id):
    # Check User Status
    if request.user.is_authenticated :
        # get this coupon
        coupon = get_object_or_404(Coupon, id = id)
        # change coupon status
        coupon.Publish = False
        coupon.save()
        # set alert
        Alert.objects.create(Part = '27', FK_User = request.user, Slug = coupon.id)
        # redirect to coupon list
        return redirect("nakhll_market:Shop_Manager_ShopCopunList")
    else:
        return redirect("nakhll_market:AccountLogin")



# Check Copun
def CheckCopun(request):
    response_data = {} 

    if request.POST.get('action') == 'post':

        try: 
            code = request.POST.get("code")
        except MultiValueDictKeyError:
            code = 'Error'
        
        try: 
            factor = request.POST.get("factor")
        except MultiValueDictKeyError:
            code = 'Error'

        if code != 'Error':

            # Get Copuns
            try:
                copun = Coupon.objects.get(SerialNumber = code, Publish = True, Available = True)
            except:
                response_data['error'] = 'کد تخفیف وارد شده معتبر نمی باشد.'
                response_data['status'] = False
                return JsonResponse(response_data)
                
            # Get Factor
            try:
                userFactor = Factor.objects.get(FactorNumber = factor)
            except:
                response_data['error'] = 'فاکتوری برای شما ثبت نشده است '
                response_data['status'] = False
                return JsonResponse(response_data)


            if copun.Publish == True:

                if copun.Available:

                    if copun.EndDate >= jdatetime.date.today():

                        if copun.FK_Users.all().count() != 0:

                            IsUser = False

                            for item in copun.FK_Users.all():

                                if item.id == request.user.id:
                                    IsUser = True

                            if IsUser:

                                if Factor.objects.filter(FK_User = request.user, Publish = True, PaymentStatus = True, FK_Coupon = copun).count() < int(copun.NumberOfUse):

                                
                                    # Build Product Class
                                    class ProductClass:
                                        def __init__(self, item, status):
                                            self.Product = item
                                            self.Status = status

                                    # Coupon Producs List
                                    Product_List = []

                                    if copun.FK_Shops.all().count() != 0:
                                        for item in copun.FK_Shops.all():
                                            for product in Product.objects.filter(Publish = True, FK_Shop = item):
                                                New = ProductClass(product, False)
                                                Product_List.append(New)

                                    if copun.FK_Products.all().count() != 0:
                                        for item in copun.FK_Products.all():
                                            New = ProductClass(item, False)
                                            Product_List.append(New)

                                    Product_List = list(dict.fromkeys(Product_List))

                                    for factor_item in userFactor.FK_FactorPost.all():    
                                        for item in Product_List:
                                            if factor_item.FK_Product.ID == item.Product.ID:
                                                item.Status = True

                                    # Chechk Coupon
                                    Check = False

                                    if len(Product_List) != 0:
                                        for item in Product_List:
                                            if item.Status == True:
                                                Check = True
                                    else:
                                        Check = True
                                    
                                    if Check:
                                        if copun.MinimumAmount != '0':

                                            if userFactor.get_total_coupon_test(copun.id) >= int(copun.MinimumAmount):

                                                if copun.MaximumAmount != '0':

                                                    if userFactor.get_total_coupon_test(copun.id) <= int(copun.MaximumAmount):

                                                        # Add Coupn To Factor
                                                        userFactor.FK_Coupon = copun
                                                        userFactor.save()

                                                        response_data['error'] = 'کد تخفیف برای شما ثبت شد، لطفا تا بارگذاری مجدد صفحه منتظر بمانید...'
                                                        response_data['status'] = True
                                                        return JsonResponse(response_data)

                                                    else:

                                                        response_data['error'] = 'خرید شما از حجره مرتبط با این کد تخفیف بیشتر از میزان تعیین شده (' + copun.MaximumAmount + 'ریال' +') می باشد.'
                                                        response_data['status'] = False
                                                        return JsonResponse(response_data)
                                                else:
    
                                                    # Add Coupn To Factor
                                                    userFactor.FK_Coupon = copun
                                                    userFactor.save()

                                                    response_data['error'] = 'کد تخفیف برای شما ثبت شد، لطفا تا بارگذاری مجدد صفحه منتظر بمانید...'
                                                    response_data['status'] = True
                                                    return JsonResponse(response_data)

                                            else:

                                                response_data['error'] = 'خرید شما از حجره مرتبط با این کد تخفیف به میزان تعیین شده (' + copun.MinimumAmount + 'ریال' +') نرسیده است.'
                                                response_data['status'] = False
                                                return JsonResponse(response_data)
                                        
                                        else:

                                            # Add Coupn To Factor
                                            userFactor.FK_Coupon = copun
                                            userFactor.save()

                                            response_data['error'] = 'کد تخفیف برای شما ثبت شد، لطفا تا بارگذاری مجدد صفحه منتظر بمانید...'
                                            response_data['status'] = True
                                            return JsonResponse(response_data)

                                    else:

                                        response_data['error'] = 'شما محصولی که شامل این کوپن باشد، ندارید!'
                                        response_data['status'] = False
                                        return JsonResponse(response_data)   

                                else:

                                    response_data['error'] = 'تعداد دفعات مجاز استفاده شما از این کد تخفیف تمام شده است!'
                                    response_data['status'] = False
                                    return JsonResponse(response_data)
                            else:

                                response_data['error'] = 'این کد تخفیف برای شما قابل استفاده نیست.'
                                response_data['status'] = False
                                return JsonResponse(response_data)

                        else:

                            if Factor.objects.filter(FK_User = request.user, Publish = True, PaymentStatus = True, FK_Coupon = copun).count() < int(copun.NumberOfUse):

                                # Build Product Class
                                class ProductClass:
                                    def __init__(self, item, status):
                                        self.Product = item
                                        self.Status = status

                                # Coupon Producs List
                                Product_List = []

                                if copun.FK_Shops.all().count() != 0:
                                    for item in copun.FK_Shops.all():
                                        for product in Product.objects.filter(Publish = True, FK_Shop = item):
                                            New = ProductClass(product, False)
                                            Product_List.append(New)

                                if copun.FK_Products.all().count() != 0:
                                    for item in copun.FK_Products.all():
                                        New = ProductClass(item, False)
                                        Product_List.append(New)

                                Product_List = list(dict.fromkeys(Product_List))

                                for factor_item in userFactor.FK_FactorPost.all():    
                                    for item in Product_List:
                                        if factor_item.FK_Product.ID == item.Product.ID:
                                            item.Status = True

                                # Chechk Coupon
                                Check = False

                                if len(Product_List) != 0:
                                    for item in Product_List:
                                        if item.Status == True:
                                            Check = True
                                else:
                                    Check = True

                                if Check:

                                    if copun.MinimumAmount != '0':
                                        if userFactor.get_total_coupon_test(copun.id) >= int(copun.MinimumAmount):

                                            if copun.MaximumAmount != '0':

                                                if userFactor.get_total_coupon_test(copun.id) <= int(copun.MaximumAmount):

                                                    # Add Coupn To Factor
                                                    userFactor.FK_Coupon = copun
                                                    userFactor.save()

                                                    response_data['error'] = 'کد تخفیف برای شما ثبت شد، لطفا تا بارگذاری مجدد صفحه منتظر بمانید...'
                                                    response_data['status'] = True
                                                    return JsonResponse(response_data)

                                                else:

                                                    response_data['error'] = 'خرید شما از حجره مرتبط با این کد تخفیف بیشتر از میزان تعیین شده (' + copun.MaximumAmount + 'ریال' +') می باشد.'
                                                    response_data['status'] = False
                                                    return JsonResponse(response_data)
                                            else:

                                                    # Add Coupn To Factor
                                                    userFactor.FK_Coupon = copun
                                                    userFactor.save()

                                                    response_data['error'] = 'کد تخفیف برای شما ثبت شد، لطفا تا بارگذاری مجدد صفحه منتظر بمانید...'
                                                    response_data['status'] = True
                                                    return JsonResponse(response_data)

                                        else:

                                            response_data['error'] = 'خرید شما از حجره مرتبط با این کد تخفیف به میزان تعیین شده (' + copun.MinimumAmount + 'ریال' +') نرسیده است.'
                                            response_data['status'] = False
                                            return JsonResponse(response_data)
                                    
                                    else:

                                        # Add Coupn To Factor
                                        userFactor.FK_Coupon = copun
                                        userFactor.save()

                                        response_data['error'] = 'کد تخفیف برای شما ثبت شد، لطفا تا بارگذاری مجدد صفحه منتظر بمانید...'
                                        response_data['status'] = True
                                        return JsonResponse(response_data)

                                
                                else:

                                    response_data['error'] = 'شما محصولی که شامل این کوپن باشد، ندارید!'
                                    response_data['status'] = False
                                    return JsonResponse(response_data)                                    

                            else:

                                response_data['error'] = 'تعداد دفعات مجاز استفاده از این کد تخفیف برای شما به پایان رسیده است.'
                                response_data['status'] = False
                                return JsonResponse(response_data)
                                
                    else:
                        response_data['error'] = 'کد تخفیف منقضی شده است.'
                        response_data['status'] = False
                        return JsonResponse(response_data)
                    
                else:
                    response_data['error'] = 'امکان استفاده از این کد تخفیف وجود ندارد.'
                    response_data['status'] = False
                    return JsonResponse(response_data)
                    
            else:
                response_data['error'] = 'امکان استفاده از این کد تخفیف وجود ندارد.'
                response_data['status'] = False
                return JsonResponse(response_data)

        else:
            response_data['error'] = 'خطای دریافت اطلاعات.'
            response_data['status'] = False
            return JsonResponse(response_data)



# ---------------------------------------------------------- End Copun Sections --------------------------------------------------

# --------------------------------------------------------- All Factor Sections --------------------------------------------------

# Show All Factor List
def ShowAllFactorList(request):

    # Check User Status
    if request.user.is_authenticated :
        # Get User Info
        This_User_Info = GetUserInfo().run(request)
        this_profile = This_User_Info["user_profiel"]
        this_inverntory = This_User_Info["user_inverntory"]
        # Get Menu Item
        options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
        # Get Nav Bar Menu Item
        navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
        #-----------------------------------------------------------------------
        # Get All Factor
        factors = Factor.objects.filter(PaymentStatus = True, Publish = True).order_by('-OrderDate')
        # get user list
        user_list = []
        for item in factors:
            user_list.append(item.FK_User)
        user_list = list(dict.fromkeys(user_list))

        context = {
            'This_User_Profile':this_profile,
            'This_User_Inverntory': this_inverntory,
            'Options': options,
            'MenuList':navbar,
            'Factors':factors,
            'User':user_list,
        }
        return render(request, 'nakhll_market/profile/pages/all_factors.html', context)
    else:
        return redirect("nakhll_market:AccountLogin")



# Show Factor Item
def ShowFactorItem(request, ID):
    # Check User Status
    if request.user.is_authenticated :
        # Get User Info
        This_User_Info = GetUserInfo().run(request)
        this_profile = This_User_Info["user_profiel"]
        this_inverntory = This_User_Info["user_inverntory"]
        # Get Menu Item
        options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
        # Get Nav Bar Menu Item
        navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
        #---------------------------------------------------------------------
        # Get This Factor
        this_factor = get_object_or_404(Factor, ID = ID)

        context = {
            'This_User_Profile':this_profile,
            'This_User_Inverntory': this_inverntory,
            'Options': options,
            'MenuList':navbar,
            'factor':this_factor,
        }
        return render(request, 'nakhll_market/profile/pages/show_factor.html', context)
    else:
        return redirect("nakhll_market:AccountLogin")


# Show Factor Item For Shop
def ShowFactorItemForShop(request, ID, status):

    # Check User Status
    if request.user.is_authenticated :
        # Get User Info
        This_User_Info = GetUserInfo().run(request)
        this_profile = This_User_Info["user_profiel"]
        this_inverntory = This_User_Info["user_inverntory"]
        # Get Menu Item
        options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
        # Get Nav Bar Menu Item
        navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
        #-----------------------------------------------------------------------
        # Get This Factor
        this_factor = get_object_or_404(Factor, ID = ID)

        context = {
            'This_User_Profile':this_profile,
            'This_User_Inverntory': this_inverntory,
            'Options': options,
            'MenuList':navbar,
            'factor':this_factor,
        }

        if status == 0:
            return render(request, 'nakhll_market/profile/pages/show_factor_wiat.html', context)
        elif status == 1:
            return render(request, 'nakhll_market/profile/pages/show_factor_send.html', context)
        else:
            return render(request, 'nakhll_market/profile/pages/show_factor_for_shoper.html', context)
    else:

        return redirect("nakhll_market:AccountLogin")



# Change Factor Checkout Status
def ChangeFactorCheckoutStatus(request, id):

    if request.user.is_authenticated :

        # Get This Factor
        this_factor = Factor.objects.get(ID = id)
        # Factor Change Checkout Status
        if this_factor.Checkout:
            this_factor.Checkout = False
            this_factor.save()
        else:
            this_factor.Checkout = True
            this_factor.FK_Staff_Checkout = request.user
            this_factor.save()

        return redirect("nakhll_market:ShowAllFactorList")

    else:

       return redirect("nakhll_market:AccountLogin")

# ------------------------------------------------------- End All Factor Sections ------------------------------------------------

# ------------------------------------------------------- Ajax Functions Sections ------------------------------------------------


# Check User Message
def CheckUserMessage(request):
    # Result
    response_data = {}
    # Message Count
    count = 0
    # Check
    if Message.objects.all().exists():
        for item in Message.objects.all():
            for It in item.FK_Users.all():
                if (It.FK_User == request.user) and (It.SeenStatus == False):
                    count += 1
        if count != 0:
            response_data['status'] = True
            response_data['count'] = count
            return JsonResponse(response_data)
        else:
            response_data['status'] = False
            response_data['count'] = 0
            return JsonResponse(response_data)
    else:
        response_data['status'] = False
        response_data['count'] = 0
        return JsonResponse(response_data)


# Change Message Status
def ChengeMessageStatus(request):
    # Result
    response_data = {}

    if request.user.is_authenticated:

        if request.POST.get('action') == 'post':

            try:
                id = request.POST["id"]
            except MultiValueDictKeyError:
                id = ''
            
            messge = Message.objects.filter(id = id)
            if messge.exists():
                last = messge[0]
                for item in last.FK_Users.all():
                    if (item.FK_User == request.user) and (item.SeenStatus == False):
                        item.SeenStatus = True
                        item.save()          
                        response_data['status'] = True
                        response_data['needload'] = True
                        return JsonResponse(response_data)
                    elif item.FK_User == request.user:
                        response_data['status'] = True
                        response_data['needload'] = False
                        return JsonResponse(response_data)
            else:
                response_data['status'] = False
                response_data['needload'] = False
                return JsonResponse(response_data)
    else:
        response_data['status'] = False
        response_data['needload'] = False
        return JsonResponse(response_data)



# Cart View To User
def CartView(request):
    # Result
    response_data = {}
    # Build Result Class
    class Result:
        def __init__(self, title, product_slug, shop_slug, image, price):
            self.Title = title
            self.Product_Slug = product_slug
            self.Shop_Slug = shop_slug
            self.Image = image
            self.Price = price
    if request.user.is_authenticated :
        Order_List = [] # Get Orders List
        Product_Count = 0 # Get Product In Cart Count
        user_factor = Factor.objects.filter(FK_User = request.user, PaymentStatus = False) # Get Users Factor
        if user_factor.exists():
            last_factor = user_factor[0] # Get Last Factor
            if last_factor.FK_FactorPost.all().count() != 0:
                Product_Count = last_factor.FK_FactorPost.all().count() # Get Product Count
                # Add Order In List
                length = 3
                for item in last_factor.FK_FactorPost.all():
                    if length != 0:
                        new = Result(item.FK_Product.Title, item.FK_Product.Slug, item.FK_Product.FK_Shop.Slug, item.FK_Product.Image, item.get_total_item_price())
                        Order_List.append(new)
                        length -= 1
                    else:
                        break
                response_data['status'] = True
                response_data['msg'] = 'محصولات خود را با کلیک روی سبد خرید مشاهده کنید.'
                response_data['count'] = Product_Count
                response_data['list'] = Order_List
                return JsonResponse(response_data)
            else:
                response_data['status'] = False
                response_data['msg'] = 'محصولی در فاکتور شما موجود نمی باشد.'
                response_data['count'] = Product_Count
                response_data['list'] = Order_List
                return JsonResponse(response_data)
        else:
            response_data['status'] = False
            response_data['msg'] = 'فاکتوری برای شما وجود ندارد.'
            response_data['count'] = Product_Count
            response_data['list'] = Order_List
            return JsonResponse(response_data)
    else:
        response_data['status'] = False
        response_data['msg'] = 'لظفا وارد حساب کاربری خود شوید.'
        response_data['count'] = Product_Count
        response_data['list'] = Order_List
        return JsonResponse(response_data)

# ----------------------------------------------------- End Ajax Functions Sections ------------------------------------------------



# ------------------------------------------------------------ Campaign Sections ---------------------------------------------------

# Manage Campaign List
def ManageCampaignList(request):

    # Check User Status
    if request.user.is_authenticated :

        #Get User Info
        user = User.objects.all()
        # Get User Profile
        profile = Profile.objects.all()
        # Get Wallet Inverntory
        wallets = Wallet.objects.all()
        # Get Menu Item
        options = Option_Meta.objects.filter(Title='index_page_menu_items')
        # Get Nav Bar Menu Item
        navbar = Option_Meta.objects.filter(Title='nav_menu_items')
        #-----------------------------------------------------------------------
        # Get All User Copuns
        allusercampaign = Campaign.objects.filter(DiscountStatus = '0', Available = True, Publish = True)

        context = {
            'Users':user,
            'Profile':profile,
            'Wallet': wallets,
            'Options': options,
            'MenuList':navbar,
            'AllUserCupons':allusercopun,
            'ShowAlart':False,
        }

        return render(request, 'nakhll_market/profile/pages/managecampaignlist.html', context)

    else:

        #Get User Info
        user = User.objects.all()
        # Get User Profile
        profile = Profile.objects.all()
        # Get Wallet Inverntory
        wallets = Wallet.objects.all()
        # Get Menu Item
        options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
        # Get Nav Bar Menu Item
        navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')

        context = {
            'Users':user,
            'Profile':profile,
            'Wallet': wallets,
            'Options': options,
            'MenuList':navbar,
        }
        
        return render(request, 'registration/login.html', context)

# ---------------------------------------------------------- End Campaign Sections --------------------------------------------------



# --------------------------------------------------------- Message Filter Sections ------------------------------------------------

# Message Filter
def MessageFilter(request):
    if request.user.is_authenticated :
        if request.method == 'POST':
            # Get All Message
            User_Message_List = []
            # Get Status
            set_status = '0'
            S_Date = None
            E_Date = None
            # Build Message Class
            class MessageClass:
                def __init__(self, item, status):
                    self.Message = item
                    self.Status = status
        
            try:
                StartDate = request.POST["filter_start"]
            except:
                StartDate = ''

            try:
                EndDate = request.POST["filter_end"]
            except:
                EndDate = ''

            try:
                Status = request.POST["status"]
            except:
                Status = ''

            if (((StartDate != '') and (EndDate != '')) or (Status != '')):
                if (StartDate != '') and (EndDate != ''):
                    Start = StartDate.split('-')
                    End = EndDate.split('-')
                    JStart = jdatetime.date(int(Start[0]), int(Start[1]), int(Start[2]))
                    JEnd = jdatetime.date(int(End[0]), int(End[1]), int(End[2]))
                    GStart = jdatetime.JalaliToGregorian(JStart.year, JStart.month, JStart.day)
                    GEnd = jdatetime.JalaliToGregorian(JEnd.year, JEnd.month, JEnd.day)
                    Str_GStart = "%d-%d-%d" % (GStart.gyear, GStart.gmonth, GStart.gday)
                    Str_GEnd = "%d-%d-%d" % (GEnd.gyear, GEnd.gmonth, GEnd.gday)
                    messages = Message.objects.filter(Type = True, Date__range = [Str_GStart, Str_GEnd])
                    for msg_item in messages:
                        for item in msg_item.FK_Users.all():
                            if item.FK_User == request.user:
                                if Status == '1':
                                    if item.SeenStatus == False:
                                        new = MessageClass(msg_item, item.SeenStatus)
                                        User_Message_List.append(new)
                                elif Status == '2':
                                    if item.SeenStatus == True:
                                        new = MessageClass(msg_item, item.SeenStatus)
                                        User_Message_List.append(new)
                                else:
                                    new = MessageClass(msg_item, item.SeenStatus)
                                    User_Message_List.append(new)
                else:
                    messages = Message.objects.filter(Type = True)
                    for msg_item in messages:
                        for item in msg_item.FK_Users.all():
                            if item.FK_User == request.user:
                                if Status == '1':
                                    if item.SeenStatus == False:
                                        new = MessageClass(msg_item, item.SeenStatus)
                                        User_Message_List.append(new)
                                elif Status == '2':
                                    if item.SeenStatus == True:
                                        new = MessageClass(msg_item, item.SeenStatus)
                                        User_Message_List.append(new)
                                else:
                                    new = MessageClass(msg_item, item.SeenStatus)
                                    User_Message_List.append(new)
                S_Date = StartDate
                E_Date = EndDate
                set_status = Status
            else:
                return redirect("nakhll_market:Message")

        # ----------------------------------------------------------------------
            # Get User Info
            This_User_Info = GetUserInfo().run(request)
            this_profile = This_User_Info["user_profiel"]
            this_inverntory = This_User_Info["user_inverntory"]
            # Get Menu Item
            options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
            # Get Nav Bar Menu Item
            navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
            
            context = {
                'This_User_Profile':this_profile,
                'This_User_Inverntory': this_inverntory,
                'Options': options,
                'MenuList':navbar,
                'Messages':User_Message_List,
                'Status':set_status,
                'Start':S_Date,
                'End':E_Date,
            }

            return render(request, 'nakhll_market/profile/pages/message.html', context)

    else:

        return redirect("nakhll_market:AccountLogin")

# --------------------------------------------------------------- End Sections ------------------------------------------------------


# ------------------------------------------------------ Manage Factor Filter Sections -----------------------------------------------

# Manage Factor Filter
def ManageFactorFilter(request):
    if request.user.is_authenticated :
        if request.method == 'POST':
            # Get Status
            set_status = '6'
            set_checkout = '0'
            S_Date = None
            E_Date = None
            customer = '000'

            try:
                StartDate = request.POST["date_start"]
            except:
                StartDate = ''

            try:
                EndDate = request.POST["date_end"]
            except:
                EndDate = ''

            try:
                Status = request.POST["status"]
            except:
                Status = ''

            try:
                Check_Out = request.POST["check_out"]
            except:
                Check_Out = ''

            try:
                Customer = request.POST["customer_name"]
            except:
                Customer = ''

            if (((StartDate != '') and (EndDate != '')) or (Status != '') or (Check_Out != '') or (Customer != '')):
                factors = Factor.objects.filter(PaymentStatus = True, Publish = True).order_by('-OrderDate')
                if (StartDate != '') and (EndDate != ''):
                    Start = StartDate.split('-')
                    End = EndDate.split('-')
                    JStart = jdatetime.date(int(Start[0]), int(Start[1]), int(Start[2]))
                    JEnd = jdatetime.date(int(End[0]), int(End[1]), int(End[2]))
                    GStart = jdatetime.JalaliToGregorian(JStart.year, JStart.month, JStart.day)
                    GEnd = jdatetime.JalaliToGregorian(JEnd.year, JEnd.month, JEnd.day)
                    Str_GStart = "%d-%d-%d" % (GStart.gyear, GStart.gmonth, GStart.gday)
                    Str_GEnd = "%d-%d-%d" % (GEnd.gyear, GEnd.gmonth, GEnd.gday)
                    factors = factors.filter(OrderDate__range = [Str_GStart, Str_GEnd])
                    S_Date = StartDate
                    E_Date = EndDate
                # get user list
                user_list = []
                for item in factors:
                    user_list.append(item.FK_User)
                user_list = list(dict.fromkeys(user_list))

                if Status != '6':
                    factors = factors.filter(OrderStatus = Status)
                    set_status = Status
                if Check_Out != '0':
                    if Check_Out == '1':
                        factors = factors.filter(Checkout = False)
                        set_checkout = Check_Out
                    elif Check_Out == '2':
                        factors = factors.filter(Checkout = True)
                        set_checkout = Check_Out
                if Customer != '000':
                    factors = factors.filter(FK_User = User.objects.get(id = Customer))
                    customer = User.objects.get(id = Customer).username
            else:
                return redirect("nakhll_market:ShowAllFactorList")
            # ----------------------------------------------------------------------
            # Get User Info
            This_User_Info = GetUserInfo().run(request)
            this_profile = This_User_Info["user_profiel"]
            this_inverntory = This_User_Info["user_inverntory"]
            # Get Menu Item
            options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
            # Get Nav Bar Menu Item
            navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
            
            context = {
                'This_User_Profile':this_profile,
                'This_User_Inverntory': this_inverntory,
                'Options': options,
                'MenuList':navbar,
                'Factors':factors,
                'User':user_list,
                'Status':set_status,
                'Start':S_Date,
                'End':E_Date,
                'CheckOut':set_checkout,
                'Customer':customer,
            }

            return render(request, 'nakhll_market/profile/pages/all_factors.html', context)
        else:
            return redirect("nakhll_market:ShowAllFactorList")
    else:
        return redirect("nakhll_market:AccountLogin")

# --------------------------------------------------------------- End Sections ------------------------------------------------------



# ------------------------------------------------------ Manage Factor Filter Sections -----------------------------------------------

# Alert Filter
def AlertFilter(request):
    if request.user.is_authenticated :
        if request.method == 'POST':
            # Get Status
            set_checkout = '0'
            S_Date = None
            E_Date = None
            customer = '000'

            try:
                StartDate = request.POST["date_start"]
            except:
                StartDate = ''

            try:
                EndDate = request.POST["date_end"]
            except:
                EndDate = ''

            try:
                Check_Out = request.POST["check_out"]
            except:
                Check_Out = ''

            try:
                Customer = request.POST["customer_name"]
            except:
                Customer = ''

            if (((StartDate != '') and (EndDate != '')) or (Check_Out != '') or (Customer != '')):
                alerts = Alert.objects.filter(Seen = False).order_by('-DateCreate')
                if (StartDate != '') and (EndDate != ''):
                    Start = StartDate.split('-')
                    End = EndDate.split('-')
                    JStart = jdatetime.date(int(Start[0]), int(Start[1]), int(Start[2]))
                    JEnd = jdatetime.date(int(End[0]), int(End[1]), int(End[2]))
                    GStart = jdatetime.JalaliToGregorian(JStart.year, JStart.month, JStart.day)
                    GEnd = jdatetime.JalaliToGregorian(JEnd.year, JEnd.month, JEnd.day)
                    Str_GStart = "%d-%d-%d" % (GStart.gyear, GStart.gmonth, GStart.gday)
                    Str_GEnd = "%d-%d-%d" % (GEnd.gyear, GEnd.gmonth, GEnd.gday)
                    alerts = alerts.filter(DateCreate__range = [Str_GStart, Str_GEnd])
                    S_Date = StartDate
                    E_Date = EndDate
                # get user list
                user_list = []
                for item in alerts:
                    user_list.append(item.FK_User)
                user_list = list(dict.fromkeys(user_list))
                if Check_Out != '000':
                    alerts = alerts.filter(Part = Check_Out)
                    set_checkout = Check_Out
                if Customer != '000':
                    alerts = alerts.filter(FK_User = User.objects.get(id = Customer))
                    customer = User.objects.get(id = Customer).username
            else:
                return redirect("nakhll_market:Alert")
            # ----------------------------------------------------------------------
            # Get User Info
            This_User_Info = GetUserInfo().run(request)
            this_profile = This_User_Info["user_profiel"]
            this_inverntory = This_User_Info["user_inverntory"]
            # Get Menu Item
            options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
            # Get Nav Bar Menu Item
            navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
            
            context = {
                'This_User_Profile':this_profile,
                'This_User_Inverntory': this_inverntory,
                'Options': options,
                'MenuList':navbar,
                'Alert':alerts,
                'User':user_list,
                'Start':S_Date,
                'End':E_Date,
                'CheckOut':set_checkout,
                'Customer':customer,
            }

            return render(request, 'nakhll_market/profile/pages/alert.html', context)
        else:
            return redirect("nakhll_market:Alert")
    else:
        return redirect("nakhll_market:AccountLogin")

# --------------------------------------------------------------- End Sections ------------------------------------------------------



# ------------------------------------------------------------- Erroe Sections ------------------------------------------------------
# Error 500
def error_500(request, error_text):

    context = {
        'error':error_text,
    }

    return render(request, '500.html', context)
# --------------------------------------------------------------- End Sections ------------------------------------------------------