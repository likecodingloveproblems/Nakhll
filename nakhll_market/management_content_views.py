from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db.models import Q
from kavenegar import *
import datetime
import threading
from django.utils.datastructures import MultiValueDictKeyError
from django.contrib.auth.models import User
from .models import Alert, Product, Profile, Shop, Category, Option_Meta, Market, SubMarket, Message, User_Message_Status, BankAccount, ShopBanner, ProductBanner, Attribute, AttrPrice, AttrProduct, Field, PostRange, AttrProduct, AttrPrice
from Payment.models import Coupon, Wallet, Factor, FactorPost


# --------------------------------------------------------------------------------------------------------------------------------------

# Get User Statistics
def GetUserStatistics():
    # Build Statistics Class
    class StatisticsClass:
        def __init__(self,  User_Count, Shop_Count, Shoper_Count, Block_User, Pub_Shop_Count):
            self.User_Count = User_Count
            self.Shop_Count = Shop_Count
            self.Shoper_Count = Shoper_Count
            self.Block_User = Block_User
            self.Pub_Shop_Count = Pub_Shop_Count

    # Get All User
    user_count = Profile.objects.all().count()
    # Shop Count
    shop_count = Shop.objects.all().count()
    # Publish Shop Count
    pub_shop_count = Shop.objects.filter(Publish = False).count()
    # Shoper Count
    # Shop_Profile = []

    # for shop_pro in Shop.objects.all():
    #     user_profile = Profile.objects.get(FK_User = shop_pro.FK_ShopManager)
    #     Shop_Profile.append(user_profile)

    # Shop_Profile = list(dict.fromkeys(Shop_Profile))

    # shoper_count = len(Shop_Profile)
    shoper_count = Shop.objects.values('FK_ShopManager').distinct().count()
    # Block Count
    block_count = User.objects.filter(is_active = False).count()

    return StatisticsClass(user_count, shop_count, shoper_count, block_count, pub_shop_count)

# Show All User Info
def Show_All_User_Info(request):

    if request.user.is_authenticated :

        if request.method == 'POST':

            try:
                first = request.POST["First_Name"]
            except:
                first = False

            try:
                last = request.POST["Last_Name"]
            except:
                last = False

            try:
                phone = request.POST["PhoneNumber"]
            except:
                phone = False

            if (first != '') or (last != '') or (phone != ''):
                profiles = None

                if (first != '') and (last == '') and (phone == ''):
                    profiles = Profile.objects.filter(FK_User__in = User.objects.filter(Q(first_name__icontains = first)))
                elif (last != '') and (first == '') and (phone == ''):
                    profiles = Profile.objects.filter(FK_User__in = User.objects.filter(Q(last_name__icontains = last)))
                elif (phone != '') and (first == '') and (last == ''):
                    profiles = Profile.objects.filter(Q(MobileNumber__icontains = phone))
                elif (first != '') and (last != '') and (phone == ''):
                    profiles = Profile.objects.filter(FK_User__in = User.objects.filter(Q(first_name__icontains = first, last_name__icontains = last)))
                elif (first != '') and (phone != '') and (last == ''):
                    profiles = Profile.objects.filter(FK_User__in = User.objects.filter(Q(first_name__icontains = first)))
                    profiles = profiles.filter(Q(MobileNumber__icontains = phone))
                elif (last != '') and (phone != '') and (first == ''):
                    profiles = Profile.objects.filter(FK_User__in = User.objects.filter(Q(last_name__icontains = last)))
                    profiles = profiles.filter(Q(MobileNumber__icontains = phone))
                else:
                    profiles = Profile.objects.filter(FK_User__in = User.objects.filter(Q(first_name__icontains = first, last_name__icontains = last)))
                    profiles = profiles.filter(Q(MobileNumber__icontains = phone))
                
                # make profiles unique
                profiles = profiles.distinct()
                # Get Menu Item
                options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
                # Get Nav Bar Menu Item
                navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
                # ----------------------------------------------------------------------
                # find user
                userProfile = Profile.objects.filter(FK_User=request.user)
                if userProfile.count() == 1:
                    userProfile = userProfile[0]
                else:
                    userProfile = False
                userWallet = Wallet.objects.filter(FK_User=request.user)
                if userWallet.count() == 1:
                    userWallet = userWallet[0]
                else:
                    userWallet = False

                # Get Statistics
                Statistic = GetUserStatistics()

                context = {
                    'Profiles':profiles,
                    'userProfile':userProfile,
                    'userWallet':userWallet,
                    'Options': options,
                    'MenuList':navbar,
                    'UserCount':Statistic.User_Count,
                    'ShopCount':Statistic.Shop_Count,
                    'PublishShopCount':Statistic.Pub_Shop_Count,
                    'ShoperCount':Statistic.Shoper_Count,
                    'BlockCount':Statistic.Block_User,
                    'ShowAlart':False,
                }

                return render(request, 'nakhll_market/parents/base_management.html', context)

            else:

                return redirect("nakhll_market:Show_All_User_Info")

        else:
            # Get User Profile
            profiles = Profile.objects.all()
            # find user
            userProfile = Profile.objects.filter(FK_User=request.user)
            if userProfile.count() == 1:
                userProfile = userProfile[0]
            else:
                userProfile = False
            userWallet = Wallet.objects.filter(FK_User=request.user)
            if userWallet.count() == 1:
                userWallet = userWallet[0]
            else:
                userWallet = False
            # Get Menu Item
            options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
            # Get Nav Bar Menu Item
            navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
            # Get All User
            profilesPaginator = Paginator (profiles, 20)
            page = request.GET.get('page')

            profiles = profilesPaginator.get_page(page)

            # Get Statistics
            Statistic = GetUserStatistics()


            context = {
                'Profiles':profiles,
                'Options': options,
                'MenuList':navbar,
                'UserCount':Statistic.User_Count,
                'ShopCount':Statistic.Shop_Count,
                'PublishShopCount':Statistic.Pub_Shop_Count,
                'ShoperCount':Statistic.Shoper_Count,
                'BlockCount':Statistic.Block_User,
                'ShowAlart':False,
                'userProfile':userProfile,
                'userWallet':userWallet,
            }
            return render(request, 'nakhll_market/parents/base_management.html', context)

    else:

        return redirect("nakhll_market:AccountLogin")



# Change User Status
def Change_User_Status(request, User_ID):

    if request.user.is_authenticated :

        # Get This User
        this_user = User.objects.get(id = User_ID)
        # Change User Status
        if this_user.is_active:
            this_user.is_active = False
            this_user.save()
        else:
            this_user.is_active = True
            this_user.save()

        return redirect("nakhll_market:Show_All_User_Info")

    else:

        return redirect("nakhll_market:AccountLogin")


# Add New User
def Add_New_User(request):

    if request.user.is_authenticated :

        if request.method == 'POST':

            try:
                First_Name = request.POST["User_FirstName"]
            except:
                First_Name = False

            try:
                Last_Name = request.POST["User_LastName"]
            except:
                Last_Name = False
            
            try:
                NationalCode = request.POST["User_NationalCode"]
            except:
                NationalCode = False
            
            try:
                MobileNumber = request.POST["User_MobileNumber"]
            except:
                MobileNumber = False

            try:
                Wallet_Amount = request.POST["User_Amount"]
            except:
                Wallet_Amount = False

            try:
                Status = request.POST["status"]
            except:
                Status = ''

            if (First_Name != '') and (Last_Name != '') and (NationalCode != '') and (MobileNumber != ''):

                if (len(NationalCode) == 10) and (len(MobileNumber) == 11):

                    if Profile.objects.filter(MobileNumber = MobileNumber, NationalCode = NationalCode).count() == 0:

                        # Build User
                        new_user = User(username = MobileNumber, first_name = First_Name, last_name = Last_Name)
                        new_user.save()
                        # Set Password
                        new_user.set_password(NationalCode)
                        new_user.save()
                        # Build Profile
                        new_profile = Profile(FK_User = new_user, MobileNumber = MobileNumber, NationalCode = NationalCode)
                        new_profile.save()
                        # Build User Wallet
                        if (Wallet_Amount != '') and (Wallet_Amount != 0):
                            new_user_wallet = Wallet(FK_User = new_user, Inverntory = Wallet_Amount)
                            new_user_wallet.save()

                            # Get Description
                            transaction_description = Option_Meta.objects.get(Title = 'add_new_user').Value_1
                            # Set Transaction
                            transaction = Transaction(FK_User = new_user, Price = Wallet_Amount, Type = '1', FK_Wallet = new_user_wallet, Description = transaction_description)
                            transaction.save()
                        else:
                            new_user_wallet = Wallet(FK_User = new_user)
                            new_user_wallet.save()

                        # Send SMS To User
                        url = 'https://api.kavenegar.com/v1/4E41676D4B514A4143744C354E6135314E4F47686B33594B747938794D30426A784A692F3579596F3767773D/verify/lookup.json' 
                        params = {'receptor': MobileNumber, 'token' : new_user.username, 'token2' : new_profile.NationalCode, 'template' : 'nakhll-addnewuser'}
                        result = requests.post(url, params = params)
                        Message = result.json()
                        MessageReturn = Message["return"]
                        print(MessageReturn["status"])

                        if Status == '1':
       
                            return redirect("nakhll_market:Add_New_Shop", id = new_user.id)


                        elif Status == '0':

                            return redirect("nakhll_market:Show_All_User_Info")

                    else:

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

                        context = {
                            'Users':user,
                            'Profile':profile,
                            'Wallet': wallets,
                            'Options': options,
                            'MenuList':navbar,
                            'ShowAlart':True,
                            'AlartMessage':'کاربری با این شماره موبایل یا کد ملی قبلا ثبت شده است!',
                        }

                        return render(request, 'nakhll_market/management/content/add_new_user.html', context)

                else:

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

                    context = {
                        'Users':user,
                        'Profile':profile,
                        'Wallet': wallets,
                        'Options': options,
                        'MenuList':navbar,
                        'ShowAlart':True,
                        'AlartMessage':'کد ملی 10 و شماره موبایل 11 رقم باید باشد!',
                    }

                    return render(request, 'nakhll_market/management/content/add_new_user.html', context)

            else:

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

                context = {
                    'Users':user,
                    'Profile':profile,
                    'Wallet': wallets,
                    'Options': options,
                    'MenuList':navbar,
                    'ShowAlart':True,
                    'AlartMessage':'نام، نام خانوادگی، کد ملی و شماره موبایل نمی تواند خالی باشد!',
                }

                return render(request, 'nakhll_market/management/content/add_new_user.html', context)

        else:

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

            context = {
                'Users':user,
                'Profile':profile,
                'Wallet': wallets,
                'Options': options,
                'MenuList':navbar,
                'ShowAlart':False,
            }

            return render(request, 'nakhll_market/management/content/add_new_user.html', context)

    else:

        return redirect("nakhll_market:AccountLogin")


# Add New User`s Shop
def Add_New_Shop(request, id):

    if request.user.is_authenticated :

        if request.method == 'POST':

            try:
                Title = request.POST["Shop_Title"]
            except:
                Title = ''
            
            try:
                Slug = request.POST["Shop_Slug"]
            except:
                Slug = ''
            
            Submarkets = request.POST.getlist("Shop_SubMarket")

            if (Title != '') and (Slug != '') and (len(Submarkets) != 0):

                if (Shop.objects.filter(Slug = Slug).count() == 0):

                    # Get This User
                    new_user = User.objects.get(id = id)
                    # Build Shop
                    new_shop = Shop.objects.create(FK_ShopManager = new_user, Title = Title, Slug = Slug, Publish = True, Available = False, FK_User = request.user)
                    # Set SubMarket
                    for item in Submarkets:
                        this_submarket = SubMarket.objects.get(Title = item)
                        new_shop.FK_SubMarket.add(this_submarket)

                    return redirect("nakhll_market:Add_New_Product", shop = new_shop.ID)

                else:

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
                    # ------------------------------------------------------------------------------------
                    # Get All SubMarkets
                    submarkets = SubMarket.objects.filter(Publish = True)
                    # Get This User
                    new_user = User.objects.get(id = id)
                
                    context = {
                        'Profile':profile,
                        'Wallet': wallets,
                        'Options': options,
                        'MenuList':navbar,
                        'ThisUser':new_user,
                        'SubMarkets':submarkets,
                        'ShowAlart':True,
                        'AlartMessage':'حجره ای با این شناسه موجود می باشد!',
                    }

                    return render(request, 'nakhll_market/management/content/add_new_shop.html', context)

            else:

                # Get User Profile
                profile = Profile.objects.all()
                # Get Wallet Inverntory
                wallets = Wallet.objects.all()
                # Get Menu Item
                options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
                # Get Nav Bar Menu Item
                navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
                # ------------------------------------------------------------------------------------
                # Get All SubMarkets
                submarkets = SubMarket.objects.filter(Publish = True)
                # Get This User
                new_user = User.objects.get(id = id)
            
                context = {
                    'Profile':profile,
                    'Wallet': wallets,
                    'Options': options,
                    'MenuList':navbar,
                    'ThisUser':new_user,
                    'SubMarkets':submarkets,
                    'ShowAlart':True,
                    'AlartMessage':'عنوان، شناسه، راسته حجره نمی تواند خالی باشد!',
                }

                return render(request, 'nakhll_market/management/content/add_new_shop.html', context)

        else:

            # Get User Profile
            profile = Profile.objects.all()
            # Get Wallet Inverntory
            wallets = Wallet.objects.all()
            # Get Menu Item
            options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
            # Get Nav Bar Menu Item
            navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
            # ------------------------------------------------------------------------------------
            # Get All SubMarkets
            submarkets = SubMarket.objects.filter(Publish = True)
            # Get This User
            new_user = User.objects.get(id = id)
        
            context = {
                'Profile':profile,
                'Wallet': wallets,
                'Options': options,
                'MenuList':navbar,
                'ThisUser':new_user,
                'SubMarkets':submarkets,
            }

            return render(request, 'nakhll_market/management/content/add_new_shop.html', context)

    else:

        return redirect("nakhll_market:AccountLogin")


# Add New Product In User`s Shop
def Add_New_Product(request, shop):

    if request.user.is_authenticated :

        if request.method == 'POST':

            try:
                Image = request.FILES["Product_Image"]
            except:
                Image = False

            try:
                Title = request.POST["prod_title"]
            except:
                Title = ''

            Categories = request.POST.getlist("ProdCat")
            
            try:
                Submarket = request.POST["ProdSub"]
            except:
                Submarket = ''
            
            try:
                Price = request.POST["prod_Price"]
            except:
                Price = ''

            try:
                Slug = request.POST["slugProd"]
            except:
                Slug = ''

            try:
                Wight = request.POST["prod_weght"]
            except:
                Wight = ''

            if (Title != '') and (Slug != '') and (len(Categories) != 0) and (Submarket != '') and (Price != '') and (Wight != '') and (Image != ''):

                if Product.objects.filter(Slug = Slug).count() == 0:

                    # Get This User
                    this_shop = Shop.objects.get(ID = shop)
                    # Get This Submarket
                    this_submarket = SubMarket.objects.get(Title = Submarket)
                    # Build Product
                    new_product = Product.objects.create(Title = Title, Slug = Slug, FK_SubMarket = this_submarket, Image = Image, FK_Shop = this_shop, Price = Price, PostRangeType = '1', Status = '4', Available = False, Publish = True, FK_User = request.user, Weight = Wight)
                    # Set Category
                    for item in Categories:
                        this_category = Category.objects.get(Title = item)
                        new_product.FK_Category.add(this_category)
                    # Set Post Range
                    # this_range = PostRange.objects.filter(State = 'کرمان', BigCity = 'کرمان', City = '')
                    # if this_range.count() == 0:
                    #     this_range = PostRange.objects.create(State = 'کرمان', BigCity = 'کرمان', City = '')
                    # else:
                    #     this_range = this_range[0]

                    # new_product.FK_PostRange.add(this_range)
                    # --------------------------------------------------------------------------------------------------------------
                    # Get User Profile
                    profile = Profile.objects.all()
                    # Get Wallet Inverntory
                    wallets = Wallet.objects.all()
                    # Get Menu Item
                    options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
                    # Get Nav Bar Menu Item
                    navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
                    # ----------------------------------------------------------------------
                    # Get All Categories
                    category = Category.objects.filter(Available = True, Publish = True)
                    # Get All Shop`s Submarkets
                    submartek = this_shop.FK_SubMarket.all()

                    context = {
                        'Profile':profile,
                        'Wallet': wallets,
                        'Options': options,
                        'MenuList':navbar,
                        'ThisShop':this_shop,
                        'Categort':category,
                        'SubMarket':submartek,
                        'ShowAlart':True,
                        'AlartMessage':'محصول شما با موفقیت ثبت شد!',
                    }
                    
                    return render(request, 'nakhll_market/management/content/add_new_product.html', context)

                else:

                    # Get User Profile
                    profile = Profile.objects.all()
                    # Get Wallet Inverntory
                    wallets = Wallet.objects.all()
                    # Get Menu Item
                    options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
                    # Get Nav Bar Menu Item
                    navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
                    # ----------------------------------------------------------------------
                    # Get This Shop
                    this_shop = Shop.objects.get(ID = shop)
                    # Get All Categories
                    category = Category.objects.filter(Available = True, Publish = True)
                    # Get All Shop`s Submarkets
                    submartek = this_shop.FK_SubMarket.all()

                    context = {
                        'Profile':profile,
                        'Wallet': wallets,
                        'Options': options,
                        'MenuList':navbar,
                        'ThisShop':this_shop,
                        'Categort':category,
                        'SubMarket':submartek,
                        'ShowAlart':True,
                        'AlartMessage':'محصولی با این شناسه موجود می باشد!',
                    }

                    return render(request, 'nakhll_market/management/content/add_new_product.html', context)

            else:

                # Get User Profile
                profile = Profile.objects.all()
                # Get Wallet Inverntory
                wallets = Wallet.objects.all()
                # Get Menu Item
                options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
                # Get Nav Bar Menu Item
                navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
                # ----------------------------------------------------------------------
                # Get This Shop
                this_shop = Shop.objects.get(ID = shop)
                # Get All Categories
                category = Category.objects.filter(Available = True, Publish = True)
                # Get All Shop`s Submarkets
                submartek = this_shop.FK_SubMarket.all()

                context = {
                    'Profile':profile,
                    'Wallet': wallets,
                    'Options': options,
                    'MenuList':navbar,
                    'ThisShop':this_shop,
                    'Categort':category,
                    'SubMarket':submartek,
                    'ShowAlart':True,
                    'AlartMessage':'عنوان، شناسه، راسته، دسته بندی، قیمت، وزن و عکس محصول نمی تواند خالی باشد!',
                }

                return render(request, 'nakhll_market/management/content/add_new_product.html', context)

        else:

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
            # ----------------------------------------------------------------------
            # Get This Shop
            this_shop = Shop.objects.get(ID = shop)
            # Get All Categories
            category = Category.objects.filter(Available = True, Publish = True)
            # Get All Shop`s Submarkets
            submartek = this_shop.FK_SubMarket.all()

            context = {
                'Profile':profile,
                'Wallet': wallets,
                'Options': options,
                'MenuList':navbar,
                'ThisShop':this_shop,
                'Categort':category,
                'SubMarket':submartek,
            }

            return render(request, 'nakhll_market/management/content/add_new_product.html', context)

    else:

        return redirect("nakhll_market:AccountLogin")


# Add User`s Bank Account Info
def Add_Bank_Account(request, id):
    # Check User Status
    if request.user.is_authenticated :

        if request.method == 'POST': 

            try:
                CreditCardNumber = request.POST["Shop_CreditCardNumber"]
            except:
                CreditCardNumber = ''

            try:
                ShabaBankNumber = request.POST["Shop_ShabaBankNumber"]
            except:
                ShabaBankNumber = ''

            try:
                AccountOwner = request.POST["Shop_AccountOwner"]
            except:
                AccountOwner = ''
            
            # Get This User
            this_user = User.objects.get(id = id)

            if BankAccount.objects.filter(FK_Profile = Profile.objects.get(FK_User = this_user)).exists():

                return redirect("nakhll_market:Show_All_User_Info")

            else:

                if (CreditCardNumber != '') and (ShabaBankNumber != '') and (AccountOwner != ''):

                    if (len(ShabaBankNumber) == 24) and (len(CreditCardNumber) == 16):

                        BankAccount.objects.create(FK_Profile = Profile.objects.get(FK_User = this_user), CreditCardNumber = CreditCardNumber, ShabaBankNumber = ShabaBankNumber, AccountOwner = AccountOwner)

                        return redirect("nakhll_market:Show_All_User_Info")

                    else:

                        # Get User Profile
                        profile = Profile.objects.all()
                        # Get Wallet Inverntory
                        wallets = Wallet.objects.all()
                        # Get Menu Item
                        options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
                        # Get Nav Bar Menu Item
                        navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
                        # ----------------------------------------------------------------------
                        # Get This User
                        this_user = User.objects.get(id = id)

                        context = {
                            'Profile':profile,
                            'Wallet': wallets,
                            'Options': options,
                            'MenuList':navbar,
                            'ThisUser':this_user,
                            'ShowAlart':True,
                            'AlartMessage':'شماره شباء 24 و شماره کارت 16 باید باشد!',
                        }

                        return render(request, 'nakhll_market/management/content/add_user_bank_account_info.html', context)

                else:

                    # Get User Profile
                    profile = Profile.objects.all()
                    # Get Wallet Inverntory
                    wallets = Wallet.objects.all()
                    # Get Menu Item
                    options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
                    # Get Nav Bar Menu Item
                    navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
                    # ----------------------------------------------------------------------
                    # Get This User
                    this_user = User.objects.get(id = id)

                    context = {
                        'Profile':profile,
                        'Wallet': wallets,
                        'Options': options,
                        'MenuList':navbar,
                        'ThisUser':this_user,
                        'ShowAlart':True,
                        'AlartMessage':'نام صاحب حساب، شماره کارت و شماره شباء نمی تواند خالی باشد!',
                    }

                    return render(request, 'nakhll_market/management/content/add_user_bank_account_info.html', context)

        else:

            # Get User Profile
            profile = Profile.objects.all()
            # Get Wallet Inverntory
            wallets = Wallet.objects.all()
            # Get Menu Item
            options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
            # Get Nav Bar Menu Item
            navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
            # ----------------------------------------------------------------------
            # Get This User
            this_user = User.objects.get(id = id)
            # Get Bank Account
            if BankAccount.objects.filter(FK_Profile = Profile.objects.get(FK_User = this_user)).exists():
                account = BankAccount.objects.get(FK_Profile = Profile.objects.get(FK_User = this_user))
            else:
                account = None

            context = {
                'Profile':profile,
                'Wallet': wallets,
                'Options': options,
                'MenuList':navbar,
                'ThisUser':this_user,
                'Account':account,
            }

            return render(request, 'nakhll_market/management/content/add_user_bank_account_info.html', context)

    else:

        return redirect("nakhll_market:AccountLogin")


# Show All Shoper User Info
def Show_All_Shoper_User_Info(request):

    if request.user.is_authenticated :
        # Get shop manager user Profile
        profiles_id =  Shop.objects.values_list('FK_ShopManager').distinct()
        profiles = Profile.objects.filter(FK_User__in=profiles_id)
        # Get user profile
        userProfile = Profile.objects.filter(FK_User=request.user)
        if userProfile.count() == 1:
            userProfile = userProfile[0]
        else:
            userProfile = False
        # Get user wallet
        userWallet = Wallet.objects.filter(FK_User=request.user)
        if userWallet.count() == 1:
            userWallet = userWallet[0]
        else:
            userWallet = False
        # Get Menu Item
        options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
        # Get Nav Bar Menu Item
        navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')

        # Get Statistics
        Statistic = GetUserStatistics()

        context = {
            'Profiles':profiles,
            'useProfile':userProfile,
            'userWallet':userWallet,
            'Options': options,
            'MenuList':navbar,
            'UserCount':Statistic.User_Count,
            'ShopCount':Statistic.Shop_Count,
            'ShoperCount':Statistic.Shoper_Count,
            'BlockCount':Statistic.Block_User,
            'ShowAlart':False,
        }

        return render(request, 'nakhll_market/parents/base_management.html', context)

    else:

        return redirect("nakhll_market:AccountLogin")


# Show User Info In Managment Section
def Management_Show_User_Info(request, id):

    # Check User Status
    if request.user.is_authenticated :

        # Get User Info
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
        # Get Select User
        user_select = User.objects.get(id = id)
        # Get Select Profile
        profile_select = Profile.objects.get(FK_User = user_select)

        context = {
            'Users':user,
            'Profile':profile,
            'Wallet': wallets,
            'Options': options,
            'MenuList':navbar,
            'User_Selected':user_select,
            'Profile_Selected':profile_select,
        }

        return render(request, 'nakhll_market/management/content/show_user_info.html', context)

    else:

        return redirect("nakhll_market:AccountLogin")


# Edit User Info In Managment Section
def Management_Edit_User_Info(request, id, msg = None):

    # Check User Status
    if request.user.is_authenticated :
        
        if request.method == 'POST':

            UserName = request.POST["username"]
            NationalCode = request.POST["nationalcode"]
            MobileNumber = request.POST["mobilenumber"]
            #-------------------------------------------
            # Get Select User
            user_select = User.objects.get(id = id)
            # Get Select Profile
            profile_select = Profile.objects.get(FK_User = user_select)
            # Check New Data
            if (UserName != user_select.username):
                try:
                    user_select.username = UserName
                    user_select.save()
                except:
                    if Profile.objects.filter(NationalCode = NationalCode).exists():
                        return redirect('nakhll_market:Edit_User_Info',
                        id = id,
                        msg =  'نام کاربری وارد شده تکراری می باشد!')
                    else:
                        return redirect('nakhll_market:Edit_User_Info',
                        id = id,
                        msg =  'نام کاربری وارد شده مطابق الگو ها نمی باشد!')
            elif (NationalCode != profile_select.NationalCode):
                try:
                    profile_select.NationalCode = NationalCode
                    profile_select.save()
                except:
                    if Profile.objects.filter(NationalCode = NationalCode).exists():
                        return redirect('nakhll_market:Edit_User_Info',
                        id = id,
                        msg =  'کد ملی وارد شده تکراری می باشد!')
                    else:
                        return redirect('nakhll_market:Edit_User_Info',
                        id = id,
                        msg =  'کد ملی وارد شده مطابق الگو ها نمی باشد!')
            elif (MobileNumber != profile_select.MobileNumber):
                try:
                    profile_select.MobileNumber = MobileNumber
                    profile_select.save()
                except:
                    if Profile.objects.filter(MobileNumber = MobileNumber).exists():
                        return redirect('nakhll_market:Edit_User_Info',
                        id = id,
                        msg =  'شماره موبایل وارد شده تکراری می باشد!')
                    else:
                        return redirect('nakhll_market:Edit_User_Info',
                        id = id,
                        msg =  'شماره موبایل وارد شده مطابق الگو ها نمی باشد!')
            else:
                return redirect('nakhll_market:Edit_User_Info',
                    id = id,
                    msg =  'شما تغییری ایجاد نکرده اید!')

            return redirect('nakhll_market:Show_All_User_Info')

        else:

            # Get User Info
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
            # Get Select User
            user_select = User.objects.get(id = id)
            # Get Select Profile
            profile_select = Profile.objects.get(FK_User = user_select)
            # Check Message
            if (msg != None) and (msg != 'none'):
                message = msg
                show = True
            else:
                message = msg
                show = False

            context = {
                'Users':user,
                'Profile':profile,
                'Wallet': wallets,
                'Options': options,
                'MenuList':navbar,
                'User_Selected':user_select,
                'Profile_Selected':profile_select,
                'ShowAlart':show,
                'AlartMessage':message,
            }

            return render(request, 'nakhll_market/management/content/edit_user_info.html', context)

    else:

        return redirect("nakhll_market:AccountLogin")


# Content Section ------------------------------------

# Get Shop Statistics
def GetShopStatistics():
    # Build Statistics Class
    class StatisticsClass:
        def __init__(self,  Product_Count, Not_Count, Off_Count, False_Count):
            self.Product_Count = Product_Count
            self.Not_Count = Not_Count
            self.Off_Count = Off_Count
            self.False_Count = False_Count

    # Get All Product
    product_count = Product.objects.all().count()
    # Not Product Count
    not_count = Product.objects.filter(Status = '4').count()
    # Off Product Count
    off_count = Product.objects.filter(Available = False).count()
    # False Product Count
    false_count = Product.objects.filter(Publish = False).count()

    return StatisticsClass(product_count, not_count, off_count, false_count)


# Show All Content
def Show_All_Content(request):

    search_list = None

    if request.user.is_authenticated :

        if request.method == 'POST':
            
            try:
                shop_title = request.POST["shop_title"]
            except MultiValueDictKeyError:
                shop_title = False

            if shop_title != '':

                search_list = Shop.objects.filter(Q(Title__icontains = shop_title))

                AllShop = []

                if search_list != None:
                    for item in search_list:
                        AllShop.append(item)

                AllShop = list(dict.fromkeys(AllShop))
                # ----------------------------------------------------------------------
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
                # ----------------------------------------------------------------------
                # Build Shop Info Class
                class ShopInfoClass:
                    def __init__(self,  item, shop_manage):
                        self.Shop = item
                        self.Shoper = shop_manage

                AllShopList = []

                # Get All Shop
                for item in AllShop:
                    user_shoper = User.objects.get(id = item.FK_ShopManager.id)
                    Shop_Manager = user_shoper.first_name + ' ' + user_shoper.last_name
                    New_Item = ShopInfoClass(item, Shop_Manager)
                    AllShopList.append(New_Item)

                # Get Statistics
                Statistic = GetShopStatistics()

                context = {
                    'Users':user,
                    'Profile':profile,
                    'Wallet': wallets,
                    'Options': options,
                    'MenuList':navbar,
                    'AllShops':AllShopList,
                    'ProductCount':Statistic.Product_Count,
                    'NotProductCount':Statistic.Not_Count,
                    'OffProductCount':Statistic.Off_Count,
                    'FalseProductCount':Statistic.False_Count,
                    'ShowAlart':False,
                }

                return render(request, 'nakhll_market/management/content/show_all_content.html', context)


            else:

                return redirect("nakhll_market:Show_All_Content")

        else:
            
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
            # ----------------------------------------------------------------------
            # Build Shop Info Class
            class ShopInfoClass:
                def __init__(self,  item, shop_manage):
                    self.Shop = item
                    self.Shoper = shop_manage

            AllShopList = []

            # Get All Shop
            for item in Shop.objects.all():
                user_shoper = User.objects.get(id = item.FK_ShopManager.id)
                Shop_Manager = user_shoper.first_name + ' ' + user_shoper.last_name
                New_Item = ShopInfoClass(item, Shop_Manager)
                AllShopList.append(New_Item)


            # pagination of all shops
            allShopListPaginator = Paginator (AllShopList, 10)
            page = request.GET.get('page')

            AllShopList = allShopListPaginator.get_page(page)

            # Get Statistics
            Statistic = GetShopStatistics()

            context = {
                'Users':user,
                'Profile':profile,
                'Wallet': wallets,
                'Options': options,
                'MenuList':navbar,
                'AllShops':AllShopList,
                'ProductCount':Statistic.Product_Count,
                'NotProductCount':Statistic.Not_Count,
                'OffProductCount':Statistic.Off_Count,
                'FalseProductCount':Statistic.False_Count,
                'ShowAlart':False,
            }

            return render(request, 'nakhll_market/management/content/show_all_content.html', context)

    else:

        return redirect("nakhll_market:AccountLogin")


# Change Shop Seen Status
def Change_Shop_Seen_Status(request, id):

    if request.user.is_authenticated :

        # Get This Shop
        this_shop = get_object_or_404(Shop, Slug = id)
        # Get All Shop`s Product
        all_product = Product.objects.filter(FK_Shop = this_shop)
        # Shop Change Status
        if this_shop.Available:
            # Change Product Status
            for item in all_product:
                item.Available = False
                item.save()

            this_shop.Available = False
            this_shop.save()
        else:
            # Change Product Status
            for item in all_product:
                item.Available = True
                item.save()

            this_shop.Available = True
            this_shop.save()

        return redirect("nakhll_market:Show_All_Content")

    else:

        return redirect("nakhll_market:AccountLogin")


# Change Shop Publish Status
def Change_Shop_Publish_Status(request, id):

    if request.user.is_authenticated :

        # Get This Shop
        this_shop = get_object_or_404(Shop, Slug = id)
        # Get All Shop`s Product
        all_product = Product.objects.filter(FK_Shop = this_shop)
        # Shop Change Status
        if this_shop.Publish:
            # Change Product Status
            for item in all_product:
                item.Publish = False
                item.save()

            this_shop.Publish = False
            this_shop.save()
        else:
            # Change Product Status
            for item in all_product:
                item.Publish = True
                item.save()

            this_shop.Publish = True
            this_shop.save()

        return redirect("nakhll_market:Show_All_Content")

    else:

        return redirect("nakhll_market:AccountLogin")



# Show Shop Info
def Show_Shop_Info(request, Shop_Slug):

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
        # ----------------------------------------------------------------------
        # Get This Shop
        this_shop = get_object_or_404(Shop, Slug = Shop_Slug)
        # Get All Shop`s Products
        AllProducts = Product.objects.filter(FK_Shop = this_shop)
        # Get All Shop`s Banners
        AllBanners = ShopBanner.objects.filter(FK_Shop = this_shop)
        # Get All Shop`s Sale
        AllSales = []
        AllSales_Send = []

        for item in Factor.objects.filter(PaymentStatus = True, Publish = True):
            for factor_item in item.FK_FactorPost.all():
                if factor_item.FK_Product.FK_Shop == this_shop:
                    if item.OrderStatus == '5':
                        AllSales_Send.append(item)
                        AllSales.append(item)
                    else:
                        AllSales.append(item)

        AllSales = list(dict.fromkeys(AllSales))
        AllSales_Send = list(dict.fromkeys(AllSales_Send))
        # Get Shop Holiday
        week = this_shop.Holidays.split('-')
        # Build Shop_Submarket Class
        class SubmarketClass:
            def __init__(self,  item, status):
                self.Submarket = item
                self.Status = status

        AllSubmarketList = []

        for item in SubMarket.objects.all():
            New_Item = SubmarketClass(item, False)
            AllSubmarketList.append(New_Item)

        for item in this_shop.FK_SubMarket.all():
            for submarket_item in AllSubmarketList:
                if item == submarket_item.Submarket:
                    submarket_item.Status = True

        context = {
            'Users':user,
            'Profile':profile,
            'Wallet': wallets,
            'Options': options,
            'MenuList':navbar,
            'Shop':this_shop,
            'ThisShop_Products_Count':AllProducts.count(),
            'ThisShop_Bannners_Count':AllBanners.count(),
            'ThisShop_Sales_Count':len(AllSales),
            'ThisShop_Sales_ISSend_Count':len(AllSales_Send),
            'Week':week,
            'SubMarkets':AllSubmarketList,
            'ThisShop_Product':AllProducts,
            'ShopBanners':AllBanners,
        }

        return render(request, 'nakhll_market/management/content/show_shop_info.html', context)

    else:

        return redirect("nakhll_market:AccountLogin")


# Change Product Seen Status
def Change_Product_Seen_Status(request, id):

    if request.user.is_authenticated :

        # Get This Product
        this_product = get_object_or_404(Product, ID = id)
        # Product Change Status
        if this_product.Available:
            this_product.Available = False
            this_product.save()
        else:
            this_product.Available = True
            this_product.save()

        return redirect("nakhll_market:Show_Shop_Info", Shop_Slug = this_product.FK_Shop.Slug)

    else:

        return redirect("nakhll_market:AccountLogin")


# Change Product Publish Status
def Change_Product_Publish_Status(request, id):

    if request.user.is_authenticated :

        # Get This Product
        this_product = get_object_or_404(Product, ID = id)
        # Product Change Status
        if this_product.Publish:
            this_product.Publish = False
            this_product.save()
        else:
            this_product.Publish = True
            this_product.save()

        return redirect("nakhll_market:Show_Shop_Info", Shop_Slug = this_product.FK_Shop.Slug)

    else:

        return redirect("nakhll_market:AccountLogin")


# Change Shop Banner Seen Status
def Change_Shop_Banner_Seen_Status(request, id):

    if request.user.is_authenticated :

        # Get This Shop Banner
        this_banner = get_object_or_404(ShopBanner, id = id)
        # Shop Banner Change Status
        if this_banner.Available:
            this_banner.Available = False
            this_banner.save()
        else:
            this_banner.Available = True
            this_banner.save()

        return redirect("nakhll_market:Show_Shop_Info", Shop_Slug = this_banner.FK_Shop.Slug)

    else:

        return redirect("nakhll_market:AccountLogin")


# Change Shop Banner Publish Status
def Change_Shop_Banner_Publish_Status(request, id):

    if request.user.is_authenticated :

        # Get This Shop Banner
        this_banner = get_object_or_404(ShopBanner, id = id)
        # Shop Banner Change Status
        if this_banner.Publish:
            this_banner.Publish = False
            this_banner.save()
        else:
            this_banner.Publish = True
            this_banner.save()

        return redirect("nakhll_market:Show_Shop_Info", Shop_Slug = this_banner.FK_Shop.Slug)

    else:

        return redirect("nakhll_market:AccountLogin")


# Show Product Info
def Show_Product_Info(request, Product_Slug):

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
        # ----------------------------------------------------------------------
        # Get This Product
        this_product = get_object_or_404(Product, Slug = Product_Slug)
        # Get All Product Banner
        this_banners = ProductBanner.objects.filter(FK_Product = this_product)
        # Get Sales Product Count
        AllSales = []
        AllSales_Send = []

        for item in FactorPost.objects.filter(FK_Product = this_product):
            if item.ProductStatus != '0':
                if item.ProductStatus == '3':
                    AllSales_Send.append(item)
                    AllSales.append(item)
                else:
                    AllSales.append(item)

        AllSales = list(dict.fromkeys(AllSales))
        AllSales_Send = list(dict.fromkeys(AllSales_Send))
        # Get All Product Attribute
        this_attribute = AttrProduct.objects.filter(FK_Product = this_product)
        # Get All Product Attribute Price
        this_attribute_price = AttrPrice.objects.filter(FK_Product = this_product)

        context = {
            'Users':user,
            'Profile':profile,
            'Wallet': wallets,
            'Options': options,
            'MenuList':navbar,
            'Shop':this_product.FK_Shop.Slug,
            'Product':this_product,
            'ThisProduct_Banners_Count':this_banners.count(),
            'ThisProduct_Sales_Count':len(AllSales),
            'ThisProduct_Sales_ISSend_Count':len(AllSales_Send),
            'ProductAttribute':this_attribute,
            'ProductAttributePrice':this_attribute_price,
            'ProductBanner':this_banners,
        }

        return render(request, 'nakhll_market/management/content/show_product_info.html', context)

    else:

        return redirect("nakhll_market:AccountLogin")


# Change Product Banner Seen Status
def Change_Product_Banner_Seen_Status(request, id):

    if request.user.is_authenticated :

        # Get This Product Banner
        this_banner = get_object_or_404(ProductBanner, id = id)
        # Banner Change Status
        if this_banner.Publish:
            this_banner.Publish = False
            this_banner.save()
        else:
            this_banner.Publish = True
            this_banner.save()

        return redirect("nakhll_market:Show_Product_Info", Product_Slug = this_banner.FK_Product.Slug)

    else:

        return redirect("nakhll_market:AccountLogin")


# Change Product Banner Publish Status
def Change_Product_Banner_Publish_Status(request, id):

    if request.user.is_authenticated :

        # Get This Product Banner
        this_banner = get_object_or_404(ProductBanner, id = id)
        # Banner Change Status
        if this_banner.Publish:
            this_banner.Publish = False
            this_banner.save()
        else:
            this_banner.Publish = True
            this_banner.save()

        return redirect("nakhll_market:Show_Product_Info", Product_Slug = this_banner.FK_Product.Slug)

    else:

        return redirect("nakhll_market:AccountLogin")


# Change Product Attribute Status
def Change_Product_Attribute_Status(request, id):

    if request.user.is_authenticated :

        # Get This Product Attribute
        this_attribute = get_object_or_404(AttrProduct, id = id)
        # Attribute Change Status
        if this_attribute.Available:
            this_attribute.Available = False
            this_attribute.save()
        else:
            this_attribute.Available = True
            this_attribute.save()

        return redirect("nakhll_market:Show_Product_Info", Product_Slug = this_attribute.FK_Product.Slug)

    else:

        return redirect("nakhll_market:AccountLogin")


# Change Product Attribute Price Status
def Change_Product_AttrPrice_Status(request, id):

    if request.user.is_authenticated :

        # Get This Product AttrPrice
        this_attrprice = get_object_or_404(AttrPrice, id = id)
        # AttrPrice Change Status
        if this_attrprice.Publish:
            this_attrprice.Publish = False
            this_attrprice.save()
        else:
            this_attrprice.Publish = True
            this_attrprice.save()

        return redirect("nakhll_market:Show_Product_Info", Product_Slug = this_attrprice.FK_Product.Slug)

    else:

        return redirect("nakhll_market:AccountLogin")


# Add New Full Shop
def Add_New_Full_Shop(request, msg = None):

    if request.user.is_authenticated :

        if request.method == 'POST':

            try:
                image = request.FILES["Shop_Image"]
            except MultiValueDictKeyError:
                image = ''
            try:
                title = request.POST["Shop_Title"]
            except MultiValueDictKeyError:
                title = ''
            try:
                slug = request.POST["Shop_Slug"]
            except MultiValueDictKeyError:
                slug = ''
            try:
                des = request.POST["Shop_Des"]
            except MultiValueDictKeyError:
                des = ''
            try:
                state = request.POST["Shop_State"]
            except MultiValueDictKeyError:
                state = ''
            try:
                bigcity = request.POST["Shop_BigCity"]
            except MultiValueDictKeyError:
                bigcity = ''
            try:
                city = request.POST["Shop_City"]
            except MultiValueDictKeyError:
                city = ''
            submarkets = request.POST.getlist("Shop_SubMarket")
            user = request.POST.getlist("Shop_User")
            try:
                bio = request.POST["Shop_Bio"]
            except MultiValueDictKeyError:
                bio = ''
            try:
                sat = request.POST["SATCheck"]
            except MultiValueDictKeyError:
                sat = ''
            try:
                sun = request.POST["SUNCheck"]
            except MultiValueDictKeyError:
                sun = ''
            try:
                mon = request.POST["MONCheck"]
            except MultiValueDictKeyError:
                mon = ''
            try:
                tue = request.POST["TUECheck"]
            except MultiValueDictKeyError:
                tue = ''
            try:
                wed = request.POST["WEDCheck"]
            except MultiValueDictKeyError:
                wed = ''
            try:
                thu = request.POST["THUCheck"]
            except MultiValueDictKeyError:
                thu = ''
            try:
                fri = request.POST["FRICheck"]
            except MultiValueDictKeyError:
                fri = ''
            try:
                seen = request.POST["Shop_Seen"]
            except MultiValueDictKeyError:
                seen = ''
            try:
                status = request.POST["Shop_Status"]
            except MultiValueDictKeyError:
                status = ''
         

            if len(user) == 1:
                if (title != '') and (slug != '') and (Shop.objects.filter(Slug = slug).count() == 0):
                    if (len(submarkets) != 0) and (state != '') and (city != '') and (bigcity != ''):

                        week = ''

                        if sat != '':
                            week += "0-"
                        if sun != '':
                            week += "1-"
                        if mon != '':
                            week += "2-"
                        if tue != '':
                            week += "3-"
                        if wed != '':
                            week += "4-"
                        if thu != '':
                            week += "5-"
                        if fri != '':
                            week += "6-"
                    
                        if image != '':

                            shop = Shop.objects.create(FK_ShopManager = User.objects.get(id = user[0]), Title = title, Slug = slug, Description = des, Image = image, Bio = bio, State = state, BigCity = bigcity, City = city, Holidays = week, Available = bool(seen), Publish = bool(state))
                            for item in submarkets:
                                sub = SubMarket.objects.get(Title = item)
                                shop.FK_SubMarket.add(sub)
                            Alert.objects.create(Part = '2', FK_User = request.user, Slug = shop.ID, Seen = True, Status = True, FK_Staff = request.user)

                            return redirect('nakhll_market:Show_Shop_Info',
                            Shop_Slug = shop.Slug)

                        else:

                            shop = Shop.objects.create(FK_ShopManager = User.objects.get(id = user[0]), Title = title, Slug = slug, Description = des, Bio = bio, State = state, BigCity = bigcity, City = city, Holidays = week, Available = bool(seen), Publish = bool(state))
                            for item in submarkets:
                                sub = SubMarket.objects.get(Title = item)
                                shop.FK_SubMarket.add(sub)
                            Alert.objects.create(Part = '2', FK_User = request.user, Slug = shop.ID, Seen = True, Status = True, FK_Staff = request.user)
             
                            return redirect('nakhll_market:Show_Shop_Info',
                            Shop_Slug = shop.Slug)
                    else:

                        return redirect('nakhll_market:Add_New_Full_Shop',
                        msg =  'راسته، استان، شهرستان و شهر نمی تواند خالی باشد.')

                else:
                    return redirect('nakhll_market:Add_New_Full_Shop',
                    msg =  'عنوان و شناسه نمی تواند خالی باشد - شناسه تکراری می باشد.')

            else:

                return redirect('nakhll_market:Add_New_Full_Shop',
                msg =  'شما باید یک کاربر را به عنوان حجره دار انتخاب نمایید.')


        else:
            
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
            # -------------------------------------------------------------------
            # Get All Submarket
            allsubmarket = SubMarket.objects.filter(Available = True, Publish = True)

            if msg != 'None':
                message = msg
                show = True
            else:
                message = ''
                show = False

            context = {
                'Users':user,
                'Profile':profile,
                'Wallet': wallets,
                'Options': options,
                'MenuList':navbar,
                'SubMarkets':allsubmarket,
                'ShowAlart':show,
                'AlartMessage':message,
            }

            return render(request, 'nakhll_market/management/content/add_new_full_shop.html', context)

    else:

        return redirect("nakhll_market:AccountLogin")



# Edit Full Shop
def Edit_Full_Shop(request, id, msg = None):

    if request.user.is_authenticated :

        if request.method == 'POST':

            try:
                image = request.FILES["Shop_Image"]
            except MultiValueDictKeyError:
                image = ''
            try:
                title = request.POST["Shop_Title"]
            except MultiValueDictKeyError:
                title = ''
            # try:
            #     slug = request.POST["Shop_Slug"]
            # except MultiValueDictKeyError:
            #     slug = ''
            try:
                des = request.POST["Shop_Des"]
            except MultiValueDictKeyError:
                des = ''
            try:
                state = request.POST["Shop_State"]
            except MultiValueDictKeyError:
                state = ''
            try:
                bigcity = request.POST["Shop_BigCity"]
            except MultiValueDictKeyError:
                bigcity = ''
            try:
                city = request.POST["Shop_City"]
            except MultiValueDictKeyError:
                city = ''
            submarkets = request.POST.getlist("Shop_SubMarket")
            user = request.POST.getlist("Shop_User")
            try:
                bio = request.POST["Shop_Bio"]
            except MultiValueDictKeyError:
                bio = ''
            try:
                sat = request.POST["SATCheck"]
            except MultiValueDictKeyError:
                sat = ''
            try:
                sun = request.POST["SUNCheck"]
            except MultiValueDictKeyError:
                sun = ''
            try:
                mon = request.POST["MONCheck"]
            except MultiValueDictKeyError:
                mon = ''
            try:
                tue = request.POST["TUECheck"]
            except MultiValueDictKeyError:
                tue = ''
            try:
                wed = request.POST["WEDCheck"]
            except MultiValueDictKeyError:
                wed = ''
            try:
                thu = request.POST["THUCheck"]
            except MultiValueDictKeyError:
                thu = ''
            try:
                fri = request.POST["FRICheck"]
            except MultiValueDictKeyError:
                fri = ''
         
            # Get This Shop
            this_shop = get_object_or_404(Shop, ID = id)

            if (title != ''):
                if (len(submarkets) != 0) and (state != '') and (city != '') and (bigcity != ''):

                    week = ''

                    if sat != '':
                        week += "0-"
                    if sun != '':
                        week += "1-"
                    if mon != '':
                        week += "2-"
                    if tue != '':
                        week += "3-"
                    if wed != '':
                        week += "4-"
                    if thu != '':
                        week += "5-"
                    if fri != '':
                        week += "6-"
                
                    alert = Alert.objects.create(Part = '3', FK_User = request.user, Slug = this_shop.ID, Seen = True, Status = True, FK_Staff = request.user)

                    if (len(submarkets) != 0):
                        Sub = '-'
                        for sub in submarkets:
                            Sub += sub + '-'

                        SubMarketField = Field.objects.create(Title = 'SubMarket', Value = Sub)
                        alert.FK_Field.add(SubMarketField)
                        # Set New Data
                        for item in this_shop.FK_SubMarket.all():
                            this_shop.FK_SubMarket.remove(item)
                        for item in submarkets:
                            this_shop.FK_SubMarket.add(SubMarket.objects.get(Title = item))

                
                    if image != '':
                        this_shop.Image = image
                        this_shop.save()
                        img_str = 'NewImage' + '#' + str(this_shop.Image)
                        ImageField = Field.objects.create(Title = 'Image', Value = img_str)
                        alert.FK_Field.add(ImageField)

                    if title != this_shop.Title:
                        this_shop.Title = title
                        this_shop.save()
                        TitleField = Field.objects.create(Title = 'Title', Value = title)
                        alert.FK_Field.add(TitleField)

                    if des != this_shop.Description:
                        this_shop.Description = des
                        this_shop.save()
                        DescriptionField = Field.objects.create(Title = 'Description', Value = des)
                        alert.FK_Field.add(DescriptionField)

                    if bio != this_shop.Bio:
                        this_shop.Bio = bio
                        this_shop.save()
                        BioField = Field.objects.create(Title = 'Bio', Value = bio)
                        alert.FK_Field.add(BioField)

                    if state != this_shop.State:
                        this_shop.State = state
                        this_shop.save()
                        StateField = Field.objects.create(Title = 'State', Value = state)
                        alert.FK_Field.add(StateField)

                    if bigcity != this_shop.BigCity:
                        this_shop.BigCity = bigcity
                        this_shop.save()
                        BigCityField = Field.objects.create(Title = 'BigCity', Value = bigcity)
                        alert.FK_Field.add(BigCityField)

                    if city != this_shop.City:
                        this_shop.City = city
                        this_shop.save()
                        CityField = Field.objects.create(Title = 'City', Value = city)
                        alert.FK_Field.add(CityField)

                    if week != this_shop.Holidays:
                        this_shop.Holidays = week
                        this_shop.save()
                        HolidaysField = Field.objects.create(Title = 'Holidays', Value = week)
                        alert.FK_Field.add(HolidaysField)
                    
                    if alert.FK_Field.all().count() == 0:
                        alert.delete()

                    return redirect('nakhll_market:Show_Shop_Info',
                    Shop_Slug = this_shop.Slug)

                else:

                    return redirect('nakhll_market:Edit_Full_Shop',
                    id = this_shop.ID,
                    msg =  'راسته، استان، شهرستان و شهر نمی تواند خالی باشد.')

            else:
                return redirect('nakhll_market:Edit_Full_Shop',
                id = this_shop.ID,
                msg =  'عنوان حجره نمی تواند خالی باشد.')



        else:
            
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
            # -------------------------------------------------------------------
            # Get This Shop
            this_shop = get_object_or_404(Shop, ID = id)
            # Get Holiday
            week = this_shop.Holidays.split('-')
            # Build Class
            class Items:
                def __init__(self, submarket, status):
                    self.SubMarket = submarket
                    self.Status = status

            ItemsList = []

            for item in SubMarket.objects.filter(Available = True, Publish = True):
                new_item = Items(item, False)
                ItemsList.append(new_item)
            
            for item in this_shop.FK_SubMarket.all():
                for list_item in ItemsList:
                    if list_item.SubMarket == item:
                        list_item.Status = True

            if msg != 'None':
                message = msg
                show = True
            else:
                message = ''
                show = False

            context = {
                'Users':user,
                'Profile':profile,
                'Wallet': wallets,
                'Options': options,
                'MenuList':navbar,
                'SubMarkets':ItemsList,
                'Shop':this_shop,
                'Week':week,
                'ShowAlart':show,
                'AlartMessage':message,
            }

            return render(request, 'nakhll_market/management/content/edit_full_shop.html', context)

    else:

        return redirect("nakhll_market:AccountLogin")


# Add New Shop Banner
def Add_New_Shop_Banner(request, id, msg = None):

    if request.user.is_authenticated :

        if request.method == 'POST':

            try:
                Banner_Image = request.FILES["Banner_Image"]
            except:
                Banner_Image = ''

            try:
                Banner_Title = request.POST["Banner_Title"]
            except:
                Banner_Title = ''

            try:
                Banner_URL = request.POST["Banner_URL"]
            except:
                Banner_URL = ''
            
            try:
                Banner_Description = request.POST["Banner_Description"]
            except:
                Banner_Description = ''
            
            try:
                Banner_Builder = request.POST["Banner_Builder"]
            except:
                Banner_Builder = ''

            try:
                Banner_URL_Builder = request.POST["Banner_URL_Builder"]
            except:
                Banner_URL_Builder = ''

            try:
                Banner_Seen = request.POST["Banner_Seen"]
            except:
                Banner_Seen = ''

            try:
                Banner_Status = request.POST["Banner_Status"]
            except:
                Banner_Status = ''

            if (Banner_Title != '') and (Banner_Image != ''):

                # This Shop
                this_shop = Shop.objects.get(ID = id)
                # Create New Object
                thisbanner = ShopBanner.objects.create(FK_Shop = this_shop, Title = Banner_Title, Description = Banner_Description, Image = Banner_Image, Available = bool(Banner_Seen), Publish = bool(Banner_Status))
                # Set New Alert
                Alert.objects.create(Part = '4', FK_User = request.user, Slug = thisbanner.id, Seen = True, Status = True, FK_Staff = request.user)
                # Save Data
                if (Banner_URL != ''):
                    thisbanner.URL = Banner_URL
                    thisbanner.save()

                if (Banner_Builder != ''):
                    thisbanner.BannerBuilder = Banner_Builder
                    thisbanner.save()
                
                if (Banner_URL_Builder != ''):
                    thisbanner.BannerURL = Banner_URL_Builder
                    thisbanner.save()
                # -----------------------------------------------------------------
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

                return redirect('nakhll_market:Show_Shop_Info',
                Shop_Slug = this_shop.Slug)

            else:

                return redirect('nakhll_market:Add_New_Shop_Banner',
                msg =  'عنوان و عکس بنر حجره نمی تواند خالی باشد.')

        else:
            
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
            # -------------------------------------------------------------------
            # This Shop
            this_shop = Shop.objects.get(ID = id)

            if msg != 'None':
                message = msg
                show = True
            else:
                message = ''
                show = False

            context = {
                'Users':user,
                'Profile':profile,
                'Wallet': wallets,
                'Options': options,
                'MenuList':navbar,
                'Shop':this_shop,
                'ShowAlart':show,
                'AlartMessage':message,
            }

            return render(request, 'nakhll_market/management/content/add_new_shop_banner.html', context)

    else:

        return redirect("nakhll_market:AccountLogin")


# Add New Shop`s Product
def Add_New_Shop_Product(request, id, msg = None):

    if request.user.is_authenticated :

        if request.method == 'POST':

            try:
                Image = request.FILES["Product_Image"]
            except:
                Image = ''

            try:
                Title = request.POST["prod_title"]
            except:
                Title = ''

            try:
                Slug = request.POST["slugProd"]
            except:
                Slug = ''

            try:
                Des = request.POST["ProdDes"]
            except:
                Des = ''
    
            category_list = request.POST.getlist("ProdCat")

            try:
                Submarket = request.POST["ProdSub"]
            except:
                Submarket = ''
            
            try:
                Bio = request.POST["ProdBio"]
            except:
                Bio = ''

            try:
                Story = request.POST["ProdStory"]
            except:
                Story = ''

            try:
                Price = request.POST["prod_Price"]
            except:
                Price = ''

            try:
                OldPrice = request.POST["Prodoldprice"]
            except:
                OldPrice = ''
    
            try:
                Range = request.POST["ProdRange"]
            except:
                Range = ''

            try:
                PostType = request.POST["ProdPostType"]
            except:
                PostType = ''
            
            Product_PostRange = request.POST.getlist("PostRange")

            Product_ExePostRange = request.POST.getlist("ExePostRange")

            try:
                Prod_Net_Weight = request.POST["product_netweight"]
            except:
                Prod_Net_Weight = ''

            try:
                Prod_Packing_Weight = request.POST["product_packingweight"]
            except:
                Prod_Packing_Weight = ''

            try:
                Prod_Length_With_Packaging = request.POST["product_lengthwithpackaging"]
            except:
                Prod_Length_With_Packaging = ''

            try:
                Prod_Width_With_Packaging = request.POST["product_widthwithpackaging"]
            except:
                Prod_Width_With_Packaging = ''

            try:
                Prod_Height_With_Packaging = request.POST["product_heightwithpackaging"]
            except:
                Prod_Height_With_Packaging = ''

            try:
                Banner_Seen = request.POST["Banner_Seen"]
            except:
                Banner_Seen = ''

            try:
                Banner_Status = request.POST["Banner_Status"]
            except:
                Banner_Status = ''

            if (Title != '') and (len(category_list) != 0) and (Slug != '') and (Submarket != '') and (Image != '') and (Price != '') and (PostType != ''):

                if (OldPrice == '') or ((OldPrice != Price) and (int(OldPrice) > int(Price))):

                    this_shop = Shop.objects.get(ID = id)
                    
                    if Product.objects.filter(Slug = Slug).exists():

                        return redirect('nakhll_market:Add_New_Shop_Product',
                        msg =  'محصولی بااین شناسه ثبت شده است.')

                    else:

                        PT = None
                        R = None

                        if PostType != '':
                            if PostType == 'آماده در انبار':
                                PT = '1'
                            elif PostType == 'تولید بعد از سفارش':
                                PT = '2'
                            elif PostType == 'سفارشی سازی فروش':
                                PT = '3'
                            elif PostType == 'موجود نیست':
                                PT = '4'

                        product = Product.objects.create(Title = Title, Slug = Slug, FK_SubMarket = SubMarket.objects.get(ID = Submarket), Image = Image, FK_Shop = this_shop, Price = Price, Status = PT, Available = bool(Banner_Seen), Publish = bool(Banner_Status))

                        for item in category_list:
                            product.FK_Category.add(Category.objects.get(id = item))

                        if len(Product_PostRange) != 0:
                            for item in Product_PostRange:
                                product.FK_PostRange.add(PostRange.objects.get(id = item))
                        
                        if len(Product_ExePostRange) != 0:
                            for item in Product_ExePostRange:
                                product.FK_ExceptionPostRange.add(PostRange.objects.get(id = item))

                        if Des != '':
                            product.Description = Des

                        if Bio != '':
                            product.Bio = Bio

                        if Story != '':
                            product.Story = Story

                        if OldPrice != '':
                            product.OldPrice = OldPrice
                        else:
                            product.OldPrice = '0'

                        if Range != '':
                            if Range == 'سراسر کشور':
                                R = '1'
                            elif Range == 'استانی':
                                R = '2'
                            elif Range == 'شهرستانی':
                                R = '3'
                            elif Range == 'شهری':
                                R = '4'
                            
                            product.PostRangeType = R

                        # Product Weight Info
                        product.Net_Weight = Prod_Net_Weight
                        product.Weight_With_Packing = Prod_Packing_Weight
                        # Product Dimensions Info
                        product.Length_With_Packaging = Prod_Length_With_Packaging
                        product.Width_With_Packaging = Prod_Width_With_Packaging
                        product.Height_With_Packaging = Prod_Height_With_Packaging

                        product.save()
                                                    
                        Alert.objects.create(Part = '6', FK_User = request.user, Slug = product.ID, Seen = True, Status = True, FK_Staff = request.user)

                        return redirect('nakhll_market:Show_Product_Info',
                        Product_Slug = product.Slug)

                else:
                    
                    if Price == OldPrice:

                        return redirect('nakhll_market:Add_New_Shop_Product',
                        msg =  'قیمت فروش محصول و قیمت واقعی نمی تواند با هم برابر باشد.')

                    elif int(Price) > int(OldPrice):

                        return redirect('nakhll_market:Add_New_Shop_Product',
                        msg =  'قیمت واقعی نمیتواند از قیمت فروش محصول کمتر باشد.')

            else:

                return redirect('nakhll_market:Add_New_Shop_Product',
                msg =  'عنوان - دسته بندی - حجره - شناسه - عکس - قیمت و نوع ارسال محصول اجباریست.')

        else:
            
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
            # -------------------------------------------------------------------
            # This Shop
            this_shop = Shop.objects.get(ID = id)
            # Get All Submarket
            submarkets = SubMarket.objects.filter(Publish = True)
            # Get All Category
            categories = Category.objects.filter(Publish = True)
            # Get All PostRange
            postrange = PostRange.objects.all()

            if msg != 'None':
                message = msg
                show = True
            else:
                message = ''
                show = False

            context = {
                'Users':user,
                'Profile':profile,
                'Wallet': wallets,
                'Options': options,
                'MenuList':navbar,
                'Shop':this_shop,
                'Categort':categories,
                'SubMarket':submarkets,
                'PostRange':postrange,
                'ShowAlart':show,
                'AlartMessage':message,
            }

            return render(request, 'nakhll_market/management/content/add_new_shop_full_product.html', context)

    else:

        return redirect("nakhll_market:AccountLogin")



# Edit Full Product
def Edit_Full_Product(request, id, msg = None):

    if request.user.is_authenticated :

        if request.method == 'POST':

            try:
                Image = request.FILES["Product_Image"]
            except:
                Image = ''

            try:
                Title = request.POST["prod_title"]
            except:
                Title = ''

            try:
                Des = request.POST["ProdDes"]
            except:
                Des = ''
    
            category_list = request.POST.getlist("ProdCat")

            try:
                Submarket = request.POST["ProdSub"]
            except:
                Submarket = ''
            
            try:
                Bio = request.POST["ProdBio"]
            except:
                Bio = ''

            try:
                Story = request.POST["ProdStory"]
            except:
                Story = ''

            try:
                Price = request.POST["prod_Price"]
            except:
                Price = ''

            try:
                OldPrice = request.POST["Prodoldprice"]
            except:
                OldPrice = ''
    
            try:
                Range = request.POST["ProdRange"]
            except:
                Range = ''

            try:
                PostType = request.POST["ProdPostType"]
            except:
                PostType = ''
            
            Product_PostRange = request.POST.getlist("PostRange")

            Product_ExePostRange = request.POST.getlist("ExePostRange")

            try:
                Prod_Net_Weight = request.POST["product_netweight"]
            except:
                Prod_Net_Weight = ''

            try:
                Prod_Packing_Weight = request.POST["product_packingweight"]
            except:
                Prod_Packing_Weight = ''

            try:
                Prod_Length_With_Packaging = request.POST["product_lengthwithpackaging"]
            except:
                Prod_Length_With_Packaging = ''

            try:
                Prod_Width_With_Packaging = request.POST["product_widthwithpackaging"]
            except:
                Prod_Width_With_Packaging = ''

            try:
                Prod_Height_With_Packaging = request.POST["product_heightwithpackaging"]
            except:
                Prod_Height_With_Packaging = ''

            this_product = Product.objects.get(ID = id)

            if (Title != '') and (len(category_list) != 0) and (Submarket != '') and (Price != '') and (PostType != ''):

                if (OldPrice == '') or ((OldPrice != Price) and (int(OldPrice) > int(Price))):

                    alert = Alert.objects.create(Part = '7', FK_User = request.user, Slug = this_product.ID, Seen = True, Status = True, FK_Staff = request.user)
                    
                    PT = None
                    R = None

                    if Title != this_product.Title:
                        this_product.Title = Title
                        this_product.save()
                        TitleField = Field.objects.create(Title = 'Title', Value = Title)
                        alert.FK_Field.add(TitleField)

                    if SubMarket.objects.get(ID = Submarket) != this_product.FK_SubMarket:
                        this_product.FK_SubMarket = SubMarket.objects.get(ID = Submarket)
                        this_product.save()
                        SubMarketField = Field.objects.create(Title = 'SubMarket', Value = SubMarket.objects.get(ID = Submarket).Title)
                        alert.FK_Field.add(SubMarketField)
                        
                    if Image != '':
                        this_product.Image = Image
                        this_product.save()
                        img_str = 'NewImage' + '#' + str(this_product.Image)
                        ImageField = Field.objects.create(Title = 'Image', Value = img_str)
                        alert.FK_Field.add(ImageField)

                    if Price != str(this_product.Price):
                        this_product.Price = Price
                        this_product.save()
                        PriceField = Field.objects.create(Title = 'Price', Value = Price)
                        alert.FK_Field.add(PriceField)

                    if PostType != '':
                        if PostType == 'آماده در انبار':
                            PT = '1'
                        elif PostType == 'تولید بعد از سفارش':
                            PT = '2'
                        elif PostType == 'سفارشی سازی فروش':
                            PT = '3'
                        elif PostType == 'موجود نیست':
                            PT = '4'

                        if this_product.Status != PT:
                            this_product.Status = PT
                            this_product.save()
                            StatusField = Field.objects.create(Title = 'ProdPostType', Value = PT)
                            alert.FK_Field.add(StatusField)            

                    if Des != this_product.Description:
                        this_product.Description = Des
                        this_product.save()
                        DescriptionField = Field.objects.create(Title = 'Description', Value = Des)
                        alert.FK_Field.add(DescriptionField)

                    if Bio != this_product.Bio:
                        this_product.Bio = Bio
                        this_product.save()
                        BioField = Field.objects.create(Title = 'Bio', Value = Bio)
                        alert.FK_Field.add(BioField)

                    if Story != this_product.Story:
                        this_product.Story = Story
                        this_product.save()
                        StoryField = Field.objects.create(Title = 'Story', Value = Story)
                        alert.FK_Field.add(StoryField)

                    if len(category_list) != 0:
                        Categori = '-'
                        for item in category_list:
                            Categori += item + '-'
                            
                        CategoryField = Field.objects.create(Title = 'Category', Value = Categori)
                        alert.FK_Field.add(CategoryField)

                        for item in this_product.FK_Category.all():
                            this_product.FK_Category.remove(item)

                        for item in category_list:
                            this_product.FK_Category.add(Category.objects.get(id = item))

                    if len(Product_PostRange) != 0:
                        Product_PR = '-'
                        for item in Product_PostRange:
                            Product_PR += item + '-'

                        PostRangeField = Field.objects.create(Title = 'PostRange', Value = Product_PR)
                        alert.FK_Field.add(PostRangeField)

                        for item in this_product.FK_PostRange.all():
                            this_product.FK_PostRange.remove(item)

                        for item in Product_PostRange:
                            this_product.FK_PostRange.add(PostRange.objects.get(id = item))
                        
                    if len(Product_ExePostRange) != 0:

                        Product_EPR = '-'
                        for item in Product_ExePostRange:
                            Product_EPR += item + '-'

                        ExePostRangeField = Field.objects.create(Title = 'ExePostRange', Value = Product_EPR)
                        alert.FK_Field.add(ExePostRangeField)

                        for item in this_product.FK_ExceptionPostRange.all():
                            this_product.FK_ExceptionPostRange.remove(item)

                        for item in Product_ExePostRange:
                            this_product.FK_ExceptionPostRange.add(PostRange.objects.get(id = item))

                    if OldPrice != '':
                        if OldPrice != this_product.OldPrice:
                            this_product.OldPrice = OldPrice
                            this_product.save()
                            OldPriceField = Field.objects.create(Title = 'OldPrice', Value = OldPrice)
                            alert.FK_Field.add(OldPriceField)
                    else:
                        if OldPrice != this_product.OldPrice:
                            this_product.OldPrice = '0'
                            this_product.save()

                    if Range != '':
                        if Range == 'سراسر کشور':
                            R = '1'
                        elif Range == 'استانی':
                            R = '2'
                        elif Range == 'شهرستانی':
                            R = '3'
                        elif Range == 'شهری':
                            R = '4'

                        if this_product.PostRangeType != R:
                            this_product.PostRangeType = R
                            this_product.save()
                            ProdRangeField = Field.objects.create(Title = 'ProdRange', Value = R)
                            alert.FK_Field.add(ProdRangeField)


                    # Product Weight Info
                    if this_product.Net_Weight != Prod_Net_Weight:
                        this_product.Net_Weight = Prod_Net_Weight
                        this_product.save()

                    if this_product.Weight_With_Packing != Prod_Packing_Weight:
                        this_product.Weight_With_Packing = Prod_Packing_Weight
                        this_product.save()
                    # Product Dimensions Info
                    if this_product.Length_With_Packaging != Prod_Length_With_Packaging:
                        this_product.Length_With_Packaging = Prod_Length_With_Packaging
                        this_product.save()

                    if this_product.Width_With_Packaging != Prod_Width_With_Packaging:
                        this_product.Width_With_Packaging = Prod_Width_With_Packaging
                        this_product.save()

                    if this_product.Height_With_Packaging != Prod_Height_With_Packaging:
                        this_product.Height_With_Packaging = Prod_Height_With_Packaging
                        this_product.save()
                        
                    return redirect('nakhll_market:Show_Product_Info',
                    Product_Slug = this_product.Slug)

                else:
                    
                    if Price == OldPrice:

                        return redirect('nakhll_market:Edit_Full_Product',
                        id = this_product.ID,
                        msg =  'قیمت فروش محصول و قیمت واقعی نمی تواند با هم برابر باشد.')

                    elif int(Price) > int(OldPrice):

                        return redirect('nakhll_market:Edit_Full_Product',
                        id = this_product.ID,
                        msg =  'قیمت واقعی نمیتواند از قیمت فروش محصول کمتر باشد.')

            else:

                return redirect('nakhll_market:Edit_Full_Product',
                id = this_product.ID,
                msg =  'عنوان - دسته بندی - حجره - شناسه - عکس - قیمت و نوع ارسال محصول اجباریست.')

        else:
            
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
            # -------------------------------------------------------------------
            # This Product
            this_product = Product.objects.get(ID = id)
            # Get All Submarket
            submarkets = SubMarket.objects.filter(Publish = True)
            # Build Class
            class Items:
                def __init__(self, category, status):
                    self.Category = category
                    self.Status = status

            # Build Class For PostRange
            class PostRangeClass:
                def __init__(self, item, status):
                    self.PostRange = item
                    self.Status = status

            # Build Class For ExePostRange
            class ExePostRange:
                def __init__(self, item, status):
                    self.ExePostRange = item
                    self.Status = status

            ItemsList = []

            for item in Category.objects.filter(Publish = True):
                item = Items(item, False)
                ItemsList.append(item)
                
            
            for item in this_product.FK_Category.all():
                for i in ItemsList:
                    if i.Category == item:
                        i.Status = True

            PostRangeList = []

            for item in PostRange.objects.all():
                newitem = PostRangeClass(item, False)
                PostRangeList.append(newitem)
                
            
            for item in this_product.FK_PostRange.all():
                for i in PostRangeList:
                    if i.PostRange == item:
                        i.Status = True

            ExePostRangeList = []

            for item in PostRange.objects.all():
                newitem = ExePostRange(item, False)
                ExePostRangeList.append(newitem)
                
            
            for item in this_product.FK_ExceptionPostRange.all():
                for i in ExePostRangeList:
                    if i.ExePostRange == item:
                        i.Status = True

            if msg != 'None':
                message = msg
                show = True
            else:
                message = ''
                show = False

            context = {
                'Users':user,
                'Profile':profile,
                'Wallet': wallets,
                'Options': options,
                'MenuList':navbar,
                'Product':this_product,
                'Categort':ItemsList,
                'SubMarket':submarkets,
                'ProPostRange':PostRangeList,
                'ProExePostRange':ExePostRangeList,
                'ShowAlart':show,
                'AlartMessage':message,
            }

            return render(request, 'nakhll_market/management/content/edit_full_product.html', context)

    else:

        return redirect("nakhll_market:AccountLogin")


# Add New Product Banner
def Add_New_Product_Banner(request, id, msg = None):

    if request.user.is_authenticated :

        if request.method == 'POST':

            try:
                Banner_Image = request.FILES["Banner_Image"]
            except:
                Banner_Image = ''

            try:
                Banner_Title = request.POST["Banner_Title"]
            except:
                Banner_Title = ''

            try:
                Banner_Seen = request.POST["Banner_Seen"]
            except:
                Banner_Seen = ''

            try:
                Banner_Status = request.POST["Banner_Status"]
            except:
                Banner_Status = ''

            if (Banner_Title != '') and (Banner_Image != ''):

                # This Product
                this_product = Product.objects.get(ID = id)
                # Create New Object
                thisbanner = ProductBanner.objects.create(FK_Product = this_product, Title = Banner_Title, Image = Banner_Image, Available = bool(Banner_Seen), Publish = bool(Banner_Status))
                # Set New Alert
                Alert.objects.create(Part = '8', FK_User = request.user, Slug = thisbanner.id, Seen = True, Status = True, FK_Staff = request.user)
                # -----------------------------------------------------------------
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

                return redirect('nakhll_market:Show_Product_Info',
                Product_Slug = this_product.Slug)

            else:

                return redirect('nakhll_market:Add_New_Product_Banner',
                id = this_product.id,
                msg =  'عنوان و عکس بنر حجره نمی تواند خالی باشد.')

        else:
            
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
            # -------------------------------------------------------------------
            # This Product
            this_product = Product.objects.get(ID = id)

            if msg != 'None':
                message = msg
                show = True
            else:
                message = ''
                show = False

            context = {
                'Users':user,
                'Profile':profile,
                'Wallet': wallets,
                'Options': options,
                'MenuList':navbar,
                'Product':this_product,
                'ShowAlart':show,
                'AlartMessage':message,
            }

            return render(request, 'nakhll_market/management/content/add_new_product_banner.html', context)

    else:

        return redirect("nakhll_market:AccountLogin")

        
# Add New Product Attribut
def Add_New_Product_Attribute(request, id, msg = None):

    if request.user.is_authenticated :

        if request.method == 'POST':

            try:
                AttrTitle = request.POST["Attribute_Title"]
            except:
                AttrTitle = ''

            try:
                AttrValue = request.POST["Attribute_Value"]
            except:
                AttrValue = ''

            this_product = Product.objects.get(ID = id)

            if (AttrTitle != '') and (AttrValue != ''):

                attrtilte = AttrTitle.split('|')
                attrproduct = AttrProduct.objects.create(FK_Product = this_product, FK_Attribute = Attribute.objects.get(Title = attrtilte[0], Unit = attrtilte[1]), Value = AttrValue)

                Alert.objects.create(Part = '11', FK_User = request.user, Slug = attrproduct.id, Seen = True, Status = True, FK_Staff = request.user)

                return redirect('nakhll_market:Add_New_Product_Attribute',
                id = this_product.ID,
                msg = None)

            else:

                return redirect('nakhll_market:Add_New_Product_Attribute',
                id = this_product.ID,
                msg =  'مقادیر عنوان و واحد نمی تواند خالی باشد.')

        else:
            
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
            # -------------------------------------------------------------------
            # Get All Attribute
            pubattributes = Attribute.objects.filter(Publish = True)
            # This Product
            this_product = Product.objects.get(ID = id)

            if msg != 'None':
                message = msg
                show = True
            else:
                message = ''
                show = False

            context = {
                'Users':user,
                'Profile':profile,
                'Wallet': wallets,
                'Options': options,
                'MenuList':navbar,
                'Attributes':pubattributes,
                'Product':this_product,
                'ShowAlart':show,
                'AlartMessage':message,
            }

            return render(request, 'nakhll_market/management/content/add_new_product_attribute.html', context)

    else:

        return redirect("nakhll_market:AccountLogin")


# Add New Product AttrPrice
def Add_New_Product_AttrPrice(request, id, msg = None):

    if request.user.is_authenticated :

        if request.method == 'POST':
            
            try:
                AttrPrice_Value = request.POST["AttributePrice_Value"]
            except :
                AttrPrice_Value = ''

            try:
                AttrPrice_Exp = request.POST["AttributePrice_Exp"]
            except :
                AttrPrice_Exp = ''

            try:
                AttrPrice_Unit = request.POST["AttributePrice_Unit"]
            except :
                AttrPrice_Unit = ''

            try:
                AttrPrice_Des = request.POST["AttributePrice_Des"]
            except :
                AttrPrice_Des = ''
            
            this_product = Product.objects.get(ID = id)

            if (AttrPrice_Value != '') and (AttrPrice_Exp != '') and (AttrPrice_Unit != ''):

                if AttrPrice.objects.filter(FK_Product = this_product, Value = AttrPrice_Value, ExtraPrice = AttrPrice_Exp, Unit = AttrPrice_Unit).exists():

                    return redirect('nakhll_market:Add_New_Product_AttrPrice',
                    id = this_product.ID,
                    msg =  'این ارزش ویژگی تکراری می باشد.')

                else:

                    attrprice = AttrPrice.objects.create(FK_Product = this_product, Value = AttrPrice_Value, ExtraPrice = AttrPrice_Exp, Unit = AttrPrice_Unit, Publish = False)

                    if AttrPrice_Des != '':
                        attrprice.Description = AttrPrice_Des
                        attrprice.save()

                    Alert.objects.create(Part = '17', FK_User = request.user, Slug = attrprice.id, Seen = True, Status = True, FK_Staff = request.user)

                    return redirect('nakhll_market:Add_New_Product_AttrPrice',
                    id = this_product.ID,
                    msg = None)

            else:

                return redirect('nakhll_market:Add_New_Product_AttrPrice',
                id = this_product.ID,
                msg =  'مقادیر ستاره دار نمی تواند خالی باشد.')

        else:
            
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
            # -------------------------------------------------------------------
            # This Product
            this_product = Product.objects.get(ID = id)

            if msg != 'None':
                message = msg
                show = True
            else:
                message = ''
                show = False

            context = {
                'Users':user,
                'Profile':profile,
                'Wallet': wallets,
                'Options': options,
                'MenuList':navbar,
                'Product':this_product,
                'ShowAlart':show,
                'AlartMessage':message,
            }

            return render(request, 'nakhll_market/management/content/add_new_product_attrprice.html', context)

    else:

        return redirect("nakhll_market:AccountLogin")