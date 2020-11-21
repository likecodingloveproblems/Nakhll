from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404 
from django.http import HttpResponse , JsonResponse

from django.utils.datastructures import MultiValueDictKeyError
from django.views.decorators.http import require_POST 
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib.auth.models import User
from django.core import serializers
import datetime
import threading
import json


from nakhll_market.models import Profile, Product, Shop, SubMarket, Category, BankAccount, ShopBanner, Attribute, AttrProduct, AttrPrice, ProductBanner, User_View, PageViews, PostRange, Message, User_Message_Status, Alert, Field, Newsletters, Message, ShopViews, Date_View
from Payment.models import Factor, Wallet, FactorPost, Transaction, PostBarCode, Coupon


from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.generics import (
    ListAPIView , 
    RetrieveAPIView ,
    DestroyAPIView ,
    UpdateAPIView ,
    CreateAPIView ,
)

from .serializers import *
from .serializers import FactorDesSerializer


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken

from oauth2_provider.views.generic import ProtectedResourceView
from django.http import HttpResponse

from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_403_FORBIDDEN,
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_202_ACCEPTED,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from rest_framework.response import Response


# user login //req : request.user  // res:  OR err
@csrf_exempt
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_login_user(request):
    return JsonResponse({'ok': True}, status = HTTP_200_OK)



# version app //req : request.user  // res:  OR err
@csrf_exempt
@api_view(["GET"])
@permission_classes([AllowAny,])
def get_version(request):
    return JsonResponse({'v':[{'version' : '1.0.0', 'isActive': True }, {'version' : '1.0.1', 'isActive': True },{'version' : '1.1.0', 'isActive': True }]}, status = HTTP_200_OK)



# check phone numbet //req : mobilenumber  // res: username OR err
@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def logins(request):
    mobilenumber = request.POST.get('mobilenumber')
    try:
        prouser = Profile.objects.get(MobileNumber = mobilenumber)
        thisuser = User.objects.get(id = prouser.FK_User_id)  
    
        return JsonResponse({'username': thisuser.username , 'issignup': True ,},
                    status=HTTP_200_OK)

    except:
        return JsonResponse({'err': 'user mobileNumber not found' ,'issignup': False},
                    status=HTTP_404_NOT_FOUND)




#user and profile //req : request.user  // res: (Profile.Object and user.Object in FK_User) OR err
@csrf_exempt
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_detail(request):
    if request.user.is_authenticated:
        try:
            this_profile = Profile.objects.get(FK_User = request.user)
            serializer = ProfileSerializer(this_profile)
            return JsonResponse(serializer.data, status = HTTP_200_OK)
        except Exception as e:
            return JsonResponse({'res': str(e),}, status = HTTP_400_BAD_REQUEST)
    else:
        return JsonResponse({'res': 'Authentication not valid',}, status = HTTP_400_BAD_REQUEST)




# get user bank status //req : request.user  // res: (true or false) OR err
@csrf_exempt
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_bank(request):
    if request.user.is_authenticated:
        try:
            this_profile = Profile.objects.get(FK_User = request.user)
            if BankAccount.objects.filter(FK_Profile = this_profile).exists():
                return JsonResponse({'res': True}, status = HTTP_200_OK)
            else:
                return JsonResponse({'res': False}, status = HTTP_200_OK)
        except Exception as e:
            return JsonResponse({'res': str(e),}, status = HTTP_400_BAD_REQUEST)
    else:
        return JsonResponse({'res': 'Authentication not valid',}, status = HTTP_400_BAD_REQUEST)



@csrf_exempt
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_transactions(request):
    try:
        transaction = Transaction.objects.filter(FK_User = request.user).order_by('-Date')
        serializer = TransactionSerializer(transaction, many = True)
        return JsonResponse(serializer.data, status = HTTP_200_OK, safe = False)
    except:
        return JsonResponse({'err': 'Authentication not valid OR Error getting data',}, status = HTTP_404_NOT_FOUND)




# wallet //req : request.user  // res: (wallet user) OR err
@csrf_exempt
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_wallet(request):
    try:
        this_wallet = Wallet.objects.get(FK_User = request.user)
        serializer = WalletSerializer(this_wallet)
        return JsonResponse(serializer.data, status = HTTP_200_OK)
    except:
        return JsonResponse({'res': 'Authentication not valid',}, status = HTTP_400_BAD_REQUEST)



# Shop //req : request.user  // res: (shop user) OR err
@csrf_exempt
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_shop(request):
    try:
        allusershop = Shop.objects.filter(FK_ShopManager = request.user)
        serializer = ShopListHomeSerializer(allusershop, many = True)
        return JsonResponse(serializer.data, status = HTTP_200_OK, safe = False)
    except:
        return JsonResponse({'res': 'Shops Not found ',}, status = HTTP_404_NOT_FOUND)



# Product //req : request.user  // res: (shop user) OR err
@csrf_exempt
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_product(request):
    try:
        userproducts = []
        for shop_item in Shop.objects.filter(FK_ShopManager = request.user):
            for product_item in Product.objects.filter(FK_Shop = shop_item):
                userproducts.append(product_item)
        serializer = ProductListHomeSerializer(userproducts, many = True)
        return JsonResponse(serializer.data, status = HTTP_200_OK, safe = False)
    except:
        return JsonResponse({'res': 'Products Not found ',}, status = HTTP_404_NOT_FOUND)




# submarket list //req : request.user  // res: (shop user) OR err
@csrf_exempt
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_submarket_list(request):
    try:
        submarket = SubMarket.objects.filter(Publish = True)
        serializer = SubMarketSerializer(submarket , many = True)
        return JsonResponse(serializer.data, status = HTTP_200_OK, safe = False)
    except:
        return JsonResponse({'res': 'Not found' ,},  status=HTTP_404_NOT_FOUND)





# category list //req : request.user  // res: (shop user) OR err
@csrf_exempt
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_category_list(request):
    try:
        category = Category.objects.filter(Publish = True)
        serializer = CategorySerializer(category , many = True)
        return JsonResponse(serializer.data, status = HTTP_200_OK, safe = False)
    except:
        return JsonResponse({'res': 'Not found' ,}, status=HTTP_404_NOT_FOUND)




# post range list //req : request.user  // res: (shop user) OR err
@csrf_exempt
@api_view(["GET"])
@permission_classes([AllowAny,])
def get_post_range_list(request):
    try:
        post_range = PostRange.objects.all()
        serializer = PostRangeShowString(post_range, many = True)
        return JsonResponse(serializer.data, status = HTTP_200_OK, safe = False)
    except:
        return JsonResponse({'res': 'Not found' ,}, status=HTTP_404_NOT_FOUND)




# attribute list //req : request.user  // res: (shop user) OR err
@csrf_exempt
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_attribute_list(request):
    try:
        attribute = Attribute.objects.filter(Publish = True)
        serializer = SubMarketSerializer(attribute , many=True)
        return JsonResponse(serializer.data, status = HTTP_200_OK, safe=False)
    except:
        return JsonResponse({'res': 'Not found' ,},
                    status=HTTP_404_NOT_FOUND)




# check shop slug //req : request.user  // res:  OR err
@csrf_exempt
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def check_slug_shop(request):
    try: 
        Slug_id = request.POST.get('slug_id')
        Shop.objects.get(Slug = Slug_id ,)
        return JsonResponse({'res': False,},status = HTTP_400_BAD_REQUEST)
    except:
        return JsonResponse({'res': True,},status = HTTP_200_OK)



# check product slug //req : request.user  // res:  OR err
@csrf_exempt
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def check_slug_product(request):
    try: 
        Slug_id = request.POST.get('slug_id')
        Product.objects.get(Slug = Slug_id)
        return JsonResponse({'res': False,},status = HTTP_400_BAD_REQUEST)
    except:
        return JsonResponse({'res': True,},status=HTTP_200_OK)




# send factor //req : request.user  // res: (send factor user) OR err
@csrf_exempt
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_send_factor(request):
    try:
        factors_redi = []
        for item in Factor.objects.filter(PaymentStatus = True, Publish = True):
            if item.get_send_user_factor(request):
                factors_redi.append(item)
        serializer = FactorListSerializer(factors_redi, many = True)
        return JsonResponse(serializer.data, status = HTTP_200_OK, safe = False)
    except Exception as e:
        return JsonResponse({'res' : str(e)}, status = HTTP_404_NOT_FOUND)




# cancel factor //req : request.user  // res: (cancel factor user) OR err
@csrf_exempt
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_cancel_factor(request):
    try:
        factors_redi = []
        for item in Factor.objects.filter(PaymentStatus = True, Publish = True):
            if item.get_cancel_factor(request):
                factors_redi.append(item)
        serializer = FactorListSerializer(factors_redi, many = True)
        return JsonResponse(serializer.data, status = HTTP_200_OK, safe = False)
    except Exception as e:
        return JsonResponse({'res' : str(e)}, status = HTTP_404_NOT_FOUND)




# in preparation factor //req : request.user  // res: (in preparation factor user) OR err
@csrf_exempt
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_inpreparation_factor(request):
    try:
        factors_redi = []
        for item in Factor.objects.filter(PaymentStatus = True, Publish = True):
            if item.get_inpreparation_factor(request):
                factors_redi.append(item)
        serializer = FactorListSerializer(factors_redi, many = True)
        return JsonResponse(serializer.data, status = HTTP_200_OK, safe = False)
    except Exception as e:
        return JsonResponse({'res' : str(e)}, status = HTTP_404_NOT_FOUND)




# Waiting for confirmation factor //req : request.user  // res: (Waiting factor user) OR err
@csrf_exempt
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_waiting_factor(request):
    try:
        factors_redi = []
        for item in Factor.objects.filter(PaymentStatus = True, Publish = True):
            if item.get_wait_user_factor(request):
                factors_redi.append(item)
        serializer = FactorListSerializer(factors_redi, many = True)
        return JsonResponse(serializer.data, status = HTTP_200_OK, safe = False)
    except Exception as e:
        return JsonResponse({'res' : str(e)}, status = HTTP_404_NOT_FOUND)




# detail factor //req : factor_id  // res: (factor detail) OR err
@csrf_exempt
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def get_factor_detail(request):
    try:
        if Shop.objects.filter(FK_ShopManager = request.user).exists():
            # get data
            factor = Factor.objects.get(ID = request.POST["factor_id"])
            user_factor_item = []
            for item in factor.FK_FactorPost.all():
                if item.FK_Product.FK_Shop.FK_ShopManager == request.user:
                    user_factor_item.append(item)
            if user_factor_item:
                serializer = FactorDesSerializer(factor)
                return JsonResponse(serializer.data, status = HTTP_200_OK)
            else:
                return JsonResponse({'err' : 'You do not have permission to access'}, status = HTTP_403_FORBIDDEN)
        else:
            return JsonResponse({'err' : 'You dont have any shops'}, status = HTTP_403_FORBIDDEN)
    except Exception as e:
        return JsonResponse({'err' : str(e)}, status = HTTP_500_INTERNAL_SERVER_ERROR)




# detail factor //req : factor_id  // res: (factor detail) OR err
@csrf_exempt
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def get_factor_details(request):
    try:
        if Shop.objects.filter(FK_ShopManager = request.user).exists():
            # get data
            factor = Factor.objects.get(ID = request.POST["factor_id"])
            user_factor_item = []
            for item in factor.FK_FactorPost.all():
                if item.FK_Product.FK_Shop.FK_ShopManager == request.user:
                    user_factor_item.append(item)
            if user_factor_item:
                serializer = FactorDetailsSerializer(factor)
                item_serializer = FactorPostSerializer(user_factor_item, many = True)
                return JsonResponse({'factor' : serializer.data, 'items' : item_serializer.data}, status = HTTP_200_OK)
            else:
                return JsonResponse({'err' : 'You do not have permission to access'}, status = HTTP_403_FORBIDDEN)
        else:
            return JsonResponse({'err' : 'You dont have any shops'}, status = HTTP_403_FORBIDDEN)
    except Exception as e:
        return JsonResponse({'err' : str(e)}, status = HTTP_500_INTERNAL_SERVER_ERROR)





# detail Product //req : product_id  // res: (Product detail) OR err
@csrf_exempt
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def get_product_detail(request):
    if Product.objects.filter(ID = request.POST["product_id"]).exists():
        try:
            # Get This Product
            this_product = get_object_or_404(Product, ID = request.POST["product_id"])
            if Shop.objects.filter(ID = this_product.FK_Shop.ID, FK_ShopManager = request.user).exists():
                serializer = ProductDetailSerializer(this_product)
                return JsonResponse(serializer.data, status = HTTP_200_OK)
            else:
                return JsonResponse({'res' : 'عدم دسترسی...'}, status = HTTP_404_NOT_FOUND)
        except Exception as e:
            return JsonResponse({'res' :str(e)}, status = HTTP_400_BAD_REQUEST)
    else:
        return JsonResponse({'res' : 'محصولی با این ویژگی ها یافت نشد...'}, status = HTTP_404_NOT_FOUND)





# detail Shop //req : Shop_id  // res: (Shop detail) OR err
@csrf_exempt
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def get_shop_detail(request):
    # Get User If This Shop For Him
    if Shop.objects.filter(ID = request.POST.get('shop_id'), FK_ShopManager = request.user).exists():

        shop = Shop.objects.filter(ID = request.POST.get('shop_id'), FK_ShopManager = request.user)[0]
        serializer = ShopDetailSerializer(shop)
        return JsonResponse(serializer.data, status = HTTP_200_OK)

    else:

        return JsonResponse({'res' : 'You do not have access to this shop'} , status = HTTP_404_NOT_FOUND )






#update_user_profile //req :  res: (Sale statistics) {send, wait, satisfaction}  OR err
@csrf_exempt
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def update_user_profile(request):

    thisuser = request.user

    try:
        User_FirstName = request.POST.get('User_FirstName')
    except :
        User_FirstName = ''

    try:
        User_LastName = request.POST.get('User_LastName')
    except :
        User_LastName = ''
        
    try:
        User_Email = request.POST.get('User_Email')
    except :
        User_Email = ''   
                            
    # --------------------------------------------------------
    thisprofile = Profile.objects.get(FK_User_id = thisuser.id)

    try:
        Profile_Bio = request.POST.get('Profile_Bio')
    except :
        Profile_Bio = ''

    try:
        Profile_BrithDay = request.POST.get('Profile_BrithDay')
    except :
        Profile_BrithDay = ''

    try:
        Profile_State = request.POST.get('Profile_State')
    except :
        Profile_State = ''

    try:
        Profile_BigCity = request.POST.get('Profile_BigCity')
    except :
        Profile_BigCity = ''

    try:
        Profile_City = request.POST.get('Profile_City')
    except :
        Profile_City = ''

    try:
        Profile_ZipCode = request.POST.get('Profile_ZipCode')
    except :
        Profile_ZipCode = ''

    try:
        Profile_Address = request.POST.get('Profile_Address')
    except :
        Profile_Address = ''
    try:
        Profile_Location = request.POST.get('Profile_Location')
    except :
        Profile_Location = ''

    try:
        Profiel_PhoneNumber = request.POST.get('Profile_PhoneNumber')
    except :
        Profiel_PhoneNumber = ''

    try:
        Profile_CityPerCode = request.POST.get('Profile_CityPerCode')
    except :
        Profile_CityPerCode = ''

    # try:
    #     Profile_MobileNumber = request.POST.get('Profile_MobileNumber')
    # except :
    #     Profile_MobileNumber = ''

    try:
        Profile_FaxNumber = request.POST.get('Profile_FaxNumber')
    except :
        Profile_FaxNumber = ''

    try:
        Profile_SexState = request.POST.get('Profile_SexState')
    except :
        Profile_SexState = '0'

    # Profile_SexState = request.POST.get('Profile_SexState')

    try:
        Profile_TutorialWebsite = request.POST.get('Profile_TutorialWebsite')
    except :
        Profile_TutorialWebsite = '8'
    # Profile_TutorialWebsite = request.POST.get('Profile_TutorialWebsite')
    
    if (User_FirstName != '') and (User_LastName != '') and (User_Email != ''):

        if (thisuser.first_name != User_FirstName) or (thisuser.last_name != User_LastName) or (thisuser.email != User_Email):

            if thisuser.email != User_Email:
                if Newsletters.objects.filter(Email = User_Email).count() == 0:
                    New = Newsletters(Email = User_Email)
                    New.save()

            thisuser.first_name = User_FirstName
            thisuser.last_name = User_LastName           
            thisuser.email = User_Email

            thisuser.save()

            

            if (thisprofile.ZipCode != Profile_ZipCode) or (thisprofile.Address != Profile_Address) or (thisprofile.State != Profile_State) or(thisprofile.BigCity != Profile_BigCity) or(thisprofile.City != Profile_City) or (thisprofile.Location != Profile_Location) or (thisprofile.BrithDay != Profile_BrithDay) or (thisprofile.FaxNumber != Profile_FaxNumber) or (thisprofile.CityPerCode != Profile_CityPerCode) or(thisprofile.PhoneNumber != Profiel_PhoneNumber) or(thisprofile.Bio != Profile_Bio) or(thisprofile.Sex != ProfileSex) or(thisprofile.TutorialWebsite != ProfileToWeb):
                
                # if thisprofile.MobileNumber != Profile_MobileNumber:
                #     if Newsletters.objects.filter(MobileNumber = Profile_MobileNumber).count() == 0:
                #         New = Newsletters(MobileNumber = Profile_MobileNumber)
                #         New.save()

                # if Profile_SexState == 'انتخاب جنسیت':
                #     ProfileSex ='0'
                # elif Profile_SexState == 'زن':
                #     ProfileSex ='1'
                # elif Profile_SexState == 'مرد':
                #     ProfileSex ='2'
                # elif Profile_SexState == 'سایر':
                #     ProfileSex ='3'

                ProfileSex = Profile_SexState


                # if Profile_TutorialWebsite == 'موتور های جستجو':
                #     ProfileToWeb ='0'
                # elif Profile_TutorialWebsite == 'حجره داران':
                #     ProfileToWeb ='1'
                # elif Profile_TutorialWebsite == 'شبکه های اجتماعی':
                #     ProfileToWeb ='2'
                # elif Profile_TutorialWebsite == 'کاربران':
                #     ProfileToWeb ='3'
                # elif Profile_TutorialWebsite == 'رسانه ها':
                #     ProfileToWeb ='4'
                # elif Profile_TutorialWebsite == 'تبلیغات':
                #     ProfileToWeb ='5'
                # elif Profile_TutorialWebsite == 'نود ها':
                #     ProfileToWeb ='6'
                # elif Profile_TutorialWebsite == 'سایر':
                #     ProfileToWeb ='7'
                # elif Profile_TutorialWebsite == 'هیچ کدام':
                #     ProfileToWeb ='8'

                ProfileToWeb = Profile_TutorialWebsite

                # thisprofile.MobileNumber = Profile_MobileNumber
                thisprofile.ZipCode = Profile_ZipCode
                thisprofile.Address = Profile_Address
                thisprofile.State = Profile_State
                thisprofile.BigCity = Profile_BigCity
                thisprofile.City = Profile_City
                thisprofile.Location = Profile_Location
                thisprofile.BrithDay = Profile_BrithDay
                thisprofile.FaxNumber = Profile_FaxNumber
                thisprofile.CityPerCode = Profile_CityPerCode
                thisprofile.PhoneNumber = Profiel_PhoneNumber
                thisprofile.Bio = Profile_Bio
                thisprofile.Sex = ProfileSex
                thisprofile.TutorialWebsite = ProfileToWeb
            
                try:
                    Profile_Avatar = request.FILES["Profile_Image"]
                except MultiValueDictKeyError:
                    Profile_Avatar = False


                if Profile_Avatar != False:
                    thisprofile.Image = Profile_Avatar
                else:
                    thisprofile.Image = thisprofile.Image


                thisprofile.save()


                message ='مشخصات شما آپدیت شده!'
                return JsonResponse({'res' : message } , status = HTTP_200_OK)


            else:

                message ='تغییری ایجاد نکرده اید!'
                return JsonResponse({'res' : message } , status = HTTP_400_BAD_REQUEST)

        else:

            if (thisprofile.ZipCode != Profile_ZipCode) or (thisprofile.Address != Profile_Address) or (thisprofile.State != Profile_State) or(thisprofile.BigCity != Profile_BigCity) or(thisprofile.City != Profile_City) or(thisprofile.Location != Profile_Location) or(thisprofile.BrithDay != Profile_BrithDay) or(thisprofile.FaxNumber != Profile_FaxNumber) or(thisprofile.CityPerCode != Profile_CityPerCode) or (thisprofile.PhoneNumber != Profiel_PhoneNumber) or (thisprofile.Bio != Profile_Bio) or (thisprofile.Sex != ProfileSex) or (thisprofile.TutorialWebsite != ProfileToWeb):
                
                # if thisprofile.MobileNumber != Profile_MobileNumber:
                #     if Newsletters.objects.filter(MobileNumber = Profile_MobileNumber).count() == 0:
                #         New = Newsletters(MobileNumber = Profile_MobileNumber)
                #         New.save()

                # if Profile_SexState == 'انتخاب جنسیت':
                #     ProfileSex ='0'
                # elif Profile_SexState == 'زن':
                #     ProfileSex ='1'
                # elif Profile_SexState == 'مرد':
                #     ProfileSex ='2'
                # elif Profile_SexState == 'سایر':
                #     ProfileSex ='3'

                ProfileSex = Profile_SexState


                # if Profile_TutorialWebsite == 'موتور های جستجو':
                #     ProfileToWeb ='0'
                # elif Profile_TutorialWebsite == 'حجره داران':
                #     ProfileToWeb ='1'
                # elif Profile_TutorialWebsite == 'شبکه های اجتماعی':
                #     ProfileToWeb ='2'
                # elif Profile_TutorialWebsite == 'کاربران':
                #     ProfileToWeb ='3'
                # elif Profile_TutorialWebsite == 'رسانه ها':
                #     ProfileToWeb ='4'
                # elif Profile_TutorialWebsite == 'تبلیغات':
                #     ProfileToWeb ='5'
                # elif Profile_TutorialWebsite == 'نود ها':
                #     ProfileToWeb ='6'
                # elif Profile_TutorialWebsite == 'سایر':
                #     ProfileToWeb ='7'
                # elif Profile_TutorialWebsite == 'هیچ کدام':
                #     ProfileToWeb ='8'

                ProfileToWeb = Profile_TutorialWebsite



                # thisprofile.MobileNumber = Profile_MobileNumber
                thisprofile.ZipCode = Profile_ZipCode
                thisprofile.Address = Profile_Address
                thisprofile.State = Profile_State
                thisprofile.BigCity = Profile_BigCity
                thisprofile.City = Profile_City
                thisprofile.Location = Profile_Location
                thisprofile.BrithDay = Profile_BrithDay
                thisprofile.FaxNumber = Profile_FaxNumber
                thisprofile.CityPerCode = Profile_CityPerCode
                thisprofile.PhoneNumber = Profiel_PhoneNumber
                thisprofile.Bio = Profile_Bio
                thisprofile.Sex = ProfileSex
                thisprofile.TutorialWebsite = ProfileToWeb
            
                try:
                    Profile_Avatar = request.FILES["Profile_Image"]
                except MultiValueDictKeyError:
                    Profile_Avatar = False

                if Profile_Avatar != False:
                    thisprofile.Image = Profile_Avatar
                else:
                    thisprofile.Image = thisprofile.Image

                thisprofile.save()


                message ='مشخصات شما آپدیت شده!'
                return JsonResponse({'res' : message } , status = HTTP_200_OK)
                
            else: 
                message ='تغییری ایجاد نکرده اید!'
                return JsonResponse({'res' : message } , status = HTTP_400_BAD_REQUEST)

    else:
        message ='فیلد های نام، نام خانوادگی، ایمیل و شماره موبایل نمی تواند خالی باشد!'
        return JsonResponse({'res' : message } , status = HTTP_400_BAD_REQUEST)







# create new shop //req :  form   // res: ({res : 'msg' }) OR err
@csrf_exempt
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_new_shop(request):
    if BankAccount.objects.filter(FK_Profile = Profile.objects.get(FK_User = request.user)).exists(): 
        # Get Data   
        Shop_Title = request.POST.get('shop_title')
        Shop_Slug = request.POST.get('shop_slug')
        try:
            Shop_Des = request.POST.get('shop_des')
        except:
            Shop_Des = ''
        Shop_State = request.POST.get('shop_state')
        Shop_BigCity = request.POST.get('shop_bigcity')
        Shop_City = request.POST.get('shop_city')
        try:
            Shop_SubMarkets = request.POST.get("shop_submarket")
            Shop_SubMarket_test = Shop_SubMarkets.split('~')
        except:
            return JsonResponse({'res' : 'خطایی رخ داده است!'} , status= HTTP_400_BAD_REQUEST )
        try:
            Shop_Bio = request.POST.get('shop_bio')
        except:
            Shop_Bio = ''
        Shop_Holidays = request.POST.get('shop_holidays')
        try:
            Shop_Avatar = request.FILES["shop_image"]
        except MultiValueDictKeyError:
            Shop_Avatar = ''
        try:
            shop = Shop.objects.create(FK_ShopManager = request.user, Title = Shop_Title, Slug = Shop_Slug, State = Shop_State, BigCity = Shop_BigCity, City = Shop_City)
            # Set Shop Bio
            if Shop_Bio != '':
                shop.Bio = Shop_Bio
            # Set Shop Description
            if Shop_Des != '':
                shop.Description = Shop_Des
            # Set Holidays
            if Shop_Holidays != 'null':
                shop.Holidays = Shop_Holidays
            # Set Image
            if Shop_Avatar != '':
                shop.Image = Shop_Avatar
            # Set Shop Submarkets
            for item in Shop_SubMarket_test:
                shop.FK_SubMarket.add(SubMarket.objects.get(Slug = item))
            shop.save()
            Alert.objects.create(Part = '2', FK_User = request.user, Slug = shop.ID)
            return JsonResponse({'res' : 'تغییرات شما ثبت گردیده و پس از تایید کارشناسان اعمال می گردد!' , 'id' : shop.ID} , status = HTTP_201_CREATED)
        except:
            return JsonResponse({'res' : 'خطایی رخ داده است!'} , status = HTTP_400_BAD_REQUEST)
    else:
        return JsonResponse({'res' : 'برای صاحب حجره حساب بانکی ایجاد نشده است!'} , status = HTTP_400_BAD_REQUEST)



# add shop banner //req :  form   // res: ({res : 'msg' }) OR err
@csrf_exempt
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_shop_banner(request):
    if Shop.objects.filter(ID = request.POST.get('shop_id'), FK_ShopManager = request.user).exists():
        
        try:
            Shop_id = request.POST.get('shop_id')
        except:
            messag = 'خطا در دریافت اطلاعات حجره ... مجدد امتحان کنید'
            return JsonResponse({'res' : messag} , status= HTTP_400_BAD_REQUEST ) 
    
        try:
            Banner_Image = request.FILES["banner_image"]
        except MultiValueDictKeyError:
            Banner_Image = False

        try:
            Banner_Title = request.POST.get('banner_title')
        except:
            Banner_Title = False

        try:
            Banner_URL = request.POST.get('banner_url')
        except:
            Banner_URL = False
        

        if (Banner_Title != False) and (Banner_Image != False):
            thisbanner = ShopBanner(FK_Shop = Shop.objects.get(ID = Shop_id), Title = Banner_Title, Image = Banner_Image)
            thisbanner.save()

            alert = Alert(FK_User = request.user, Part = '4', Slug = thisbanner.id)
            alert.save()

            if (Banner_URL != False):
                thisbanner.URL = Banner_URL
                thisbanner.save()


            messag = 'تغییرات شما با موفقیت ثبت شد و بعد از بررسی اعمال می گردد!'
            return JsonResponse({'res' : messag} , status= HTTP_201_CREATED )


        else:
            messag = 'اطلاعات وارد شده کامل نمی باشد! (عنوان و عکس اجباریست!)'
            return JsonResponse({'res' : messag} , status= HTTP_400_BAD_REQUEST )


    else:
        return JsonResponse({'res' : 'You do not have access to this shop'} , status = HTTP_404_NOT_FOUND)




# create new product //req :  form   // res: ({res : 'msg' }) OR err  
@csrf_exempt
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_new_product(request):
    try:
        if Shop.objects.filter(ID = request.POST.get('product_shop_id'), FK_ShopManager = request.user).exists():
            try:
                Image = request.FILES["product_img"]
            except MultiValueDictKeyError:
                Image = ''

            try:
                Title = request.POST["product_title"]
            except:
                Title = ''

            try:
                Slug = request.POST["product_slug"]
            except:
                Slug = ''

            try:
                This_Shop = request.POST["product_shop_id"]
            except:
                This_Shop = ''

            try:
                Description = request.POST["product_description"]
            except:
                Description = ''
            
            try:
                CategoryList = request.POST.get("product_category")
            except:
                CategoryList = ''

            try:
                This_SubMarket = request.POST.get("product_submarket")
            except:
                This_SubMarket = ''
                
            try:
                Bio = request.POST["product_bio"]
            except:
                Bio = ''

            try:
                Story = request.POST["product_story"]
            except:
                Story = ''

            try:
                Price = request.POST["product_price"]
            except:
                Price = ''

            try:
                OldPrice = request.POST["product_oldprice"]
            except:
                OldPrice = ''

            try:
                Post_Range_Type = request.POST["product_post_range_type"]
            except:
                Post_Range_Type = ''

            try:
                Status = request.POST["product_status"]
            except:
                Status = ''
            
            try:
                Post_Range = request.POST.get("product_post_range")
            except:
                Post_Range = ''

            try:
                Exception_Post_Range = request.POST.get("product_exception_post_range")
            except:
                Exception_Post_Range = ''

            try:
                Net_Weight = request.POST["product_net_weight"]
            except:
                Net_Weight = ''

            try:
                Packing_Weight = request.POST["product_packing_weight"]
            except:
                Packing_Weight = ''

            try:
                Length_With_Packaging = request.POST["product_length_with_packaging"]
            except:
                Length_With_Packaging = ''

            try:
                Width_With_Packaging = request.POST["product_width_with_packaging"]
            except:
                Width_With_Packaging = ''

            try:
                Height_With_Packaging = request.POST["product_height_with_packaging"]
            except:
                Height_With_Packaging = ''

            try:
                Store_Inventory = request.POST["product_store_inventory"]
            except:
                Store_Inventory = ''
            
            # Create New Product
            this_product = Product.objects.create(Title = Title, Slug = Slug, FK_SubMarket = SubMarket.objects.get(ID = This_SubMarket), Image = Image, FK_Shop = Shop.objects.get(ID = This_Shop), Price = Price, Status = Status)
            # Check Product Status            
            if Status == '1':
                this_product.Inventory = Store_Inventory
            elif Status == '4':
                this_product.Inventory = 0

            for item in CategoryList.split('~'):
                try:
                    if Category.objects.filter(id = item).exists():
                        this_product.FK_Category.add(Category.objects.get(id = item))
                except:
                    continue
            
            Post_Range_List = Post_Range.split('~')
            for item in Post_Range_List:
                try:
                    if PostRange.objects.filter(id = item).exists():
                        this_product.FK_PostRange.add(PostRange.objects.get(id = item))
                except:
                    continue

            Exception_Post_Range_List = Exception_Post_Range.split('~')
            for item in Exception_Post_Range_List:
                try:
                    if PostRange.objects.filter(id = item).exists():
                        this_product.FK_ExceptionPostRange.add(PostRange.objects.get(id = item))
                except:
                    continue

            if Description != '':
                this_product.Description = Description

            if Bio != '':
                this_product.Bio = Bio

            if Story != '':
                this_product.Story = Story

            if OldPrice != '':
                this_product.OldPrice = OldPrice       

            this_product.PostRangeType = Post_Range_Type
            # Product Weight Info
            this_product.Net_Weight = Net_Weight
            this_product.Weight_With_Packing = Packing_Weight
            # Product Dimensions Info
            this_product.Length_With_Packaging = Length_With_Packaging
            this_product.Width_With_Packaging = Width_With_Packaging
            this_product.Height_With_Packaging = Height_With_Packaging
            # Save Data    
            this_product.save()
            # Set Alert
            Alert.objects.create(FK_User = request.user, Part = '6', Slug = this_product.ID)

            return JsonResponse({'res' : 'محصول جدید ایجاد شد!' , 'id' : this_product.ID}, status = HTTP_201_CREATED)   
        else:
            return JsonResponse({'res' : 'محصول با این مشخصات یافت نشد.'}, status = HTTP_400_BAD_REQUEST)
    except Exception as e:
        return JsonResponse({'res' :str(e)}, status = HTTP_400_BAD_REQUEST)





# edit shop //req :  form   // res: ({res : 'msg' }) OR err
@csrf_exempt
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def edit_user_shop(request):
    if Shop.objects.filter(FK_ShopManager = request.user, Slug = request.POST.get('shop_slug')).exists():

        try:
            Shop_Title = request.POST.get('shop_title')
        except:
            Shop_Title = ''

        try:
            Shop_Des = request.POST.get('shop_des')
        except:
            Shop_Des = ''

        try:
            Shop_State = request.POST.get('shop_state')
        except:
            Shop_State = ''

        try:
            Shop_BigCity = request.POST.get('shop_bigcity')
        except:
            Shop_BigCity = ''

        try:
            Shop_City = request.POST.get('shop_city')
        except:
            Shop_City = ''

        try:
            Shop_SubMarkets = request.POST.get("shop_submarket")
        except:
            Shop_SubMarkets = ''

        try:
            Shop_Bio = request.POST.get('shop_bio')
        except:
            Shop_Title = ''

        try:
            Shop_Holidays = request.POST.get("shop_holidays")
        except:
            Shop_Holidays = ''

        try:
            Shop_Avatar = request.FILES["shop_image"]
        except MultiValueDictKeyError:
            Shop_Avatar = ''
        try:
            # Get This Shop
            this_shop = get_object_or_404(Shop, Slug = request.POST.get('shop_slug'))
            alert = None
            # Set Alert
            if Alert.objects.filter(Part = '3', Slug = this_shop.ID, Seen = False).exists():
                alert = get_object_or_404(Alert, Part = '3', Slug = this_shop.ID, Seen = False)
                alert.FK_Field.all().delete()
                alert.save()
            else:
                alert = Alert.objects.create(FK_User = request.user, Part = '3', Slug = this_shop.ID)
            # Set This_Submarket
            if Shop_SubMarkets != '':
                SubMarketField = Field(Title = 'SubMarket', Value = Shop_SubMarkets)
                SubMarketField.save()
                alert.FK_Field.add(SubMarketField)
                alert.save()
            # Set Shop Image
            if Shop_Avatar != '':
                this_shop.NewImage = Shop_Avatar
                this_shop.save()
                img_str = 'NewImage' + '#' + str(this_shop.NewImage)
                ImageField = Field(Title = 'Image', Value = img_str)
                ImageField.save()
                alert.FK_Field.add(ImageField)
                alert.save()
            # Set Title
            if (Shop_Title != '') and (Shop_Title != this_shop.Title):
                TitleField = Field(Title = 'Title', Value = Shop_Title)
                TitleField.save()
                alert.FK_Field.add(TitleField)
                alert.save()
            # Set Descrption
            if (Shop_Des != '') and (Shop_Des != this_shop.Description):
                DescriptionField = Field(Title = 'Description', Value = Shop_Des)
                DescriptionField.save()
                alert.FK_Field.add(DescriptionField)
                alert.save()
            # Set Bio
            if (Shop_Bio != '') and (Shop_Bio != this_shop.Bio):
                BioField = Field(Title = 'Bio', Value = Shop_Bio)
                BioField.save()
                alert.FK_Field.add(BioField)
                alert.save()
            # Set State
            if (Shop_State != '') and (Shop_State != this_shop.State):
                StateField = Field(Title = 'State', Value = Shop_State)
                StateField.save()
                alert.FK_Field.add(StateField)
                alert.save()
            # Set BigCity
            if (Shop_BigCity != '') and (Shop_BigCity != this_shop.BigCity):
                BigCityField = Field(Title = 'BigCity', Value = Shop_BigCity)
                BigCityField.save()
                alert.FK_Field.add(BigCityField)
                alert.save()
            # Set City
            if (Shop_City != '') and (Shop_City != this_shop.City):
                CityField = Field(Title = 'City', Value = Shop_City)
                CityField.save()
                alert.FK_Field.add(CityField)
                alert.save()
            # Set Holidays
            if Shop_Holidays != this_shop.Holidays:
                HolidaysField = Field(Title = 'Holidays', Value = Shop_Holidays)
                HolidaysField.save()
                alert.FK_Field.add(HolidaysField)
                alert.save()
            # Check Alert
            if alert.FK_Field.all().count() == 0:
                alert.FK_Field.all().delete()
                alert.delete()
                return JsonResponse({'res' : 'تغییری ایجاد نکرده اید!'} , status = HTTP_400_BAD_REQUEST)
            else:
                return JsonResponse({'res' : 'تغییرات شما ثبت شد!'} , status = HTTP_200_OK)
            
        except Exception as e:
            return JsonResponse({'res' :str(e)}, status = HTTP_400_BAD_REQUEST)
    else:
        return JsonResponse({'res' : 'حجره ای با این مشخصات یافت نشد!'} , status = HTTP_404_NOT_FOUND)




# edit shop banner //req :  form   // res: ({res : 'msg' }) OR err
@csrf_exempt
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def edit_shop_banner(request):
    try:
        if Shop.objects.filter(FK_ShopManager = request.user).exists():
            try:
                Banner_id = request.POST.get('banner_id')
                thisbanner = ShopBanner.objects.get(id = Banner_id)
            except:
                thisbanner = False

            try:
                Banner_Image = request.FILES["banner_image"]
            except MultiValueDictKeyError:
                Banner_Image = ''

            try:
                Banner_Title = request.POST.get('banner_title')
            except:
                Banner_Title = False

            try:
                Banner_URL = request.POST.get('banner_url')
            except:
                Banner_URL = False
            

            if (Banner_Title != ''):

                if (Banner_Title != thisbanner.Title) or (Banner_Image != '') or (Banner_URL != thisbanner.URL):

                    if Alert.objects.filter(Part = '5', Slug = thisbanner.id, Seen = False).count() == 0:
                        alert = Alert(FK_User = request.user, Part = '5', Slug = thisbanner.id)
                        alert.save()
                    else:
                        alert = Alert.objects.get(Part = '5', Slug = thisbanner.id, Seen = False)
                        alert.FK_Field.all().delete()
                        alert.save()

                    if (Banner_Title != thisbanner.Title):
                        # thisbanner.Title = Banner_Title
                        # thisbanner.save()
                        Title_Alert = Field(Title = 'Title', Value = Banner_Title)
                        Title_Alert.save()
                        alert.FK_Field.add(Title_Alert)

                    if (Banner_Image != ''):
                        # thisbanner.Image = Banner_Image
                        # thisbanner.save()
                        thisbanner.NewImage = Banner_Image
                        thisbanner.save()
                        img_str = 'NewImage' + '#' + str(thisbanner.NewImage)
                        Image_Alert = Field(Title = 'Image', Value = img_str)
                        Image_Alert.save()
                        alert.FK_Field.add(Image_Alert)

                    if (Banner_URL != thisbanner.URL):
                        # thisbanner.URL = Banner_URL
                        # thisbanner.save()
                        URL_Alert = Field(Title = 'URL',Value = Banner_URL)
                        URL_Alert.save()
                        alert.FK_Field.add(URL_Alert)

                    messag = 'تغییرات شما با موفقیت ثبت شد و بعد از بررسی اعمال می گردد!'
                    return JsonResponse({'res' : messag}, status = HTTP_200_OK)
                else:
                    messag = 'تغییری اعمال نکرده اید!'
                    return JsonResponse({'res' : messag}, status = HTTP_400_BAD_REQUEST)
            else:
                messag = 'اطلاعات وارد شده کامل نمی باشد! (عنوان بنر و عکس بنر اجباریست)'
                return JsonResponse({'res' : messag}, status = HTTP_400_BAD_REQUEST)
        else:
            return JsonResponse({'res' : 'You dont have any shops'}, status = HTTP_404_NOT_FOUND)
    except Exception as e:
        return JsonResponse({'res' : str(e)}, status = HTTP_400_BAD_REQUEST)



    



# edit banner Status //req :  form   // res: ({res : 'msg' }) OR err
@csrf_exempt
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def edit_shop_banner_status(request):
    if Shop.objects.filter(FK_ShopManager = request.user).exists():
        #Get Banner
        try:
            Banner_id = request.POST.get('banner_id')
            banner = ShopBanner.objects.get(id = Banner_id)
        except MultiValueDictKeyError:
            banner = False
        # Change Status
        if banner.Available:
            banner.Available = False
            banner.save()
        else:
            banner.Available = True
            banner.save()


        messag = 'وضعیت بنر مد نظر شما تغییر کرد!'
        return JsonResponse({'res' : messag} , status= HTTP_200_OK )

    else:
        return JsonResponse({'res' : 'You dont have any shops'} , status= HTTP_404_NOT_FOUND )







# delete  shop banner //req :  form   // res: ({res : 'msg' }) OR err
@csrf_exempt
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def delete_shop_banner(request):
    try:
        if Shop.objects.filter(FK_ShopManager = request.user).exists():
            # Get Banner
            banner = ShopBanner.objects.get(id = request.POST["banner_id"])
            # Change Status
            banner.Publish = False
            banner.save()
            # Set Alert
            Alert.objects.create(Part = '22', FK_User = request.user, Slug = banner.id)
            
            return JsonResponse({'res' : 'بنر حذف شد...'}, status = HTTP_200_OK)
        else:
            return JsonResponse({'res' : 'You dont have any shops'}, status = HTTP_404_NOT_FOUND)
    except Exception as e:
        return JsonResponse({'res' : str(e)}, status = HTTP_400_BAD_REQUEST)





# edit product //req :  form   // res: ({res : 'msg' }) OR err
@csrf_exempt
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def edit_user_product(request):

    if Product.objects.filter(ID = request.POST["product_id"]).exists():
        # Get This Product
        this_product = get_object_or_404(Product, ID = request.POST["product_id"])
        if Shop.objects.filter(ID = this_product.FK_Shop.ID, FK_ShopManager = request.user).exists():

            try:
                Image = request.FILES["product_img"]
            except MultiValueDictKeyError:
                Image = ''

            try:
                Title = request.POST["product_title"]
            except:
                Title = ''

            try:
                Description = request.POST["product_description"]
            except:
                Description = ''
            
            try:
                This_Category = request.POST.get("product_category")
            except:
                This_Category = ''

            try:
                This_SubMarket = request.POST.get("product_submarket")
            except:
                This_SubMarket = ''
                
            try:
                Bio = request.POST["product_bio"]
            except:
                Bio = ''

            try:
                Story = request.POST["product_story"]
            except:
                Story = ''

            try:
                Price = request.POST["product_price"]
            except:
                Price = ''

            try:
                OldPrice = request.POST["product_oldprice"]
            except:
                OldPrice = ''

            try:
                Post_Range_Type = request.POST["product_post_range_type"]
            except:
                Post_Range_Type = ''

            try:
                Status = request.POST["product_status"]
            except:
                Status = ''
            
            try:
                Post_Range = request.POST.get("product_post_range")
            except:
                Post_Range = ''

            try:
                Exception_Post_Range = request.POST.get("product_exception_post_range")
            except:
                Exception_Post_Range = ''

            try:
                Net_Weight = request.POST["product_net_weight"]
            except:
                Net_Weight = ''

            try:
                Packing_Weight = request.POST["product_packing_weight"]
            except:
                Packing_Weight = ''

            try:
                Length_With_Packaging = request.POST["product_length_with_packaging"]
            except:
                Length_With_Packaging = ''

            try:
                Width_With_Packaging = request.POST["product_width_with_packaging"]
            except:
                Width_With_Packaging = ''

            try:
                Height_With_Packaging = request.POST["product_height_with_packaging"]
            except:
                Height_With_Packaging = ''

            try:
                Store_Inventory = request.POST["product_store_inventory"]
            except:
                Store_Inventory = ''

            alert = None
            if Alert.objects.filter(Part = '7', Slug = this_product.ID, Seen = False).exists():
                alert = get_object_or_404(Alert, Part = '7', Slug = this_product.ID, Seen = False)
                alert.FK_Field.all().delete()
            else:
                alert =Alert.objects.create(FK_User = request.user, Part = '7', Slug = this_product.ID)

            if (Title != '') and (Title != this_product.Title):
                TitleField = Field(Title = 'Title', Value = Title)
                TitleField.save()
                alert.FK_Field.add(TitleField)

            if (This_SubMarket != '') and (SubMarket.objects.filter(ID = This_SubMarket).exists()):
                if get_object_or_404(SubMarket, ID = This_SubMarket) != this_product.FK_SubMarket:
                    SubMarketField = Field(Title = 'SubMarket', Value = This_SubMarket)
                    SubMarketField.save()
                    alert.FK_Field.add(SubMarketField)

            if Image != '':
                this_product.NewImage = Image
                this_product.save()
                img_str = 'NewImage' + '#' + str(this_product.NewImage)
                ImageField = Field(Title = 'Image', Value = img_str)
                ImageField.save()
                alert.FK_Field.add(ImageField)

            if (Price != '') and (Price != str(this_product.Price)):
                PriceField = Field(Title = 'Price', Value = Price)
                PriceField.save()
                alert.FK_Field.add(PriceField)

            # Check Product Status            
            if Status == '1':
                if (Store_Inventory != '') and (int(Store_Inventory) != this_product.Inventory):
                    ProdInStoreField = Field(Title = 'ProdInStore', Value = Store_Inventory)
                    ProdInStoreField.save()
                    alert.FK_Field.add(ProdInStoreField)
            elif (Status == '4') or (Status == '3') or (Status == '2'):
                if int(this_product.Inventory) != 0:
                    ProdInStoreField = Field(Title = 'ProdInStore', Value = 0)
                    ProdInStoreField.save()
                    alert.FK_Field.add(ProdInStoreField)

            if (Status != '') and (Status != this_product.Status):
                StatusField = Field(Title = 'ProdPostType', Value = Status)
                StatusField.save()
                alert.FK_Field.add(StatusField)

            if (Description != '') and (Description != this_product.Description):
                DescriptionField = Field(Title = 'Description', Value = Description)
                DescriptionField.save()
                alert.FK_Field.add(DescriptionField)

            if (Bio != '') and (Bio != this_product.Bio):
                BioField = Field(Title = 'Bio', Value = Bio)
                BioField.save()
                alert.FK_Field.add(BioField)

            if (Story != '') and (Story != this_product.Story):
                StoryField = Field(Title = 'Story', Value = Story)
                StoryField.save()
                alert.FK_Field.add(StoryField)
            # Check Product Category
            Category_List = This_Category.split('~')
            Category_txt = ''
            for item in Category_List:
                try:
                    if Category.objects.filter(id = item).exists():
                        Category_txt += item + '-'
                except:
                    continue
                    
            CategoryField = Field(Title = 'Category', Value = Category_txt)
            CategoryField.save()
            alert.FK_Field.add(CategoryField)
            # Chech Product Post Range
            Post_Range_List = Post_Range.split('~')
            if len(Post_Range_List) != 0:
                Post_Range_txt = ''
                for item in Post_Range_List:
                    try:
                        if PostRange.objects.filter(id = item).exists():
                            Post_Range_txt += item + '-'
                    except:
                        continue

                PostRangeField = Field(Title = 'PostRange', Value = Post_Range_txt)
                PostRangeField.save()
                alert.FK_Field.add(PostRangeField)
            else:
                PostRangeField = Field(Title = 'PostRange', Value = 'remove')
                PostRangeField.save()
                alert.FK_Field.add(PostRangeField)
            # Check Product Exception Post Range
            Exception_Post_Range_List = Exception_Post_Range.split('~')               
            if len(Exception_Post_Range_List) != 0:
                Exe_Post_Range_txt = ''
                for item in Exception_Post_Range_List:
                    try:
                        if PostRange.objects.filter(id = item).exists():
                            Exe_Post_Range_txt += item + '-'
                    except:
                        continue

                ExePostRangeField = Field(Title = 'ExePostRange', Value = Exe_Post_Range_txt)
                ExePostRangeField.save()
                alert.FK_Field.add(ExePostRangeField)
            else:
                ExePostRangeField = Field(Title = 'ExePostRange', Value = 'remove')
                ExePostRangeField.save()
                alert.FK_Field.add(ExePostRangeField)

            if OldPrice != '':
                if OldPrice != this_product.OldPrice:
                    OldPriceField = Field(Title = 'OldPrice', Value = OldPrice)
                    OldPriceField.save()
                    alert.FK_Field.add(OldPriceField)
            else:
                OldPriceField = Field(Title = 'OldPrice', Value = '0')
                OldPriceField.save()
                alert.FK_Field.add(OldPriceField)

            if Post_Range_Type != this_product.PostRangeType:
                ProdRangeField = Field(Title = 'ProdRange', Value = Post_Range_Type)
                ProdRangeField.save()
                alert.FK_Field.add(ProdRangeField)
            # Product Weight Info
            if (Net_Weight != '') and (Net_Weight != this_product.Net_Weight):
                ProdNet_WeightField = Field(Title = 'ProdNetWeight', Value = Net_Weight)
                ProdNet_WeightField.save()
                alert.FK_Field.add(ProdNet_WeightField)
            if (Packing_Weight != '') and (Packing_Weight != this_product.Weight_With_Packing):
                ProdPacking_Weight = Field(Title = 'ProdPackingWeight', Value = Packing_Weight)
                ProdPacking_Weight.save()
                alert.FK_Field.add(ProdPacking_Weight)
            # Product Dimensions Info
            if (Length_With_Packaging != '') and (Length_With_Packaging != this_product.Length_With_Packaging):
                ProdLength_With_Packaging = Field(Title = 'ProdLengthWithPackaging', Value = Length_With_Packaging)
                ProdLength_With_Packaging.save()
                alert.FK_Field.add(ProdLength_With_Packaging)
            if (Width_With_Packaging != '') and (Width_With_Packaging != this_product.Width_With_Packaging):
                ProdWidth_With_Packaging = Field(Title = 'ProdWidthWithPackaging', Value = Width_With_Packaging)
                ProdWidth_With_Packaging.save()
                alert.FK_Field.add(ProdWidth_With_Packaging)
            if (Height_With_Packaging != '') and (Height_With_Packaging != this_product.Height_With_Packaging):
                ProdHeight_With_Packaging = Field(Title = 'ProdHeightWithPackaging', Value = Height_With_Packaging)
                ProdHeight_With_Packaging.save()
                alert.FK_Field.add(ProdHeight_With_Packaging)

            if (alert.FK_Field.all().count() == 0):
                alert.FK_Field.all().delete()
                alert.delete()
                return JsonResponse({'res' : 'تغییری ایجاد نکرده اید!'} , status = HTTP_400_BAD_REQUEST)
            else:
                return JsonResponse({'res' : 'تغییرات شما انجام شد!'} , status = HTTP_200_OK)
        else:
            return JsonResponse({'res' : 'شما محصولی با این مشخصات ندارید!'} , status = HTTP_404_NOT_FOUND)
    else:
        return JsonResponse({'res' : 'محصولی با این مشخصات یافت نشد!'} , status = HTTP_404_NOT_FOUND)





# add product attribute //req :  form   // res: ({res : 'msg' }) OR err
@csrf_exempt
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_product_attribute(request):

    if Product.objects.filter(ID = request.POST["product_id"]).exists():
        # Get This Product
        this_product = get_object_or_404(Product, ID = request.POST["product_id"])
        if Shop.objects.filter(ID = this_product.FK_Shop.ID, FK_ShopManager = request.user).exists():
            # Get Data
            try:
                Attribute_id = request.POST.get('attribute_id')
            except:
                Attribute_id = ''
            try:
                Value = request.POST.get('attribute_value')
            except:
                Value = ''
            
            try:
                if (Attribute.objects.filter(id = Attribute_id).exists()) and (Value != ''):
                    # Set Data
                    this_attribute = Attribute.objects.get(id = Attribute_id)
                    attrproduct = AttrProduct.objects.create(FK_Product = this_product, FK_Attribute = this_attribute, Value = Value)
                    # Set Alert
                    Alert.objects.create(FK_User = request.user, Part = '11', Slug = attrproduct.id)

                    return JsonResponse({'res' : 'ویژگی ثبت شد!'}, status = HTTP_201_CREATED)
                else:
                    return JsonResponse({'res' : 'ویژگی با این id یا مقدار ویژگی خالی است!'}, status = HTTP_400_BAD_REQUEST)
            except:
                return JsonResponse({'res' : 'خطایی رخ داده است...'}, status = HTTP_400_BAD_REQUEST)
        else:
            return JsonResponse({'res' : 'شما حجره ای با این مشخصات ندارید!'}, status= HTTP_400_BAD_REQUEST)
    else:
        return JsonResponse({'res' : 'محصولی با این مشخصات یافت نشد!'}, status = HTTP_404_NOT_FOUND)




# add new attribute //req :  form   // res: ({res : 'msg' }) OR err
@csrf_exempt
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_new_attribute(request):

    if Shop.objects.filter(FK_ShopManager = request.user).exists():
        # Get Data
        try:
            Attribute_Title = request.POST.get('attribute_title')
        except:
            Attribute_Title = ''
        try:
            Attribute_Value = request.POST.get('attribute_value')
        except:
            Attribute_Value = ''

        try:
            if (Attribute_Title != '') and (Attribute_Value != '') and not (Attribute.objects.filter(Title = Attribute_Title, Unit = Attribute_Value).exists()):
                this_attribute = Attribute.objects.create(Title = Attribute_Title, Unit = Attribute_Value)
                Alert.objects.create(FK_User = request.user, Part = '10', Slug = this_attribute.id)
                return JsonResponse({'res' : 'True'}, status = HTTP_201_CREATED)
            else:
                return JsonResponse({'res' : 'False'}, status = HTTP_400_BAD_REQUEST)
        except Exception as e:
            return JsonResponse({'res' :str(e)}, status = HTTP_400_BAD_REQUEST)



# delete product attribute //req :  form   // res: ({res : 'msg' }) OR err
@csrf_exempt
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def delete_product_attribute(request):

    if AttrProduct.objects.filter(id = request.POST["attribute_id"]).exists():
        try:
            # Get This Product Attribute
            this_attrProduct = get_object_or_404(AttrProduct, id = request.POST["attribute_id"])
            if Shop.objects.filter(FK_ShopManager = this_attrProduct.FK_Product.FK_Shop.FK_ShopManager.id).exists():
                # Delete Data
                this_attrProduct.Available = False
                this_attrProduct.save()
                # Set Alert
                Alert.objects.create(Part = '24', FK_User = request.user, Slug = this_attrProduct.id)
                return JsonResponse({'res' : 'ویژگی محصول شما حذف شد'}, status = HTTP_200_OK)
            else:
                return JsonResponse({'res' : 'محصول و حجره برای شما ثبت نشده است...'}, status = HTTP_404_NOT_FOUND)
        except Exception as e:
            return JsonResponse({'res' :str(e)}, status = HTTP_400_BAD_REQUEST)
    else:
        return JsonResponse({'res' : 'ویژگی با این مشخصات یافت نشد...'}, status = HTTP_404_NOT_FOUND)





# get all attribute //req :  // res:  OR err
@csrf_exempt
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_all_attribute(request):
    try:
        attribute_list = Attribute.objects.filter(Publish = True)
        serializer = AttributeSerializer(attribute_list, many = True)
        return JsonResponse(serializer.data, status = HTTP_200_OK, safe = False)
    except Exception as e:
        return JsonResponse({'res' :str(e)}, status = HTTP_400_BAD_REQUEST)





# get all product attribute //req : product_id  // res:  OR err
@csrf_exempt
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def get_product_attribute(request):
    if Product.objects.filter(ID = request.POST["product_id"]).exists():
        # Get This Product
        this_product = get_object_or_404(Product, ID = request.POST["product_id"])
        if Shop.objects.filter(ID = this_product.FK_Shop.ID, FK_ShopManager = request.user).exists():
            try:
                product_attribute_list = AttrProduct.objects.filter(FK_Product = this_product, Available = True)
                serializer = AttrProductSerializer(product_attribute_list, many = True)
                return JsonResponse(serializer.data, status = HTTP_200_OK, safe = False)
            except Exception as e:
                return JsonResponse({'res' :str(e)}, status = HTTP_400_BAD_REQUEST)
        else:
            return JsonResponse({'res' : 'عدم دسترسی...'}, status = HTTP_404_NOT_FOUND)
    else:
        return JsonResponse({'res' : 'محصولی با این ویژگی ها یافت نشد...'}, status = HTTP_404_NOT_FOUND)





# get all product attribute price //req : product_id  // res:  OR err
@csrf_exempt
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def get_product_price_attribute(request):
    if Product.objects.filter(ID = request.POST["product_id"]).exists():
        # Get This Product
        this_product = get_object_or_404(Product, ID = request.POST["product_id"])
        if Shop.objects.filter(ID = this_product.FK_Shop.ID, FK_ShopManager = request.user).exists():
            try:
                product_price_attribute_list = AttrPrice.objects.filter(FK_Product = this_product, Publish = True)
                serializer = AttrPriceSerializer(product_price_attribute_list, many = True)
                return JsonResponse(serializer.data, status = HTTP_200_OK, safe = False)
            except Exception as e:
                return JsonResponse({'res' :str(e)}, status = HTTP_400_BAD_REQUEST)
        else:
            return JsonResponse({'res' : 'عدم دسترسی...'}, status = HTTP_404_NOT_FOUND)
    else:
        return JsonResponse({'res' : 'محصولی با این ویژگی ها یافت نشد...'}, status = HTTP_404_NOT_FOUND)





# change product attribute price status //req : price_attribute_id  // res:  OR err
@csrf_exempt
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def change_product_price_attribute_status(request):
    if AttrPrice.objects.filter(id = request.POST["price_attribute_id"]).exists():
        # Get This Price Attribute
        this_price_attribute = AttrPrice.objects.get(id = request.POST["price_attribute_id"])
        # Get This Product
        this_product = this_price_attribute.FK_Product
        if Shop.objects.filter(ID = this_product.FK_Shop.ID, FK_ShopManager = request.user).exists():
            try:
                if this_price_attribute.Available:
                    this_price_attribute.Available = False
                    this_price_attribute.save()
                else:
                    this_price_attribute.Available = True
                    this_price_attribute.save()
                return JsonResponse({'res' : 'True'}, status = HTTP_200_OK, safe = False)
            except Exception as e:
                return JsonResponse({'res' :str(e)}, status = HTTP_400_BAD_REQUEST)
        else:
            return JsonResponse({'res' : 'عدم دسترسی...'}, status = HTTP_404_NOT_FOUND)
    else:
        return JsonResponse({'res' : 'ارزش ویژگی با این مشخصات یافت نشد...'}, status = HTTP_404_NOT_FOUND)

        



# add product price attribute //req : product_id   // res: ({res : 'msg' }) OR err
@csrf_exempt
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_product_price_attribute(request):
    if Product.objects.filter(ID = request.POST["product_id"]).exists():
        # Get This Product
        this_product = get_object_or_404(Product, ID = request.POST["product_id"])
        if Shop.objects.filter(ID = this_product.FK_Shop.ID, FK_ShopManager = request.user).exists():
            # Get Data
            try:
                AttrPrice_Value = request.POST.get('attributePrice_value')
            except :
                AttrPrice_Value = ''

            try:
                AttrPrice_Exp = request.POST.get('attributePrice_exp')
            except :
                AttrPrice_Exp = ''

            try:
                AttrPrice_Unit = request.POST.get('attributePrice_unit')
            except :
                AttrPrice_Unit = ''

            try:
                AttrPrice_Des = request.POST.get('attributePrice_des')
            except :
                AttrPrice_Des = ''
            # Set Data
            try:
                if (AttrPrice_Value != '') and (AttrPrice_Exp != '') and (AttrPrice_Unit != '') and not (AttrPrice.objects.filter(FK_Product = this_product, Value = AttrPrice_Value, ExtraPrice = AttrPrice_Exp, Unit = AttrPrice_Unit).exists()):
                    if AttrPrice_Des == '':
                        this_price_attribute = AttrPrice.objects.create(FK_Product = this_product, Value = AttrPrice_Value, ExtraPrice = AttrPrice_Exp, Unit = AttrPrice_Unit, Publish = False)
                    else:
                        this_price_attribute = AttrPrice.objects.create(FK_Product = this_product, Value = AttrPrice_Value, ExtraPrice = AttrPrice_Exp, Unit = AttrPrice_Unit, Description = AttrPrice_Des, Publish = False)
                    Alert.objects.create(Part = '17', FK_User = request.user, Slug = this_price_attribute.id)
                    return JsonResponse({'res' : 'True'}, status = HTTP_201_CREATED)
                else:
                    return JsonResponse({'res' : 'عنوان - واحد - قسمت اضافه اجباری - این ارزش ویژگی موجود است...'}, status = HTTP_400_BAD_REQUEST)
            except Exception as e:
                return JsonResponse({'res' :str(e)}, status = HTTP_400_BAD_REQUEST)
        else:
            return JsonResponse({'res' : 'عدم دسترسی...'}, status = HTTP_404_NOT_FOUND)
    else:
        return JsonResponse({'res' : 'محصولی با این ویژگی ها یافت نشد...'}, status = HTTP_404_NOT_FOUND)






# delete product price attribute //req : price_attribute_id   // res: ({res : 'msg' }) OR err
@csrf_exempt
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def delete_product_price_attribute(request):
    if AttrPrice.objects.filter(id = request.POST["price_attribute_id"]).exists():
        # Get This Price Attribute
        this_price_attribute = AttrPrice.objects.get(id = request.POST["price_attribute_id"])
        # Get This Product
        this_product = this_price_attribute.FK_Product
        if Shop.objects.filter(ID = this_product.FK_Shop.ID, FK_ShopManager = request.user).exists():
            try:
                # Change Status
                this_price_attribute.Publish = False
                this_price_attribute.save()
                # Set Alert
                Alert.objects.create(Part = '25', FK_User = request.user, Slug = this_price_attribute.id)
                return JsonResponse({'res' : 'حذف شد...'}, status = HTTP_200_OK)
            except Exception as e:
                return JsonResponse({'res' :str(e)}, status = HTTP_400_BAD_REQUEST)
        else:
            return JsonResponse({'res' : 'عدم دسترسی...'}, status = HTTP_404_NOT_FOUND)
    else:
        return JsonResponse({'res' : 'ارزش ویژگی با این مشخصات یافت نشد...'}, status = HTTP_404_NOT_FOUND)






# get product all banner //req : product_id  // res:  OR err
@csrf_exempt
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def get_product_all_banner(request):
    if Product.objects.filter(ID = request.POST["product_id"]).exists():
        # Get This Product
        this_product = get_object_or_404(Product, ID = request.POST["product_id"])
        if Shop.objects.filter(ID = this_product.FK_Shop.ID, FK_ShopManager = request.user).exists():
            try:
                this_product_banner_list = ProductBanner.objects.filter(FK_Product = this_product, Publish = True)
                serializer = ProductBannerSerializer(this_product_banner_list, many = True)
                return JsonResponse(serializer.data, status = HTTP_200_OK, safe = False)
            except Exception as e:
                return JsonResponse({'res' : str(e)}, status = HTTP_400_BAD_REQUEST)
        else:
            return JsonResponse({'res' : 'عدم دسترسی...'}, status = HTTP_404_NOT_FOUND)
    else:
        return JsonResponse({'res' : 'محصولی با این مشخصات پیدا نشد...'}, status = HTTP_404_NOT_FOUND)






# add product banner //req : product_id   // res: ({res : 'msg' }) OR err
@csrf_exempt
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_product_banner(request):
    if Product.objects.filter(ID = request.POST["product_id"]).exists():
        # Get This Product
        this_product = get_object_or_404(Product, ID = request.POST["product_id"])
        if Shop.objects.filter(ID = this_product.FK_Shop.ID, FK_ShopManager = request.user).exists():
            # Get Data
            try:
                Banner_Image = request.FILES["banner_image"]
            except MultiValueDictKeyError:
                Banner_Image = ''

            try:
                if Banner_Image != '':
                    this_banner = ProductBanner.objects.create(FK_Product = this_product, Image = Banner_Image)
                    # Set Alert
                    Alert.objects.create(FK_User = request.user, Part = '8', Slug = this_banner.id)
                    return JsonResponse({'res' : 'ثبت شد...'}, status = HTTP_200_OK)
                else:
                    return JsonResponse({'res' : 'فیلد عکس نمی تواند خالی باشد...'}, status = HTTP_400_BAD_REQUEST)
            except Exception as e:
                return JsonResponse({'res' : str(e)}, status = HTTP_400_BAD_REQUEST)
        else:
            return JsonResponse({'res' : 'عدم دسترسی...'}, status = HTTP_404_NOT_FOUND)
    else:
        return JsonResponse({'res' : 'محصولی با این مشخصات پیدا نشد...'}, status = HTTP_404_NOT_FOUND)





# delete product banner //req : banner_id   // res: ({res : 'msg' }) OR err
@csrf_exempt
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def delete_product_banner(request):
    if ProductBanner.objects.filter(id = request.POST["banner_id"]).exists():
        # Get This Banner
        this_banner = ProductBanner.objects.get(id = request.POST["banner_id"])
        # Get This Product
        this_product = this_banner.FK_Product
        if Shop.objects.filter(ID = this_product.FK_Shop.ID, FK_ShopManager = request.user).exists():
            this_banner.Publish = False
            this_banner.save()
            # Set Alert
            Alert.objects.create(FK_User = request.user, Part = '23', Slug = this_banner.id)
            return JsonResponse({'res' : 'حذف شد...'}, status = HTTP_200_OK)
        else:
            return JsonResponse({'res' : 'عدم دسترسی...'}, status = HTTP_404_NOT_FOUND)
    else:
        return JsonResponse({'res' : 'بنری با این مشخصات یافت نشد...'}, status = HTTP_404_NOT_FOUND)





# change product banner status //req : banner_id   // res: ({res : 'msg' }) OR err
@csrf_exempt
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def change_product_banner_status(request):
    if ProductBanner.objects.filter(id = request.POST["banner_id"]).exists():
        # Get This Banner
        this_banner = ProductBanner.objects.get(id = request.POST["banner_id"])
        # Get This Product
        this_product = this_banner.FK_Product
        if Shop.objects.filter(ID = this_product.FK_Shop.ID, FK_ShopManager = request.user).exists():
            # Change Status
            if this_banner.Available:
                this_banner.Available = False
                this_banner.save()
            else:
                this_banner.Available = True
                this_banner.save()
            return JsonResponse({'res' : 'تغییر کرد...'}, status = HTTP_200_OK)
        else:
            return JsonResponse({'res' : 'عدم دسترسی...'}, status = HTTP_404_NOT_FOUND)
    else:
        return JsonResponse({'res' : 'بنری با این مشخصات یافت نشد...'}, status = HTTP_404_NOT_FOUND)






# detail banner shop //req : shop_slug  // res:  OR err
@csrf_exempt
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def get_shop_banner(request):
    if Shop.objects.filter(FK_ShopManager = request.user).count() != 0:
        try:
            shop_ID = request.POST.get('shop_id')
            
            if Shop.objects.filter(ID = shop_ID, FK_ShopManager = request.user).count() != 0 :
            
                shopbanner = ShopBanner.objects.filter(FK_Shop = shop_ID)
                serializer = ShopBannerSerializer(shopbanner, many = True)
                return JsonResponse(serializer.data, status = HTTP_200_OK, safe = False)
            else :
                return JsonResponse({'res' : 'Error getting data'}, status = HTTP_400_BAD_REQUEST)
        except:
            return JsonResponse({'res' : 'Error getting data'}, status = HTTP_400_BAD_REQUEST)
    
    else:
        return JsonResponse({'res' : 'You dont have any shops'}, status = HTTP_404_NOT_FOUND)




# send barcode post for factor //req : shop_slug  // res:  OR err
@csrf_exempt
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def barcodepost_for_factor(request):
    # Get User All Product
    pubproduc = Product.objects.filter(FK_Shop__in = Shop.objects.filter(FK_ShopManager = request.user))
    # Check User Factor For Send
    factors_post_status_three = []
    for item in FactorPost.objects.filter(ProductStatus = '3', FK_Product__in = pubproduc):
        factors_post_status_three.append(item)
    factors_post_status_three = list(dict.fromkeys(factors_post_status_three))
    if len(factors_post_status_three) != 0:
        try:
            Factor_id = request.POST.get('factor_id')
        except:
            Factor_id = ''

        try:
            Barcode_Send = request.POST.get('post_barcode')
        except:
            Barcode_Send = ''

        try:
            Price_Send = request.POST.get('post_price')
        except:
            Price_Send = ''

        try:
            User_Send = request.POST.get('post_usersend')
        except:
            User_Send = ''
            
        if (Barcode_Send != '') and (len(Barcode_Send) == 24) and (Price_Send != '') and (User_Send != '') and (Factor_id != ''):
            if (PostBarCode.objects.filter(FK_Factor = Factor.objects.get(ID = Factor_id), BarCode = Barcode_Send, User_Sender = User_Send).count() == 0):
                # Add Barcode
                barcode = PostBarCode.objects.create(FK_Factor = Factor.objects.get(ID = Factor_id), User_Sender = User_Send, PostPrice = Price_Send, BarCode = Barcode_Send)
                # Set Alert
                Alert.objects.create(Part = '21', FK_User = request.user, Slug = barcode.id)
                return JsonResponse({'res' : 'بارکدپستی ثبت شد...'}, status = HTTP_200_OK)
            else:
                return JsonResponse({'res' : 'این اطلاعات تکراری می باشد...'}, status = HTTP_400_BAD_REQUEST)
        else:
            return JsonResponse({'res' : 'مقادیر وارد شده صحیح نمی باشد...'}, status = HTTP_400_BAD_REQUEST)
    else:
        return JsonResponse({'res' : 'عدم دسترسی...'}, status = HTTP_400_BAD_REQUEST)




# accept factor product for factor //req : shop_slug  // res:  OR err
@csrf_exempt
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def accept_factor_product(request):
    try:
        Factor_id = request.POST.get('factor_id')
    except :
        Factor_id = ''

    try:
        # Get Factor Info
        factor = get_object_or_404(Factor, ID = Factor_id)
        # Factor Post List
        factor_item = []

        for item in factor.FK_FactorPost.all():
            for shop in Shop.objects.filter(FK_ShopManager = request.user):
                if item.FK_Product.FK_Shop == shop:
                    factor_item.append(item)

        factor_item = list(dict.fromkeys(factor_item))
        # Change Factor Status
        for item in factor_item:
            item.ProductStatus = '2'
            item.save()
        # Get Factor Status
        factor_status = True
        # Get All Factor Item Status Is Not = 0
        items = []
        for item in factor.FK_FactorPost.all():
            if item.ProductStatus != '0':
                items.append(item)
        # Chenge Factor Status
        for item in items:
            if item.ProductStatus != '2':
                factor_status = False
        # Set Factor Status
        if factor_status == True:
            factor.OrderStatus = '2'
            factor.save()
        # Set Alert
        if Alert.objects.filter(Part = '20', FK_User = request.user, Slug = ID).exists():
            return JsonResponse({'res' : 'شما قبلا این فاکتور را ثبت کرده اید'} , status = HTTP_400_BAD_REQUEST)
        else:
            Alert.objects.create(Part = '20', FK_User = request.user, Slug = ID)
            return JsonResponse({'res' : 'فاکتور با موفقیت، تایید شد.'} , status = HTTP_200_OK)
    
    except Exception as e:
        return JsonResponse({'res' :str(e)}, status = HTTP_400_BAD_REQUEST)




# accept factor product for factor //req : shop_slug  // res:  OR err
@csrf_exempt
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def cancel_factor_product(request):
    try:
        Factor_id = request.POST.get('factor_id')
    except :
        Factor_id = ''

    try:
        # Get Factor Info
        factor = Factor.objects.get(ID = Factor_id)
        # Factor Item
        factor_item = []

        for item in factor.FK_FactorPost.all():
            for shop in Shop.objects.filter(FK_ShopManager = request.user):
                if item.FK_Product.FK_Shop == shop:
                    factor_item.append(item)

        factor_item = list(dict.fromkeys(factor_item))
        # Change Factor Item Status
        for item in factor_item:
            item.ProductStatus = '0'
            if item.FK_Product.Status == '1':
                item.FK_Product.Inventory += item.ProductCount
                item.FK_Product.save()
            item.save()
        # Get Factor Status
        factor_status = True

        for item in factor.FK_FactorPost.all():
            if item.ProductStatus != '0':
                factor_status = False

        if factor_status == True:
            factor.OrderStatus = '4'
            factor.save()
        # Set Alert
        if Alert.objects.filter(Part = '13', FK_User = request.user, Slug = factor.ID).exists():
            return JsonResponse({'res' : 'شما قبلا این فاکتور را ثبت کرده اید!'} , status = HTTP_400_BAD_REQUEST)
        else:
            Alert.objects.create(Part = '13', FK_User = request.user, Slug = factor.ID)
            return JsonResponse({'res' : 'فاکتور با موفقیت، لغو شد.'} , status = HTTP_200_OK)
    except Exception as e:
        return JsonResponse({'res' :str(e)}, status = HTTP_400_BAD_REQUEST)






# get user message  //req : request.user  // res: message list OR err
@csrf_exempt
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_message_status_is_false(request):
    # Get User Message
    user_message_list = []
    for item in Message.objects.filter(Type = True).order_by('-Date'):
        try:
            if item.FK_Users.filter(FK_User = request.user, SeenStatus = False).exists():
                user_message_list.append(item)
        except:
            continue
    serializer = MessageSerializer(user_message_list, many = True)
    return JsonResponse(serializer.data, status = HTTP_200_OK, safe = False)





# get user message  //req : request.user  // res: message list OR err
@csrf_exempt
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_message_status_is_true(request):
    # Get User Message
    user_message_list = []
    for item in Message.objects.filter(Type = True).order_by('-Date'):
        try:
            if item.FK_Users.filter(FK_User = request.user, SeenStatus = True).exists():
                user_message_list.append(item)
        except:
            continue
    serializer = MessageSerializer(user_message_list, many = True)
    return JsonResponse(serializer.data, status = HTTP_200_OK, safe = False)





# change message status //req : message_id  // res: message list OR err
@csrf_exempt
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def change_message_status(request):
    # Get All User Message When Seen == False
    for item in Message.objects.filter(Type = True).order_by('-Date'):
        try:
            if item.FK_Users.filter(FK_User = request.user, SeenStatus = False).exists():
                this = item.FK_Users.get(FK_User = request.user, SeenStatus = False)
                this.SeenStatus = True 
                this.save()
        except:
            continue
    return JsonResponse({'res' : 'تغییر کرد...'}, status = HTTP_200_OK)







# //////////// web cart navbar view

#detail factor //req : request.user // res: (factor & factorpost detail) OR err
@csrf_exempt
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_factor_products(request):
    try:
        user_factor = Factor.objects.filter(FK_User = request.user, PaymentStatus = False)[0]
        serializer = FactorCartView(user_factor)
        return JsonResponse(serializer.data, status = HTTP_200_OK)
    except:
        return JsonResponse({'err' : 'محصولی در سبد خرید خود ندارید ...'}, status = HTTP_404_NOT_FOUND)



@csrf_exempt
@api_view(["GET"])
@permission_classes([AllowAny,])
def add_to_basket(request):

    if request.user.is_authenticated :
        try:
            product_ID = request.POST.get('prod_id')
        except:
            return JsonResponse({'res' : 'محصولی یافت نشد ...'} , status=HTTP_404_NOT_FOUND )
            
        item = get_object_or_404(Product, ID = product_ID)

        if item.Status != '4':
            Factor_qs = Factor.objects.filter(FK_User = request.user, PaymentStatus = False)
            if Factor_qs.exists():
                order = Factor_qs[0]
                try:
                    Factor_item = order.FK_FactorPost.filter(
                        FK_Product = item,
                        FK_User = request.user,
                    )
                    for j in Factor_item:
                        if j.FK_AttrPrice.count() == 0:
                            Factor_item = j

                    Factor_item.ProductCount += 1
                    Factor_item.save()
                    # Chech Coupon
                    if order.FK_Coupon != None:
                        if order.get_total_coupon_test(order.FK_Coupon.id) < int(order.FK_Coupon.MinimumAmount):
                            order.FK_Coupon = None
                            order.save()

                    return JsonResponse({'res' : 'محصول به سبد خرید شما اضافه شد ...'} , status=HTTP_200_OK)
                except:
                    Factor_item = FactorPost(FK_Product = item, FK_User = request.user)
                    Factor_item.save()

                    order.FK_FactorPost.add(Factor_item)
                    order.save()
                    # Chech Coupon
                    if order.FK_Coupon != None:
                        if order.get_total_coupon_test(order.FK_Coupon.id) < int(order.FK_Coupon.MinimumAmount):
                            order.FK_Coupon = None
                            order.save()

                    return JsonResponse({'res' : 'محصول به سبد خرید شما اضافه شد ...'} , status=HTTP_200_OK)
            else:
                order = Factor.objects.create(FK_User = request.user, PaymentStatus = False)
                Factor_item = FactorPost(FK_Product = item, FK_User = request.user)
                Factor_item.save()

                order.FK_FactorPost.add(Factor_item)
                order.save()

                return JsonResponse({'res' : 'محصول به سبد خرید شما اضافه شد ...'} , status=HTTP_200_OK)
        else:
            return JsonResponse({'err' : 'محصول مدنظر شما در حال حاضر موجود نمی باشد!'} , status = HTTP_404_NOT_FOUND)   
    else:
        return JsonResponse({'res' : 'برای افزودن محصول به سبد خرید ابتدا وارد حساب کاربری خود در بازار نخل شوید.'}, status = HTTP_400_BAD_REQUEST)





# set check out //req : request.user // res:  OR err
@csrf_exempt
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_check_out(request):
    try:
        # Get All Product
        pubproduc = Product.objects.filter(FK_Shop__in = Shop.objects.filter(FK_ShopManager = request.user))
        # Get User Is Shoper Or Not
        if Shop.objects.filter(FK_ShopManager = request.user).exists():
            showshopfactor = True
        else:
            showshopfactor = False

        factor_items_post_status_three = []
        factors_post_status_three = []

        if showshopfactor:
            for item in FactorPost.objects.filter(ProductStatus = '3', FK_Product__in = pubproduc):
                factor_items_post_status_three.append(item)

        factors_post_status_three = Factor.objects.filter(PaymentStatus = True, Publish = True, FK_FactorPost__in = factor_items_post_status_three)
        factors_post_status_three = list(dict.fromkeys(factors_post_status_three))
        
        if len(factors_post_status_three) != 0:
            try:
                Description = request.POST.get('check_out_description')
            except :
                Description = ''

            Alert.objects.create(Part = '31', FK_User = request.user, Slug = Description)
            return JsonResponse({'res' : 'ثبت شد...'}, status = HTTP_200_OK)
        else:
            return JsonResponse({'res' : 'عدم دسترسی...'}, status = HTTP_200_OK)
    except Exception as e:
        return JsonResponse({'res' : str(e)}, status = HTTP_400_BAD_REQUEST)






# get shop view in //req : request.user  // res: data OR err

# Functions
class get_shop_view_in_seven_day(threading.Thread):
    def run(self, id):
        # View In Seven Day
        day_list = []
        # Get Shop View
        this_shop = get_object_or_404(ShopViews, FK_Shop = id)
        # Get To Day
        to_day = datetime.date.today()
        # Get View When Index = 0
        try:
            day_list.append(this_shop.FK_Date.get(Date = to_day).Count)
        except:
            day_list.append('0')
        # Get View When 1 < Index < 7
        for i in range(1, 7):
            try:
                day_past = datetime.timedelta(days = int(i))
                this_date = to_day - day_past
                day_list.append(this_shop.FK_Date.get(Date = this_date).Count)
            except:
                day_list.append('0')
        return day_list

class get_shop_view_in_seven_week(threading.Thread):
    def run(self, id):
        # View In Seven Day
        week_list = []
        # Sum View In This Week
        sum_view_in_this_week = 0
        # Get Shop View
        this_shop = get_object_or_404(ShopViews, FK_Shop = id)
        # Get To Day
        to_day = datetime.date.today()
        # Get View When Index = 0
        first_start_day_in_week = None
        first_end_day_in_week = None
        try:
            # Get Day In Week
            if to_day.weekday() == 0:
                # Set Start Week
                day_past = datetime.timedelta(days = 2)
                first_start_day_in_week = to_day - day_past
                # Set End Week
                day_past = datetime.timedelta(days = 6)
                first_end_day_in_week = first_start_day_in_week + day_past
                # Get View In Range
                for item in this_shop.FK_Date.filter(Date__range = [first_start_day_in_week, first_first_end_day_in_week]):
                    sum_view_in_this_week += int(item.Count)
                week_list.append(str(sum_view_in_this_week))
            elif to_day.weekday() == 1:
                # Set Start Week
                day_past = datetime.timedelta(days = 3)
                first_start_day_in_week = to_day - day_past
                # Set End Week
                day_past = datetime.timedelta(days = 6)
                first_end_day_in_week = first_start_day_in_week + day_past
                # Get View In Range
                for item in this_shop.FK_Date.filter(Date__range = [first_start_day_in_week, first_end_day_in_week]):
                    sum_view_in_this_week += int(item.Count)
                week_list.append(str(sum_view_in_this_week))
            elif to_day.weekday() == 2:
                # Set Start Week
                day_past = datetime.timedelta(days = 4)
                first_start_day_in_week = to_day - day_past
                # Set End Week
                day_past = datetime.timedelta(days = 6)
                first_end_day_in_week = first_start_day_in_week + day_past
                # Get View In Range
                for item in this_shop.FK_Date.filter(Date__range = [first_start_day_in_week, first_end_day_in_week]):
                    sum_view_in_this_week += int(item.Count)
                week_list.append(str(sum_view_in_this_week))
            elif to_day.weekday() == 3:
                # Set Start Week
                day_past = datetime.timedelta(days = 5)
                first_start_day_in_week = to_day - day_past
                # Set End Week
                day_past = datetime.timedelta(days = 6)
                first_end_day_in_week = first_start_day_in_week + day_past
                # Get View In Range
                for item in this_shop.FK_Date.filter(Date__range = [first_start_day_in_week, first_end_day_in_week]):
                    sum_view_in_this_week += int(item.Count)
                week_list.append(str(sum_view_in_this_week))
            elif to_day.weekday() == 4:
                # Set Start Week
                day_past = datetime.timedelta(days = 6)
                first_start_day_in_week = to_day - day_past
                # Set End Week
                day_past = datetime.timedelta(days = 6)
                first_end_day_in_week = first_start_day_in_week + day_past
                # Get View In Range
                for item in this_shop.FK_Date.filter(Date__range = [first_start_day_in_week, first_end_day_in_week]):
                    sum_view_in_this_week += int(item.Count)
                week_list.append(str(sum_view_in_this_week))
            elif to_day.weekday() == 5:
                # Set Start Week
                first_start_day_in_week = to_day
                # Set End Week
                day_past = datetime.timedelta(days = 6)
                first_end_day_in_week = first_start_day_in_week + day_past
                # Get View In Range
                for item in this_shop.FK_Date.filter(Date__range = [first_start_day_in_week, first_end_day_in_week]):
                    sum_view_in_this_week += int(item.Count)
                week_list.append(str(sum_view_in_this_week))
            elif to_day.weekday() == 6:
                # Set Start Week
                day_past = datetime.timedelta(days = 1)
                first_start_day_in_week = to_day - day_past
                # Set End Week
                day_past = datetime.timedelta(days = 6)
                first_end_day_in_week = first_start_day_in_week + day_past
                # Get View In Range
                for item in this_shop.FK_Date.filter(Date__range = [first_start_day_in_week, first_end_day_in_week]):
                    sum_view_in_this_week += int(item.Count)
                week_list.append(str(sum_view_in_this_week))
        except:
            week_list.append('0')
        # Get View When 0 <= Index < 7
        for i in range(1, 7):
            # Set Zero
            sum_view_in_this_week = 0
            start_day_in_week = None
            end_day_in_week = None
            try:
                # Set Start And End Week
                day_past = datetime.timedelta(days = (i * 7))
                start_day_in_week = first_start_day_in_week - day_past
                end_day_in_week = first_end_day_in_week - day_past
                # Get View In Range
                for item in this_shop.FK_Date.filter(Date__range = [start_day_in_week, end_day_in_week]):
                    sum_view_in_this_week += int(item.Count)
                week_list.append(str(sum_view_in_this_week))
            except:
                week_list.append('0')
        return week_list

class get_shop_view_in_seven_month(threading.Thread):
    def run(self, id):
        # View In Seven Day
        month_list = []
        # Sum View In This Month
        sum_view_in_this_month = 0
        # Set All Month End Day
        month_end_day = {
            "January": 31,
            "February": 29,
            "March": 31,
            "April": 30,
            "May": 31,
            "June": 30,
            "July": 31,
            "August": 31,
            "September": 30,
            "October": 31,
            "November": 30,
            "December": 31,
        }
        # Get Shop View
        this_shop = get_object_or_404(ShopViews, FK_Shop = id)
        # Get To Day
        to_day = datetime.date.today()
        # Get View When Index = 0
        try:
            first_start_day_in_month = "%d-%d-%d" % (to_day.year, to_day.month, 1)
            first_end_day_in_month = "%d-%d-%d" % (to_day.year, to_day.month, month_end_day[to_day.strftime("%B")])
            # Get View In Range
            for item in this_shop.FK_Date.filter(Date__range = [first_start_day_in_month, first_end_day_in_month]):
                sum_view_in_this_month += int(item.Count)
            month_list.append(str(sum_view_in_this_month))
        except:
            month_list.append('0')
        # Get View When 0 <= Index < 7
        for i in range(1, 7):
            # Set Zero
            sum_view_in_this_month = 0
            start_day_in_month = None
            end_day_in_month = None
            try:
                # Set Start And End Month
                if to_day.month - i == 0:
                    this_month = 12
                    this_year = to_day.year - 1
                elif to_day.month - i < 0:
                    this_month = 12 - ((to_day.month - i) * -1)
                    this_year = to_day.year - 1
                else:
                    this_month = to_day.month - i
                    this_year = to_day.year
                
                start_day_in_month = "%d-%d-%d" % (this_year, this_month, 1)
                this_start = datetime.datetime.strptime(start_day_in_month, '%Y-%m-%d')
                end_day_in_month = "%d-%d-%d" % (this_year, this_month, month_end_day[this_start.strftime("%B")])
                # Get View In Range
                for item in this_shop.FK_Date.filter(Date__range = [start_day_in_month, end_day_in_month]):
                    sum_view_in_this_month += int(item.Count)
                month_list.append(str(sum_view_in_this_month))
            except:
                month_list.append('0')
        return month_list

@csrf_exempt
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_chart(request):
    try:
        # User First Shop
        user_shop = Shop.objects.filter(FK_ShopManager = request.user).order_by('DateCreate')[0]
        # Set Data
        day_view_list = user_shop.get_view_in_seven_day()
        week_view_list = user_shop.get_view_in_seven_week()
        month_view_list = user_shop.get_view_in_seven_month()
        return JsonResponse({'days': day_view_list,'weeks': week_view_list,'months': month_view_list}, status = HTTP_200_OK)
    except:
        return JsonResponse({'days': ['0', '0', '0', '0', '0', '0', '0'],'weeks': ['0', '0', '0', '0', '0', '0', '0'],'months': ['0', '0', '0', '0', '0', '0', '0']}, status = HTTP_200_OK)





# detail Message // res: (User Message Count When Seen = False) OR err

# Functions
class get_user_massege_count_when_status_is_false(threading.Thread):
    def run(self, request):
        count = 0
        # Get User Message Count When Seen = False
        if Message.objects.all().exists():
            for item in Message.objects.all():
                for user_msg in item.FK_Users.all():
                    if (user_msg.FK_User == request.user) and (user_msg.SeenStatus == False):
                        count += 1
        return count


@csrf_exempt
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_message_count(request):
    # Get User Message Count
    count = 0
    # Get User Message Count When Seen = False
    if Message.objects.all().exists():
        for item in Message.objects.all():
            for user_msg in item.FK_Users.all():
                if (user_msg.FK_User == request.user) and (user_msg.SeenStatus == False):
                    count += 1
    return JsonResponse({'count' : count}, status = HTTP_200_OK)





# detail Message // res: (Sale statistics) {send, wait, satisfaction}  OR err

# Functions
class get_wait_factors(threading.Thread):
    def run(self, request):
        try:
            items = []
            wath_factors = []
            for item in FactorPost.objects.filter(ProductStatus = '1'):
                print(item.Slug)
                if item.FK_Product.FK_Shop.FK_ShopManager == request.user:
                    items.append(item)
            for item in Factor.objects.filter(PaymentStatus = True, Publish = True):
                for factor_item in item.FK_FactorPost.all():
                    if factor_item in items:
                        wath_factors.append(item)
            wath_factors = list(dict.fromkeys(wath_factors))
            return wath_factors
        except Exception as e:
            return JsonResponse({'get-wait-factor-error' : str(e)}, status = HTTP_400_BAD_REQUEST)

class get_send_factors(threading.Thread):
    def run(self, request):
        try:
            items = []
            send_factors = []
            for item in FactorPost.objects.filter(ProductStatus = '3'):
                if item.FK_Product.FK_Shop.FK_ShopManager == request.user:
                    items.append(item)
            for item in Factor.objects.filter(PaymentStatus = True, Publish = True):
                for factor_item in item.FK_FactorPost.all():
                    if factor_item in items:
                        send_factors.append(item)
            send_factors = list(dict.fromkeys(send_factors))
            return send_factors
        except Exception as e:
            return JsonResponse({'get-send-factor-error' : str(e)}, status = HTTP_400_BAD_REQUEST)


@csrf_exempt
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_sale_statistics(request):
    try:
        if Shop.objects.filter(FK_ShopManager = request.user).exists():
            # Get All User Shops Orders
            wath_factors = get_wait_factors().run(request)
            send_factors = get_send_factors().run(request)

            return JsonResponse({'sned' : len(send_factors), 'wait' : len(wath_factors), 'satisfaction' : 0}, status = HTTP_200_OK)
        else:
            return JsonResponse({'err' : 'Not Exists Any Shop For You'}, status = HTTP_404_NOT_FOUND)
    except Exception as e:
        return JsonResponse({'err' : str(e)}, status = HTTP_400_BAD_REQUEST)



# get user home page statistics // res: (data) {send, wait, satisfaction, message count, chart} OR err
@csrf_exempt
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_home_page_statistics(request):
    if Shop.objects.filter(FK_ShopManager = request.user).exists():
        # Get All User Shops Orders
        wait_factors = 0
        send_factors = 0
        for item in Factor.objects.filter(PaymentStatus = True, Publish = True):
            if item.get_wait_user_factor(request):
                wait_factors += 1
            if item.get_send_user_factor(request):
                send_factors += 1
        # Get User Message
        count = 0
        # Get User Message Count When Seen = False
        for item in Message.objects.filter(Type = True):
            count += item.FK_Users.filter(FK_User = request.user, SeenStatus = False).count()

        return JsonResponse({'message_count' : count, 'sned' : send_factors, 'wait' : wait_factors, 'satisfaction' : 0}, status = HTTP_200_OK)
    else:
        return JsonResponse({'err' : 'Not Exists Any Shop For You'}, status = HTTP_404_NOT_FOUND)