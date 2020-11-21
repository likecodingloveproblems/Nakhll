from django.shortcuts import render_to_response
from django.contrib.sessions.backends.db import SessionStore
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.conf import settings
from django.urls import reverse
from django.views import generic
from ipware import get_client_ip
from datetime import datetime, date, timedelta
import jdatetime
from django.contrib import messages
from django.utils.datastructures import MultiValueDictKeyError
from django import template
from itertools import chain
from operator import attrgetter
import random, string, os
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from unidecode import unidecode
from kavenegar import *
import threading
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.conf import settings


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
from .models import Message
from .models import Option_Meta
from .models import Pages
from .models import Newsletters
from .models import Alert
from .models import Field, UserphoneValid
from .models import Note
from .models import PageViews, User_View, ShopViews, Date_View

from Payment.models import Wallet, Factor ,FactorPost, Coupon
from blog.models import CategoryBlog, PostBlog, VendorStory

from .forms import Login, CheckEmail
from .profileviews import ProfileDashbord

# Get Username
User_username = None

# Forget Password Code
fogetpasswordcode = None

# Rigister Code
register = None

# phonenumber Offline
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

# Login To User Panel
def accountlogin(request):
    return render(request, 'registration/login.html')

def login_to_account(request):
    response_data = {}
    try:
        mobile = request.POST.get("mobilenumber")
        password = request.POST.get("password")
        remember_me = request.POST.get("remember_me")
        # set status
        if remember_me == '1':
            status = True
        else:
            status = False
        # get user with mobile nubmer
        this_profile = Profile.objects.get(MobileNumber = mobile)
        # check user
        user = authenticate(request, username = this_profile.FK_User.username, password = password)
        # get next page
        next_page = settings.LOGIN
        if 'next' in request.session:
            next_page = request.session['next']
        if user is not None:
            # login user
            login(request, user)
            if status:
                session_key = request.session.session_key or Session.objects.get_new_session_key()
                Session.objects.save(session_key, request.session._session, timezone.now() + timedelta(seconds = settings.SESSION_COOKIE_AGE))
            response_data['status'] = True
            response_data['message'] = '200'
            response_data['next'] = next_page
            return JsonResponse(response_data)
        else:
            response_data['status'] = True
            response_data['message'] = '400'
            return JsonResponse(response_data)
    except Exception as e:
        response_data['status'] = False
        response_data['message'] = str(e)
        return JsonResponse(response_data)

# Logout To User Panel
def logout(request):
    return HttpResponseRedirect(reverse(index))

# Register User
def Register(request):

    response_data={}

    if request.POST.get('action') == 'post':

        try:
            FirstName = request.POST["firstname"]
        except MultiValueDictKeyError:
            FirstName = ''

        try:
            LastName = request.POST["lastname"]
        except MultiValueDictKeyError:
            LastName = ''

        try:
            NactionCode = request.POST["nactioncode"]
        except MultiValueDictKeyError:
            NactionCode = ''

        try:
            MobileNumber = request.POST["mobilenumber"]
        except MultiValueDictKeyError:
            MobileNumber = ''
 
        try:
            Email = request.POST["email"]
        except MultiValueDictKeyError:
            Email = ''

        try:
            UserName = request.POST["username"]
        except MultiValueDictKeyError:
            UserName = ''
         
        try:
            Password = request.POST["password"]
        except MultiValueDictKeyError:
            Password = ''

        try:
            newpassword = request.POST["newpassword"]
        except MultiValueDictKeyError:
            newpassword = ''


        try:
            referencecode = request.POST["referencecode"]
        except MultiValueDictKeyError:
            referencecode = ''


        if (UserName != '') and (Password != '') and (FirstName != '') and (LastName != '') and (NactionCode != '') and (MobileNumber != '') and (Email != '') and (newpassword != ''):

            if len(NactionCode) == 10 :
                if (NactionCode == '0000000000') or (NactionCode == '1111111111') or (NactionCode == '2222222222') or (NactionCode == '3333333333') or (NactionCode == '4444444444') or (NactionCode == '5555555555') or (NactionCode == '6666666666') or (NactionCode == '7777777777') or (NactionCode == '8888888888') or (NactionCode == '9999999999') :
                    response_data['error'] = 'کد ملی وارد شده صحیح نمی باشد'
                    response_data['status'] = False
                else:
                    if (Password == newpassword) :

                        user = User.objects.filter(username = UserName, email = Email)
                        pro = Profile.objects.filter(MobileNumber = MobileNumber)
                        thispro = Profile.objects.filter(NationalCode = NactionCode)

                        if (user.count() != 0) or (pro.count() != 0) or (thispro.count() != 0):

                            response_data['error'] = 'کاربری با این مشخصات موجود است!'
                            response_data['status'] = False

                            return JsonResponse(response_data)

                        else:

                            try:
                                
                                this = User.objects.create_user(UserName, Email, Password)
                                this.last_name = LastName
                                this.first_name = FirstName
                                this.save()
                                

                                thispro = Profile(FK_User = this, MobileNumber = MobileNumber, NationalCode = NactionCode, IPAddress = visitor_ip_address(request), ReferenceCode =  referencecode)
                                thispro.save()

                                thiswallet = Wallet(FK_User = this)
                                thiswallet.save()


                                response_data['error'] = 'ثبت نام با موفقیت انجام شد'
                                response_data['status'] = True
                                return JsonResponse(response_data)

                            except:

                                response_data['error'] = 'کاربری با این مشخصات موجود است - رمز عبور شما طبق الگو های خواسته شده نمی باشد!'
                                response_data['status'] = False

                                return JsonResponse(response_data)
                    else:       
                        response_data['error'] = 'رمز عبور و تکرار رمز عبور برابر یکسان نیستند'
                        response_data['status'] = False
                        return JsonResponse(response_data)
            else:
                response_data['error'] = 'کد ملی بایدس ده رقم باشد'
                response_data['status'] = False
                return JsonResponse(response_data)

            #     else:
            # #         c = int(NactionCode[9])
            # #         n = int(NactionCode[0]) * 10 +
            # #             int(NactionCode[1]) * 9 +
            # #             int(NactionCode[2]) * 8 +
            # #             int(NactionCode[3]) * 7 +
            # #             int(NactionCode[4]) * 6 +
            # #             int(NactionCode[5]) * 5 +
            # #             int(NactionCode[6]) * 4 +
            # #             int(NactionCode[7]) * 3 +
            # #             int(NactionCode[8]) * 2 
            # #         r = n - int(n / 11) * 11;
            # #         if ((r == 0) and (r == c)) or ((r == 1) and (c == 1)) or ((r > 1) and (c == 11 - r)):
            #         ncode = true
            # #         else:
            # #             response_data['error'] = 'کد ملی وارد شده صحیح نمی باشد'
            # #             response_data['status'] = False
            # else:
            #     response_data['error'] = 'کد ملی وارد شده صحیح نمی باشد'
            #     response_data['status'] = False

                    
            
        else:

            response_data['error'] = 'لطفا تمامی فیلد ها را به درستی پر کنید!'
            response_data['status'] = False
            return JsonResponse(response_data)
        
    else:
        context = {
        }
        return render (request, 'registration/register.html', context)
# Show Change Password Page
def ShowChangePassword(request):    

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

        context = {
            'Users':user,
            'Profile':profile,
            'Wallet': wallets,
            'Options': options,
            'MenuList':navbar,
            'ShowAlart':False,
            'AlartMessage':'',
        }

        return render(request, 'registration/forgetpassword/changepassword.html', context)
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



# Change Password
def ChangePassword(request):   
    # Check User Status
    if request.user.is_authenticated :

        if request.method == 'POST':

            try:
                password = request.POST["password"]
            except MultiValueDictKeyError:
                password = False
            
            try:
                newpassword = request.POST["newpassword"]
            except MultiValueDictKeyError:
                newpassword = False

            thisuser = request.user

            if (password != False) and (newpassword != False):

                if (password == newpassword):

                    if (newpassword != thisuser.username):

                        try:
                            thisuser.set_password(newpassword)
                            thisuser.save()
                            
                            message = 'رمز عبور شما با موفقیت تغییر کرد!'
                            showalert = True
                        except:
                            showalert = True
                            message = 'عبارت وارد شده باید طبق الگو ها باشد!'

                            context = {
                                'ShowAlart':showalert,
                                'AlartMessage':message,
                            }

                            return redirect('registration/forgetpassword/changepassword.html', context)

                    else:
                        showalert = True
                        message = 'مقادیر وارد شده نباید مشابه بقیه اطلاعات شما باشد!'

                        context = {
                            'ShowAlart':showalert,
                            'AlartMessage':message,
                        }

                        return redirect('registration/forgetpassword/changepassword.html', context)

                else:
                    showalert = True
                    message = 'مقادیر وارد شده با یک دیگر برابر نیستند!'

                    context = {
                        'ShowAlart':showalert,
                        'AlartMessage':message,
                    }

                    return redirect('registration/forgetpassword/changepassword.html', context)
                
            else:
                showalert = True
                message = 'لطفا تمامی فیلد های خواسته شده را پر کنید!'

                context = {
                    'ShowAlart':showalert,
                    'AlartMessage':message,
                }

                return redirect('registration/forgetpassword/changepassword.html', context)

            context = {
                'ShowAlart':showalert,
                'AlartMessage':message,
            }

            return redirect(request, 'registration/login.html', context)

        else:
            context = {
                'ShowAlart':False,
                'AlartMessage':'',
            }

            return redirect('registration/forgetpassword/changepassword.html', context)

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
            'ShowAlart':False,
        }
        
        return render(request, 'registration/login.html', context)

# Show Get Phone Number Page
def ShowGetPhoneNumber(request):    

    context = {
        'ShowAlart':False,
        'AlartMessage':'',
    }

    return render(request, 'registration/forgetpassword/getphonenumber.html', context)

    # Show Get Phone Number Page
def ShowChangePasswordOff(request):    

    context = {
        'ShowAlart':False,
        'AlartMessage':'',
    }

    return render(request, 'registration/forgetpassword/changepass.html', context)

# Get Registeri Code
def GetRegisteriCode(request):
    response_data = {} 

    if request.POST.get('action') == 'post':

        try: 
            phonenumber = request.POST.get("mobilenumber")
        except MultiValueDictKeyError:
            phonenumber = '00'

        if (phonenumber != '00'):

            if (Profile.objects.filter(MobileNumber = phonenumber).count() == 0):
                regcode = ''.join( random.choice(string.digits) for i in range(6))
                if (UserphoneValid.objects.filter(MobileNumber = phonenumber).count() == 0):
                    userphoneValid = UserphoneValid(MobileNumber=phonenumber,ValidCode=regcode,Validation=False)
                    userphoneValid.save() 
                try:
                    userphoneValid=UserphoneValid.objects.get(MobileNumber = phonenumber)
                    userphoneValid.ValidCode = regcode
                    userphoneValid.Validation = False
                    userphoneValid.save()
                except:
                    response_data['error'] = 'خطای دریافت شماره تماس'
                    response_data['status'] = False
                    return JsonResponse(response_data)

                url = 'https://api.kavenegar.com/v1/4E41676D4B514A4143744C354E6135314E4F47686B33594B747938794D30426A784A692F3579596F3767773D/verify/lookup.json' 
                params = {'receptor': phonenumber, 'token' : regcode, 'template' : 'nakhl-register'}
                requests.post(url, params = params)

                response_data['message'] = 'با موفقیت انجام شد'
                response_data['status'] = True
                return JsonResponse(response_data)
            else:
                response_data['error'] = 'این کاربر قبلا ثبت نام کرده است ! '
                response_data['status'] = False
                return JsonResponse(response_data)

        else:

            response_data['error'] = 'شماره وارد شده نامعتبر است!'
            response_data['status'] = False
    else:
        context = {
            'ShowAlart':False,
            'AlartMessage':'',
        }

        return render(request, 'registration/register.html', context)



# Get Code
def GetCode(request):

    response_data = {} 

    if request.POST.get('action') == 'post':

        try:
            phonenumber = request.POST.get("mobilenumber")
        except MultiValueDictKeyError:
            phonenumber = False

        if (phonenumber != False):

            if (Profile.objects.filter(MobileNumber = phonenumber).count() != 0):
                fogetpasswordcode = ''.join( random.choice(string.digits) for i in range(6))
                if (UserphoneValid.objects.filter(MobileNumber = phonenumber).count() == 0):
                    userphoneValid = UserphoneValid(MobileNumber=phonenumber,ValidCode=fogetpasswordcode,Validation=False)
                    userphoneValid.save()
                else:    
                    try:
                        userphoneValid=UserphoneValid.objects.get(MobileNumber = phonenumber)
                        userphoneValid.ValidCode = fogetpasswordcode
                        userphoneValid.Validation = False
                        userphoneValid.save()
                    except:
                        response_data['error'] = 'خطای دریافت شماره تماس'
                        response_data['status'] = False
                        return JsonResponse(response_data)

                url = 'https://api.kavenegar.com/v1/4E41676D4B514A4143744C354E6135314E4F47686B33594B747938794D30426A784A692F3579596F3767773D/verify/lookup.json' 
                params = {'receptor': phonenumber, 'token' : fogetpasswordcode, 'template' : 'nakhl-forgetpassword'}
                requests.post(url, params = params)

                response_data['message'] = 'با موفقیت انجام شد'
                response_data['status'] = True
                return JsonResponse(response_data)
            else:

                response_data['error'] = 'کاربری با این شماره موبایل ثبت نام نکرده است ! '
                response_data['status'] = False

                return JsonResponse(response_data)

        else:

            response_data['error'] = 'شماره وارد شده نامعتبر است!'
            response_data['status'] = False
    else:
        context = {
            'ShowAlart':False,
            'AlartMessage':'',
        }

        return render(request, 'registration/forgetpassword/getphonenumber.html', context)



def codesetvalid(request):
    response_data = {} 
    if request.POST.get('action') == 'post':
        try:
            phonenumber = request.POST.get("mobilenumber")
            codeinputuser = request.POST.get("code")
        except MultiValueDictKeyError:
            response_data['status'] = False
            response_data['error'] = 'خطا ! لطفا مجدد امتحان کنید!'
            return JsonResponse(response_data)

        if (UserphoneValid.objects.get(MobileNumber = phonenumber).ValidCode == codeinputuser):
            userphoneValid=UserphoneValid.objects.get(MobileNumber = phonenumber)
            userphoneValid.Validation = True
            userphoneValid.save()
            response_data['status'] = True
            return JsonResponse(response_data)
        else:
            response_data['error'] = 'کد وارد شده نا معتبر می باشد '
            response_data['status'] = False
        return JsonResponse(response_data)
    else:
        context = {
            'ShowAlart':False,
            'AlartMessage':'',
        }
        return render(request, 'registration/forgetpassword/getphonenumber.html', context)

        
        
        

    
# ChangePasswordOffline
def ChangePasswordOffline(request): 
 
    response_data = {}
    
    if request.method == 'POST':

        try:
            password = request.POST["password"]
        except MultiValueDictKeyError:
            password = False
        
        try:
            newpassword = request.POST["newpassword"]
        except MultiValueDictKeyError:
            newpassword = False

        try:
            mobile = request.POST["mobilenumber"]
        except MultiValueDictKeyError:
            mobile = False

        if (UserphoneValid.objects.get(MobileNumber = mobile).Validation == True):
            if (password != False) and (newpassword != False) and (mobile != False):

                if (password == newpassword):
                    thispro = Profile.objects.get(MobileNumber = mobile)
                    thisuser = User.objects.get(id = thispro.FK_User_id)

                    if (newpassword != thisuser.username):

                        try:                       
                            thisuser.set_password(newpassword)
                            thisuser.save()
                            response_data['status'] = True
                            response_data['message'] = 'با موفقیت انجام شد .. '
                            return JsonResponse(response_data)
                        except:
                            response_data['error'] = 'رمز عبور شما نمی تواند از عبارات معروف باشد!'
                            response_data['status'] = False

                            return JsonResponse(response_data)

                    else:
                        response_data['error'] = 'مقادیر وارد شده نباید مشابه بقیه اطلاعات شما باشد!'
                        response_data['status'] = False

                        return JsonResponse(response_data)

                else:

                    response_data['error'] = 'مقادیر وارد شده با یک دیگر برابر نیستند!'
                    response_data['status'] = False

                    return JsonResponse(response_data)
                
            else:

                response_data['error'] = 'تمامی فیلد ها ارا تکمیل کنید'
                response_data['status'] = False

                return JsonResponse(response_data)
        else:
            response_data['message'] = 'خطای اعتبار سنجی'
            response_data['status'] = False
            return JsonResponse(response_data)
    else:

        context = {
        }
        
        return render (request, 'registration/forgetpassword/getphonenumber.html', context)
  

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



# Get Random Categories
class RandomCategories(threading.Thread):
    def run(self):
        # Get All Categories
        all_cat = []
        for item in Category.objects.filter(Publish = True, Available = True, FK_SubCategory = None):
            all_cat.append(item)
        # Get Random Category For 12 Round
        final_category = []
        count = 12
        while (count != 0) and (len(all_cat) != 0):
            random_cat = random.randint(0, len(all_cat))
            if random_cat == len(all_cat):
                
                final_category.append(all_cat[random_cat - 1])
            else:

                final_category.append(all_cat[random_cat])

            for obj in final_category:
                if obj in all_cat:
                    all_cat.remove(obj)
            count -= 1

        return final_category



# Get Random Shops
class RandomShops(threading.Thread):
    def run(self):
        # Get All Shops
        all_shop = []
        for item in Shop.objects.filter(Publish = True, Available = True):
            all_shop.append(item)
        # Get Random Shop For 12 Round
        final_shop = []
        count = 12
        while (count != 0) and (len(all_shop) != 0):
            random_item = random.randint(0, len(all_shop))
            if random_item == len(all_shop):
                
                final_shop.append(all_shop[random_item - 1])
            else:

                final_shop.append(all_shop[random_item])

            for obj in final_shop:
                if obj in all_shop:
                    all_shop.remove(obj)
            count -= 1

        return final_shop



# Get Random Discounted Product List
class DiscountedProductList(threading.Thread):
    def run(self):
        dis_product = []
        for item in Product.objects.filter(Publish = True, Available = True, Status__in = ['1', '2', '3']).order_by('-DateCreate'):
            if item.OldPrice != '0':
                dis_product.append(item)

        dis_product = dis_product[:16]
        return dis_product



# Get Random Discounted Product
class RandomDiscountedProduct(threading.Thread):
    def run(self):
        # Get All Discounted Product
        dis_product = []
        for item in Product.objects.filter(Publish = True, Available = True, Status__in = ['1', '2', '3']):
            if item.OldPrice != '0':
                dis_product.append(item)
        # Get Random Product
        random_product = random.randint(0, len(dis_product))
        if random_product == len(dis_product):
            return dis_product[random_product - 1]
        else:
            return dis_product[random_product]


class SuggestedProducts(threading.Thread):
    def run(self):
        FinalList = []
        ProductList = []
        # Get Random Product
        for item in Shop.objects.filter(Publish = True, Available = True):
            if Product.objects.filter(FK_Shop = item, Publish = True, Available = True, OldPrice = '0', Status__in = ['1', '2', '3']).count() != 0:
                for product in Product.objects.filter(FK_Shop = item, Publish = True, Available = True, OldPrice = '0', Status__in = ['1', '2', '3']):
                    ProductList.append(product)
                # Get Random
                random_index = random.randint(0, len(ProductList))
                if random_index == len(ProductList):
                    FinalList.append(ProductList[(len(ProductList) - 1)])
                else:
                    FinalList.append(ProductList[random_index])
                ProductList.clear()
                

        FinalList = FinalList[:16]

        return FinalList


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


class GetBlog(threading.Thread):
    def run(self):
        # Get 4 Blog For Index
        blog = []
        class Blog:
            def __init__(self, item, writer):
                self.Blog = item
                self.Writer = writer
        # Built New Object
        for item in PostBlog.objects.filter(Publish = True).order_by('-DateCreate')[:4]:
            new = Blog(item, Profile.objects.get(FK_User = item.FK_User))
            blog.append(new)
        return blog
    
def index(request):
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
    # ------------------------------------------------------------------------
    # Get All Products
    pubproduct = Product.objects.filter(Publish = True, Available = True, OldPrice = '0', Status__in = ['1', '2', '3']).order_by('-DateCreate')[:12]
    pubproductold = SuggestedProducts().run()
    # Get All Discounted Product
    dis_product = DiscountedProductList().run()
    # Get Index Sliders
    pubsliders = Slider.objects.filter(Location = 1, Publish = True)
    # Get All Categories
    categories = RandomCategories().run()
    # Get All Index Advertising - Buttom
    pubbuttomadvsliders = Slider.objects.filter(Location = 2, Publish = True)
    # Get All Index Advertising - Center
    pubcenteradvsliders = Slider.objects.filter(Location = 3, Publish = True)
    postblog = GetBlog().run()
    vendorstory = VendorStory.objects.filter(Publish = True).order_by('-DateCreate')[:2]
    catblog = CategoryBlog.objects.filter(Publish = True)
    # Get All Shops
    pubshops = RandomShops().run()
    # Build Discounted Product Class
    class DisPro:
        def __init__(self, Product, Shop):
            self.UserShop = Shop
            self.UserProduct = Product
    # Discounted Product
    disprods = RandomDiscountedProduct().run()
    try:   
        disprod = Product.objects.get(Slug = disprods.Slug)
        disprod_shop = Shop.objects.get(ID = disprod.FK_Shop.ID)

        discounted_product = DisPro(disprod, disprod_shop)
    except:
        discounted_product = False

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
        'Postblog':postblog,
        'Vendorstory':vendorstory,
        'Catblog':catblog,
        'AllDisProduct':dis_product,
    }

    return render(request, 'nakhll_market/pages/index.html', context)


# set session
def set_session(request):
    response_data = {}
    if 'next' in request.session:
        print('123456')
    try:
        this_path = request.POST['this_path']
        # get path other than non-account path
        if not ((this_path == '/login/') or (this_path == '/account/logout/') or (this_path == '/account/register/')):
            request.session['next'] = this_path
        response_data['status'] = True
        return JsonResponse(response_data)
    except Exception as e:
        response_data['status'] = False
        response_data['message'] = str(e)
        return JsonResponse(response_data)


# get shop category
class get_shop_other_info(threading.Thread):
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
        # --------------------------------------------------------------------------------
        if VendorStory.objects.filter(FK_Shop = shop, Publish = True).exists():
            this_shop_story =  VendorStory.objects.filter(FK_Shop = shop, Publish = True)[0]
        else:
            this_shop_story =  None
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
            "this_shop_story":this_shop_story,
            # "total_sell":total_sell,
            "view":shop_view,
        }
        return result

# Get All Markets
def market(request):
    # Get User Info
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
    # Get This Shop Story
    this_shop_story = other_info["this_shop_story"]
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
        'This_Shop_Story':this_shop_story,
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
            for this in Category.objects.filter(Publish = True, FK_SubCategory = item):
                if str(this.id) in category_list_id:
                    this_sub.append(Sub_Item(this, True))
                else:
                    this_sub.append(Sub_Item(this, False))

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
class Product_Total_Sell(threading.Thread):
    def run(self, product):
        # Total Sell
        total_sell = 0
        # Get All Factor Item Is Product = This Product
        sell_list = FactorPost.objects.filter(FK_Product = product, ProductStatus__in = ['2', '3'])
        for item in sell_list:
            total_sell += item.ProductCount
        return total_sell


# Get Related products
class get_related_products(threading.Thread):
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
    }

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

        try:
            words = request.POST["search"]
            words = words.split(' ')
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
        # ----------------------------------------------------------------
        # Get User Info
        if request.user.is_authenticated:
            This_User_Info = GetUserInfo().run(request)
            this_profile = This_User_Info["user_profiel"]
            this_inverntory = This_User_Info["user_inverntory"]
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
        for item in Shop.objects.filter(Q(Title__regex = search_word), Available = True, Publish = True).order_by('-DateCreate'):
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
        for item in Product.objects.filter(Q(Title__regex = search_word), Available = True, Publish = True, Status__in = ['1', '2', '3']).order_by('-DateCreate'):
            all_product_in_query.append(item)
        for item in Product.objects.filter(Q(Title__regex = search_word), Available = True, Publish = True, Status__in = ['4']).order_by('-DateCreate'):
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

        return redirect("nakhll_market:AccountLogin")


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

        return redirect("nakhll_market:AccountLogin")


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

        return redirect("nakhll_market:AccountLogin")


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

        return redirect("nakhll_market:AccountLogin")


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

            thisproduct = get_object_or_404(Product, Slug = this_product)

            if (Review_Title != '') and (Review_Description != ''):

                review_check = Review.objects.filter(Title = Review_Title, FK_UserAdder = request.user, FK_Product = thisproduct, Description = Review_Description)
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
                        shop_slug = thisproduct.FK_Shop.Slug,
                        product_slug = thisproduct.Slug,
                        status = True,
                        msg = 'نظر شما قبلا ثبت شده است!')

                else:

                    review = Review.objects.create(Title = Review_Title, FK_UserAdder = request.user, Description = Review_Description, FK_Product = thisproduct)

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
                    shop_slug = thisproduct.FK_Shop.Slug,
                    product_slug = thisproduct.Slug,
                    status = True,
                    msg = 'نقد شما با موفقیت ثبت شد، و پس از بررسی کارشناسان در سایت قرار خواهد گرفت.')

            else:

                return redirect('nakhll_market:Re_ProductsDetail',
                shop_slug =thisproduc.FK_Shop.Slug,
                product_slug = thisproduct.Slug,
                status = True,
                msg = 'عنوان و توضیحات برای ثیت نقد و بررسی اجباریست!')

    else:

        return redirect("nakhll_market:AccountLogin")


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

        return redirect("nakhll_market:AccountLogin")


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

        return redirect("nakhll_market:AccountLogin")


# -------------------------------------------------------------------------------------------------------------------------------

# Choise Random Product Function
class Choise_Random_Product(threading.Thread):
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