from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
from kavenegar import *
import datetime
import threading
from django.utils.datastructures import MultiValueDictKeyError
from django.contrib.auth.models import User
from .models import Alert, Product, Profile, Shop, Category, Option_Meta, Market, SubMarket, Message, User_Message_Status, BankAccount, ShopBanner, ProductBanner, Attribute, AttrPrice, AttrProduct, Field, PostRange, AttrProduct, AttrPrice
from Payment.models import Coupon, Wallet, Factor, FactorPost
from django.urls import reverse

# --------------------------------------------------------------------------------------------------------------------------------------
# base data for base template
def baseData(request, activeSidebarMenu):
    # user profile 
    userProfile = request.user.User_Profile
    # user wallet 
    userWallet = request.user.WalletManager
    # Get Menu Item
    options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
    # Get Nav Bar Menu Item
    navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
    # number of unseen massagged
    new_message_count = Message.objects.filter(FK_Users__FK_User=request.user, FK_Users__SeenStatus=False).count()
    # side bar menu
    sidebarMenu = [
        {'id':'dasboard', 'name':'داشبورد', 'url':reverse('nakhll_market:Dashboard'), 'class':'fas fa-id-badge', 'isActive':False, 'staffOnly':False},
        {'id':'transaction', 'name':'تراکنش ها', 'url':reverse('nakhll_market:Transaction'), 'class':'fad fa-clipboard-list', 'isActive':False, 'staffOnly':False},
        {'id':'factor', 'name':' فاکتور ها', 'url':reverse('nakhll_market:Factor'), 'class':'fas fa-file-invoice-dollar', 'isActive':False, 'staffOnly':False},
        {'id':'ticketing', 'name':'پشتیبانی', 'url':reverse('nakhll_market:Ticketing'), 'class':'fad fa-user-headset', 'isActive':False, 'staffOnly':False},
        {'id':'userShop', 'name':'مدیریت حجره', 'url':reverse('nakhll_market:UserShops'), 'class':'fas fa-store', 'isActive':False, 'staffOnly':False},
        {'id':'review', 'name':'نقدها و نظرات', 'url':reverse('nakhll_market:Review'), 'class':'fad fa-comments-alt', 'isActive':False, 'staffOnly':False},
        {'id':'alert', 'name':'هشدار ها', 'url':reverse('nakhll_market:Alert'), 'class':'fas fa-bell', 'isActive':False, 'staffOnly':True},
        {'id':'allUser', 'name':'کاربران', 'url':reverse('nakhll_market:Show_All_User_Info'), 'class':'fas fa-users', 'isActive':False, 'staffOnly':True},
        {'id':'coupon', 'name':'کوپن ها', 'url':reverse('nakhll_market:ManagementCoupunList'), 'class':'fad fa-window-maximize', 'isActive':False, 'staffOnly':True},
        {'id':'allShop', 'name':'مدیریت محتوا', 'url':reverse('nakhll_market:Show_All_Content'), 'class':'fas fa-sliders-h', 'isActive':False, 'staffOnly':True},
    ]
    for n, menu in enumerate(sidebarMenu):
        if menu['id']==activeSidebarMenu:
            sidebarMenu[n]['isActive'] = True

    return {
        'userProfile':userProfile,
        'userWallet':userWallet,
        'Options': options,
        'MenuList':navbar,
        'userMessagesCount':new_message_count,
        'ShowAlart':False,
        'sidebarMenu':sidebarMenu,
    }


# get post method data and put to context
def getPostData(request, context, fields, undefined=''):
    for field in fields:
        context[field] = request.POST.get(field, undefined)
    return context


# Show All User Info
def Show_All_User_Info(request):

    if request.user.is_staff:
        context = baseData(request, 'allUser')
        fields = ['First_Name', 'Last_Name', 'PhoneNumber']
        if request.method == 'POST':
            context = getPostData(request, context, fields)
            profiles = Profile.objects.filter(
                FK_User__first_name__icontains=context['First_Name'], 
                FK_User__last_name__icontains=context['Last_Name'],
                MobileNumber__icontains=context['PhoneNumber'])

        elif request.method == 'GET':
            # Get User Profile
            profiles = Profile.objects.all()
            # initialize fields
            context = getPostData(request, context, fields)
        else:
            HttpResponse('this method is not allowed!', status_code=405)

    else:
        return redirect("nakhll_market:AccountLogin")

    # Paginate Profiles
    profilesPaginator = Paginator (profiles, 20)
    page = request.GET.get('page')

    profiles = profilesPaginator.get_page(page)
    context['Profiles']=profiles
    # Get All User Count
    context['UserCount']=Profile.objects.all().count()
    # Shop Count
    context['ShopCount']=Shop.objects.all().count()
    # Publish Shop Count
    context['PublishShopCount']=Shop.objects.filter(Publish = False).count()
    # number of shop manager
    context['ShoperCount']=Shop.objects.values('FK_ShopManager').distinct().count()
    # Block Count
    context['BlockCount']=User.objects.filter(is_active = False).count()

    return render(request, 'nakhll_market/management/content/show_all_user_info.html', context)
    

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

    if request.user.is_staff :
        context = baseData(request, 'allUser')
        fields = ['User_FirstName', 'User_LastName', 'User_NationalCode',
            'User_MobileNumber', 'User_Amount', 'status']
        if request.method == 'POST':
            context = getPostData(request, context, fields)
            if context['status'] != '1':
                context['status'] = context['status'].replace('', '0')
            context['status'] = int(context['status'])

            if (context['User_FirstName'] != '') and (context['User_LastName'] != '') and (context['User_NationalCode'] != '') and (context['User_MobileNumber'] != ''):

                if (len(context['User_NationalCode']) == 10) and (len(context['User_MobileNumber']) == 11):

                    if not Profile.objects.filter(MobileNumber = context['User_MobileNumber'], NationalCode = context['User_NationalCode']).exists():

                        # Build User
                        new_user = User(username = context['User_MobileNumber'], first_name = context['User_FirstName'], last_name = context['User_LastName'] )
                        new_user.save()
                        # Set Password
                        new_user.set_password(context['User_NationalCode'])
                        new_user.save()
                        # Build Profile
                        new_profile = Profile(FK_User = new_user, MobileNumber = context['User_MobileNumber'], NationalCode = context['User_NationalCode'])
                        new_profile.save()
                        # Build User Wallet
                        if (context['User_Amount'] != '') and (context['User_Amount'] != 0):
                            new_user_wallet = Wallet(FK_User = new_user, Inverntory = context['User_Amount'])
                            new_user_wallet.save()

                            # Get Description
                            transaction_description = Option_Meta.objects.get(Title = 'add_new_user').Value_1
                            # Set Transaction
                            transaction = Transaction(FK_User = new_user, Price = context['User_Amount'], Type = '1', FK_Wallet = new_user_wallet, Description = transaction_description)
                            transaction.save()
                        else:
                            new_user_wallet = Wallet(FK_User = new_user)
                            new_user_wallet.save()

                        # Send SMS To User
                        url = 'https://api.kavenegar.com/v1/4E41676D4B514A4143744C354E6135314E4F47686B33594B747938794D30426A784A692F3579596F3767773D/verify/lookup.json' 
                        params = {'receptor': context['User_MobileNumber'], 'token' : new_user.username, 'token2' : new_profile.NationalCode, 'template' : 'nakhll-addnewuser'}
                        result = requests.post(url, params = params)
                        Message = result.json()
                        MessageReturn = Message["return"]
                        print(MessageReturn["status"])


                        if context['status'] == 1:
       
                            return redirect("nakhll_market:Add_New_Shop", id = new_user.id)

                        elif context['status'] == 0:

                            return redirect("nakhll_market:Show_All_User_Info")

                    else:
                        context['ShowAlart'] = True
                        context['AlartMessage'] = 'کاربری با این شماره موبایل یا کد ملی قبلا ثبت شده است!'

                else:
                    context['ShowAlart'] = True
                    context['AlartMessage'] = 'کد ملی 10 و شماره موبایل 11 رقم باید باشد!'

            else:

                context['ShowAlart'] = True
                context['AlartMessage'] = 'نام، نام خانوادگی، کد ملی و شماره موبایل نمی تواند خالی باشد!'

        elif request.method == 'GET':
            context = getPostData(request, context, fields)
            context['status'] = 0

        else:
            HttpResponse('this method is not allowed!')

    else:
        return redirect("nakhll_market:AccountLogin")

    return render(request, 'nakhll_market/management/content/add_new_user.html', context)


# Add New User`s Shop
def Add_New_Shop(request, id):

    if request.user.is_authenticated :
        context = baseData(request, 'allShop')
        fields = ['Shop_Title', 'Shop_Slug']
        context = getPostData(request, context, fields)
        subMarkets = request.POST.getlist("Shop_SubMarket")
        context['Shop_SubMarket'] = subMarkets
        # Get This User
        new_user = User.objects.get(id = id)
        if request.method == 'POST':
            if (context['Shop_Title'] != '') and (context['Shop_Slug'] != '') and (len(subMarkets) != 0):

                if not Shop.objects.filter(Slug = context['Shop_Slug']).exists():

                    # Build Shop
                    new_shop = Shop(FK_ShopManager = new_user, Title = context['Shop_Title'], Slug = context['Shop_Slug'], Publish = True, Available = False, FK_User = request.user)
                    new_shop.save()
                    # Set SubMarket
                    try:
                        for item in subMarkets:
                            this_subMarket = SubMarket.objects.get(ID = item)
                            new_shop.FK_SubMarket.add(this_subMarket)
                            
                        return redirect("nakhll_market:Add_New_Product", shop = new_shop.ID)
                    except:
                        new_shop.delete()
                        context['ShowAlart'] = True
                        context['AlartMessage'] = 'در هنگام ثبت بازارچه برای حجره شما مشکلی رخ داده است. لطفا با پشتیبانی تماس بگیرید.'
                        
                else:
                    context['ShowAlart'] = True
                    context['AlartMessage'] = 'حجره ای با این شناسه موجود می باشد!'

            else:
                context['ShowAlart'] = True
                context['AlartMessage'] = 'عنوان، شناسه، راسته حجره نمی تواند خالی باشد!'
        
        else:
            context['ShowAlart'] = False

    else:

        return redirect("nakhll_market:AccountLogin")

    context['ThisUser'] = new_user
    # Get All SubMarkets
    subMarkets = SubMarket.objects.filter(Publish = True)        
    context['SubMarkets'] = subMarkets
    return render(request, 'nakhll_market/management/content/add_new_shop.html', context)

# Add New Product In User`s Shop
def Add_New_Product(request, shop):

    if request.user.is_authenticated :

        fields = ['prod_title', 'ProdCat', 'ProdSub', 
            'prod_Price', 'slugProd', 'prod_weight']
        context = baseData(request, 'allUser')
        context = getPostData(request, context, fields)
        context['Product_Image'] = request.FILES.get('Product_Image')
        Categories = request.POST.getlist("ProdCat")

        if request.method == 'POST':

            if (context['prod_title'] != '') and \
                (context['slugProd'] != '') and \
                (len(Categories) != 0) and \
                (context['ProdSub'] != '') and \
                (context['prod_Price'] != '') and \
                (context['prod_weight'] != '') and \
                (context['Product_Image'] != '' or context['Product_Image'] != None):

                if not Product.objects.filter(Slug = context['slugProd']).exists():

                    # Get This User
                    this_shop = Shop.objects.get(ID = shop)
                    # Get This Submarket
                    context['ProdSub'] = SubMarket.objects.get(ID = context['ProdSub'])
                    try:
                        # Build Product
                        # TODO POSTRANGE and STATUS must be get from user not set fixxed,
                        # at the most low level inform the user about this variables
                        new_product = Product.objects.create(Title = context['prod_title'], 
                                                            Slug = context['slugProd'], 
                                                            FK_SubMarket = context['ProdSub'], 
                                                            Image = context['Product_Image'], 
                                                            FK_Shop = this_shop, 
                                                            Price = context['prod_Price'], 
                                                            PostRangeType = '1', 
                                                            Status = '4', 
                                                            Available = False, 
                                                            Publish = True, 
                                                            FK_User = request.user, 
                                                            Net_Weight = context['prod_weight'],
                                                            )
                        # Set Category
                        for item in Categories:
                            this_category = Category.objects.get(pk = item)
                            new_product.FK_Category.add(this_category)

                        # TODO , when process is successful it must show some green alert
                        context['ShowAlart'] = True
                        context['AlartMessage'] = 'محصول شما با موفقیت ثبت شد.'
                    
                    except:
                        try:
                            new_product.delete()
                        except:
                            pass
                        context['ShowAlart'] = True
                        context['AlartMessage'] = 'در فرایند ذخیره سازی محصول مشکلی رخ داده است. لطفا با پشتیبانی تماس بگیرید.'
                    
                else:
                    context['ShowAlart'] = True
                    context['AlartMessage'] = 'محصولی با این شناسه موجود می باشد!'

            else:

                context['ShowAlart'] = True
                context['AlartMessage'] = 'عنوان، شناسه، راسته، دسته بندی، قیمت، وزن و عکس محصول نمی تواند خالی باشد!'

        elif request.method == 'GET':
            pass
        else:
            HttpResponse('this method is not allowed!', status_code=405)
        
    else:

        return redirect("nakhll_market:AccountLogin")

    # Get This Shop
    context['ThisShop'] = Shop.objects.get(ID = shop)
    # Get All Categories
    context['Categories'] = Category.objects.filter(Available = True, Publish = True)
    # Get All Shop`s Submarkets
    context['SubMarkets'] = context['ThisShop'].FK_SubMarket.all()

    return render(request, 'nakhll_market/management/content/add_new_product.html', context)

# Add User`s Bank Account Info
def Add_Bank_Account(request, id):
    # Check User Status
    '''
    TODO this function get id of user that want ot add bank account but 
    get the first_name and last name of him/her at the same time.
    it can be for that because a user can add bank account that is not for shopManager
    if this is not the case i think this is a bug!
    and after that i think we must make that a user not just get first_name and last_name at field
    '''

    if request.user.is_authenticated :

        fields = ['Shop_CreditCardNumber', 'Shop_ShabaBankNumber', 'Shop_AccountOwner']
        context = baseData(request, 'allUser')
        context = getPostData(request, context, fields)
        # Get This User
        context['ThisUser'] = User.objects.get(id = id)

        if request.method == 'POST': 
            # TODO every user can have only one account?
            if BankAccount.objects.filter(FK_Profile = Profile.objects.get(FK_User = context['ThisUser'])).exists():

                context['ShowAlart'] = True
                context['AlartMessage'] = 'یک حساب بانکی به نام {} {} موجود می باشد.'.format(
                            context['ThisUser'].first_name, context['ThisUser'].last_name)

            else:

                if (context['Shop_CreditCardNumber'] != '') and \
                    (context['Shop_ShabaBankNumber'] != '') and \
                    (context['Shop_AccountOwner'] != ''):

                    if (len(context['Shop_ShabaBankNumber']) == 24) and (len(context['Shop_CreditCardNumber']) == 16):

                        BankAccount.objects.create(FK_Profile = Profile.objects.get(FK_User = context['ThisUser']), 
                                CreditCardNumber = context['Shop_CreditCardNumber'], 
                                ShabaBankNumber = context['Shop_ShabaBankNumber'], 
                                AccountOwner = context['Shop_AccountOwner'])

                        context['ShowAlart'] = True
                        context['AlartMessage'] = 'اکانت با موفقیت ثبت شد.'

                    else:

                        context['ShowAlart'] = True
                        context['AlartMessage'] = 'شماره شباء و شماره کارت باید 24 و 16 رقم باشند!'

                else:

                    context['ShowAlart'] = True
                    context['AlartMessage'] = 'نام صاحب حساب، شماره کارت و شماره شباء نمی تواند خالی باشد!'

        else:

            # Get Bank Account
            # TODO in the get method it get user account and put its data in the field 
            # maybe it's better to load data bank account and show then in a table 
            if BankAccount.objects.filter(FK_Profile = Profile.objects.get(FK_User = context['ThisUser'])).exists():
                account = BankAccount.objects.get(FK_Profile = Profile.objects.get(FK_User = context['ThisUser']))
            else:
                account = None

            context['Account'] = account

    else:

        return redirect("nakhll_market:AccountLogin")

    return render(request, 'nakhll_market/management/content/add_user_bank_account_info.html', context)

# Show All Shoper User Info
def Show_All_Shoper_User_Info(request):

    if request.user.is_staff :
        # Get shop manager user Profile
        profiles_id =  Shop.objects.values_list('FK_ShopManager').distinct()
        profiles = Profile.objects.filter(FK_User__in=profiles_id)

        context = baseData(request, 'allUser')
        context['Profiles']=profiles
        # Get All User Count
        context['UserCount']=Profile.objects.all().count()
        # Shop Count
        context['ShopCount']=Shop.objects.all().count()
        # Publish Shop Count
        context['PublishShopCount']=Shop.objects.filter(Publish = False).count()
        # number of shop manager
        context['ShoperCount']=Shop.objects.values('FK_ShopManager').distinct().count()
        # Block Count
        context['BlockCount']=User.objects.filter(is_active = False).count()

        return render(request, 'nakhll_market/management/content/show_all_user_info.html', context)

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
def GetShopStatistics(request):
    # Build Statistics Class
    class StatisticsClass:
        def __init__(self,  Product_Count, Not_Count, Off_Count, False_Count, userProfile, userWallet, options, navbar):
            self.Product_Count = Product_Count
            self.Not_Count = Not_Count
            self.Off_Count = Off_Count
            self.False_Count = False_Count
            self.userProfile = userProfile
            self.userWallet = userWallet
            self.options = options
            self.navbar = navbar

    # Get All Product
    product_count = Product.objects.all().count()
    # Not Product Count
    not_count = Product.objects.filter(Status = '4').count()
    # Off Product Count
    off_count = Product.objects.filter(Available = False).count()
    # False Product Count
    false_count = Product.objects.filter(Publish = False).count()
    # user profile 
    userProfile = request.user.User_Profile
    # user wallet 
    userWallet = request.user.WalletManager
    # Get Menu Item
    options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
    # Get Nav Bar Menu Item
    navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')

    return StatisticsClass(product_count, not_count, off_count, false_count, userProfile, userWallet, options, navbar)


# Show All Content
def Show_All_Content(request):
    search_list = None
    if request.user.is_staff :
        # Get Statistics
        Statistic = GetShopStatistics(request)
        if request.method == 'POST':
            shop_title = request.POST.get("shop_title")
            shop_manager_first_name = request.POST.get("shop_manager_first_name")
            shop_manager_last_name = request.POST.get("shop_manager_last_name")
            Shops = Shop.objects.filter(
                Title__icontains = shop_title,
                FK_ShopManager__first_name__icontains = shop_manager_first_name,
                FK_ShopManager__last_name__icontains = shop_manager_last_name
                )
        elif request.method == 'GET':
            Shops = Shop.objects.all()
        else:
            return HttpResponse('this method is not allowed!')

        # pagination of all shops
        allShopListPaginator = Paginator (Shops, 30)
        page = request.GET.get('page')
        Shops = allShopListPaginator.get_page(page)

        context = baseData(request, 'allShop')
        context['ProductCount']=Statistic.Product_Count,
        context['NotProductCount']=Statistic.Not_Count,
        context['OffProductCount']=Statistic.Off_Count,
        context['FalseProductCount']=Statistic.False_Count,
        context['Shops']=Shops

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
        context = baseData(request, 'allShop')

        if request.method == 'POST':
            image = request.FILES.get("Shop_Image", '')
            title = request.POST.get("Shop_Title", '')
            slug = request.POST.get("Shop_Slug", '')
            des = request.POST.get("Shop_Des", '')
            state = request.POST.get("Shop_State", '')
            bigcity = request.POST.get("Shop_BigCity", '')
            city = request.POST.get("Shop_City", '')
            bio = request.POST.get("Shop_Bio", '')
            sat = request.POST.get("SATCheck", '')
            sun = request.POST.get("SUNCheck", '')
            mon = request.POST.get("MONCheck", '')
            tue = request.POST.get("TUECheck", '')
            wed = request.POST.get("WEDCheck", '')
            thu = request.POST.get("THUCheck", '')
            fri = request.POST.get("FRICheck", '')
            seen = request.POST.get("Shop_Seen", '')
            status = request.POST.get("Shop_Status", '')
            submarkets = request.POST.getlist("Shop_SubMarket")
            user = request.POST.getlist("Shop_User")

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
                        msg =  'راسته، استان، شهرستان و شهر نمی تواند خالی باشد.'

                else:
                    msg =  'عنوان و شناسه نمی تواند خالی باشد - شناسه تکراری می باشد.'

            else:
                msg =  'شما باید یک کاربر را به عنوان حجره دار انتخاب نمایید.'


        elif request.method == 'GET':
            pass
        else:
            HttpResponse('this method is not allowed!', status_code=405)
            
        # Get All Submarket
        allsubmarket = SubMarket.objects.filter(Available = True, Publish = True)

        if msg != 'None':
            message = msg
            show = True
        else:
            message = ''
            show = False

        context['SubMarkets'] = allsubmarket
        context['ShowAlart'] = show
        context['AlartMessage'] = message

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