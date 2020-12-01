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
from .models import (
                    Alert, 
                    Product, 
                    Profile, 
                    Shop, 
                    Category, 
                    Option_Meta, 
                    Market, 
                    SubMarket, 
                    Message, 
                    User_Message_Status, 
                    BankAccount, 
                    ShopBanner, 
                    ProductBanner, 
                    Attribute, 
                    AttrPrice, 
                    AttrProduct, 
                    Field, 
                    PostRange, 
                    AttrProduct, 
                    AttrPrice
                    )
from Payment.models import Coupon, Wallet, Factor, FactorPost
from django.urls import reverse
'''
TODO
Use standard styles such as camle case, pascal and ...
Use of decoratore for checking is_authenticated or is_staff instead of if condition
Use of class bass view instead of functions and using if condition
Use slogify instead of getting from user for Shop and Product Slug
'''
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

# --------------------------------------------------------------------------------------------------------------------------------------
# allUser module
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

    if request.user.is_staff :

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
        context = getPostData(request, context, fields)
        if request.method == 'POST':
            if context['status'] != '1':
                context['status'] = context['status'].replace('', '0')
            context['status'] = int(context['status'])

            if (context['User_FirstName'] != '') and (context['User_LastName'] != '') and (context['User_NationalCode'] != '') and (context['User_MobileNumber'] != ''):

                if (len(context['User_NationalCode']) == 10) and (len(context['User_MobileNumber']) == 11):

                    if not Profile.objects.filter( Q(MobileNumber = context['User_MobileNumber']) and Q(NationalCode = context['User_NationalCode'])).exists():

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
            context['status'] = 0

        else:
            HttpResponse('this method is not allowed!')

    else:
        return redirect("nakhll_market:AccountLogin")

    return render(request, 'nakhll_market/management/content/add_new_user.html', context)

# Add New User`s Shop
def Add_New_Shop(request, id):

    if request.user.is_staff :
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

    if request.user.is_staff :

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

    if request.user.is_staff :

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
        if request.method == 'GET':
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
            return HttpResponse('this method is not allowed!', status_code=405)

    else:

        return redirect("nakhll_market:AccountLogin")

# Show User Info In Managment Section
def Management_Show_User_Info(request, id):

    # Check User Status
    if request.user.is_staff :

        if request.method == 'GET':

            context = baseData(request, 'allUser')
            # Get Select User
            user_select = User.objects.get(id = id)
            # Get Select Profile
            profile_select = Profile.objects.get(FK_User = user_select)

            context['User_Selected'] = user_select
            context['Profile_Selected'] = profile_select

            return render(request, 'nakhll_market/management/content/show_user_info.html', context)

        else:
            HttpResponse('this method is not allowed!', status_code=405)

    else:

        return redirect("nakhll_market:AccountLogin")

# Edit User Info In Managment Section
def Management_Edit_User_Info(request, id):
    '''
    TODO this page is a very ... page, it only give three option to modify:
        1-username
        2-nationalcode
        3-mobilenumber
    editing bank account is not possible in site!
    if the user modify all option alert message showed in oneline
    '''

    if request.user.is_staff :
        
        # base data
        fields = ['username', 'nationalcode', 'mobilenumber']
        context = baseData(request, 'allUser')
        context = getPostData(request, context, fields)
        # Get Select User
        context['User_Selected'] = User.objects.get(id = id)
        # Get Select Profile
        context['Profile_Selected'] = Profile.objects.get(FK_User = context['User_Selected'])

        if request.method == 'POST':
            context['AlartMessage'] = ''
            # Check New Data
            if (context['username'] == context['User_Selected'].username) and\
            (context['nationalcode'] == context['Profile_Selected'].NationalCode) and\
            (context['mobilenumber'] == context['Profile_Selected'].MobileNumber):
                context['AlartMessage'] =  'شما تغییری ایجاد نکرده اید!'
            else:
                if (context['username'] != context['User_Selected'].username):
                    try:
                        context['User_Selected'].username = context['username']
                        context['User_Selected'].save()
                        context['AlartMessage'] =  'نام کاربری با موفقیت اصلاح شد.'
                    except:
                        if Profile.objects.filter(NationalCode = context['nationalcode']).exists():
                            context['AlartMessage'] =  'نام کاربری وارد شده تکراری می باشد!'
                        else:
                            context['AlartMessage'] =  'نام کاربری وارد شده مطابق الگو ها نمی باشد!'

                if (context['nationalcode'] != context['Profile_Selected'].NationalCode):
                    try:
                        context['Profile_Selected'].NationalCode = context['nationalcode']
                        context['Profile_Selected'].save()
                        if context['AlartMessage'] != '':
                            context['AlartMessage'] += '\n'
                            context['AlartMessage'] +=  'کد ملی با موفقیت اصلاح شد.'
                    except:
                        if Profile.objects.filter(NationalCode = context['nationalcode']).exists():
                            context['AlartMessage'] =  'کد ملی وارد شده تکراری می باشد!'
                        else:
                            context['AlartMessage'] =  'کد ملی وارد شده مطابق الگو ها نمی باشد!'

                if (context['mobilenumber'] != context['Profile_Selected'].MobileNumber):
                    try:
                        context['Profile_Selected'].MobileNumber = context['mobilenumber']
                        context['Profile_Selected'].save()
                        if context['AlartMessage'] != '':
                            context['AlartMessage'] += '\n'
                            context['AlartMessage'] +=  'شماره موبایل با موفقیت اصلاح شد.'
                    except:
                        if Profile.objects.filter(MobileNumber = context['mobilenumber']).exists():
                            context['AlartMessage'] =  'شماره موبایل وارد شده تکراری می باشد!'
                        else:
                            context['AlartMessage'] =  'شماره موبایل وارد شده مطابق الگو ها نمی باشد!'
                        
            context['ShowAlart'] = True
            return render(request, 'nakhll_market/management/content/edit_user_info.html', context)

        else:

            context['ShowAlart'] = False
            return render(request, 'nakhll_market/management/content/edit_user_info.html', context)

    else:

        return redirect("nakhll_market:AccountLogin")

# Content Section ------------------------------------

# Show All Content
def Show_All_Content(request):
    '''
    show_all_content return all shops of site
    it support two methods of get and post
    get method return all shops
    post method used for filtering and return shops based on the post data
    and is for staff users
    '''
    if request.user.is_staff :

        fields = ['shop_title', 'shop_manager_first_name', 'shop_manager_last_name']
        context = baseData(request, 'allShop')
        context = getPostData(request, context, fields)
        if request.method == 'POST':
            Shops = Shop.objects.filter(
                Title__icontains = context['shop_title'],
                FK_ShopManager__first_name__icontains = context['shop_manager_first_name'],
                FK_ShopManager__last_name__icontains = context['shop_manager_last_name']
                )
        elif request.method == 'GET':
            # check request is a redirect from change methods
            if request.GET.get('message'):
                context['ShowAlart'] = True
                context['AlartMessage'] = request.GET.get('message')
            Shops = Shop.objects.all()
        else:
            return HttpResponse('this method is not allowed!', status_code=405)

        # pagination of all shops
        allShopListPaginator = Paginator (Shops, 30)
        page = request.GET.get('page')
        Shops = allShopListPaginator.get_page(page)
        context['Shops'] = Shops
        # Get All Product
        context['ProductCount'] = Product.objects.all().count()
        # Not Product Count
        context['NotProductCount'] = Product.objects.filter(Status = '4').count()
        # Off Product Count
        context['OffProductCount'] = Product.objects.filter(Available = False).count()
        # False Product Count
        context['FalseProductCount'] = Product.objects.filter(Publish = False).count()

        return render(request, 'nakhll_market/management/content/show_all_content.html', context)

    else:

        return redirect("nakhll_market:AccountLogin")

# Change Shop Seen Status
def Change_Shop_Status(request, attribute, id):
    '''
    Change_Shop_Status change shop and all of its product "Available" and "Publish" attribute
    the algorithm loop over all products of a shop and maybe there is a better way
    only GET method is allowed
    and is for staff users
    TODO it query shop and all its product and then loop over the product and change attribute 
    and then change shop attribute i think it's better to use stored procedure
    '''

    if request.user.is_staff :

        if request.method == 'GET':
            # Get This Shop
            this_shop = Shop.objects.filter(pk=id)
            if this_shop.exists():
                this_shop = this_shop[0]
                # Get All Shop`s Product
                all_product = Product.objects.filter(FK_Shop = this_shop)
                # check attribute
                if attribute == 'Available':
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
                        
                elif attribute == 'Publish':
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

                else:
                    message = 'ویژگی مورد نظر تعریف نشده است.'
                    # redirect to with parameter
                    return redirect('{}?{}'.format(reverse("nakhll_market:Show_All_Content"), 
                            'message={}'.format(message)))

                message = 'تغییرات با موفقیت انجام شد.'
            else:
                message = 'خطایی رخ داده است. فروشگاه مورد نظر پیدا نشد.'
            # redirect to with parameter
            return redirect('{}?{}'.format(reverse("nakhll_market:Show_All_Content"), 
                            'message={}'.format(message)))
        
        else:
            HttpResponse('this method is not allowed!', status_code=405)

    else:

        return redirect("nakhll_market:AccountLogin")

# Show Shop Info
def Show_Shop_Info(request, id):
    '''
    return information about the shop
    only get method is allowed
    get the id of shop
    TODO for the calculation of number of sales and ... it needs stored procedure
    TODO shop banners are a link to show them but don't work
    '''

    if request.user.is_authenticated :

        if request.method == 'GET':

            context = baseData(request, 'allShop')
            try:
                # Get This Shop
                context['ThisShop'] = Shop.objects.get(pk = id)
                # Get All Shop`s Products
                context['ThisShopProducts'] = Product.objects.filter(FK_Shop = context['ThisShop'])
                # Get All Shop`s Banners
                context['ThisShopBanners'] = ShopBanner.objects.filter(FK_Shop = context['ThisShop'])
                # Get SubMarkets of the shop
                context['SubMarkets'] = context['ThisShop'].FK_SubMarket.all()
                # Get Shop Holiday
                context['Week'] = context['ThisShop'].Holidays.split('-')

                # TODO number of sales of a shop must be a stored procedure  
                # Get All Shop`s Sale
                AllSales = []
                AllSales_Send = []

                for item in Factor.objects.filter(PaymentStatus = True, Publish = True):
                    for factor_item in item.FK_FactorPost.all():
                        if factor_item.FK_Product.FK_Shop == context['ThisShop']:
                            if item.OrderStatus == '5':
                                AllSales_Send.append(item)
                                AllSales.append(item)
                            else:
                                AllSales.append(item)

                AllSales = list(dict.fromkeys(AllSales))
                AllSales_Send = list(dict.fromkeys(AllSales_Send))
                
                context['ThisShop_Sales_Count'] = len(AllSales)
                context['ThisShop_Sales_ISSend_Count'] = len(AllSales_Send)

                return render(request, 'nakhll_market/management/content/show_shop_info.html', context)

            except:
                # return a message that this shop does not exist
                message = 'خطایی رخ داده است. فروشگاه مورد نظر پیدا نشد.'
                # redirect to show_all_content with message
                return redirect('{}?{}'.format(reverse("nakhll_market:Show_All_Content"), 
                                'message={}'.format(message)))
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

        return redirect("nakhll_market:Show_Shop_Info", id = this_product.FK_Shop.ID)

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

        return redirect("nakhll_market:Show_Shop_Info", id = this_product.FK_Shop.ID)

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

        return redirect("nakhll_market:Show_Shop_Info", id = this_banner.FK_Shop.ID)

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

        return redirect("nakhll_market:Show_Shop_Info", id = this_banner.FK_Shop.ID)

    else:

        return redirect("nakhll_market:AccountLogin")


# Show Product Info
def Show_Product_Info(request, Product_Slug):

    if request.user.is_authenticated :

        context = baseData(request, 'allShop')
        # Get This Product
        this_product = get_object_or_404(Product, Slug = Product_Slug)
        # Get All Product Banner
        this_banners = ProductBanner.objects.filter(FK_Product = this_product)
        # Get Sales Product Count
        context['ThisProduct_Sales_Count'] = \
            FactorPost.objects.filter(FK_Product=this_product).exclude(ProductStatus='0').count()
        context['ThisProduct_Sales_ISSend_Count'] = \
            FactorPost.objects.filter(FK_Product=this_product, ProductStatus='3').count()

        # Get All Product Attribute
        this_attribute = AttrProduct.objects.filter(FK_Product = this_product)
        # Get All Product Attribute Price
        this_attribute_price = AttrPrice.objects.filter(FK_Product = this_product)


        context['Shop'] = this_product.FK_Shop.ID
        context['Product'] = this_product
        context['ProductAttribute'] = this_attribute
        context['ProductAttributePrice'] = this_attribute_price
        context['ProductBanner'] = this_banners

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
                            id = shop.ID)

                        else:

                            shop = Shop.objects.create(FK_ShopManager = User.objects.get(id = user[0]), Title = title, Slug = slug, Description = des, Bio = bio, State = state, BigCity = bigcity, City = city, Holidays = week, Available = bool(seen), Publish = bool(state))
                            for item in submarkets:
                                sub = SubMarket.objects.get(Title = item)
                                shop.FK_SubMarket.add(sub)
                            Alert.objects.create(Part = '2', FK_User = request.user, Slug = shop.ID, Seen = True, Status = True, FK_Staff = request.user)
             
                            return redirect('nakhll_market:Show_Shop_Info',
                            id = shop.ID)
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
def Edit_Full_Shop(request, id):

    if request.user.is_authenticated :
        
        fields = ['Shop_Image', 'Shop_Title', 'Shop_Des', 'Shop_State', 'Shop_BigCity',
            'Shop_City', 'Shop_Bio', 'SATCheck', 'SUNCheck', 'MONCheck', 'TUECheck',
            'WEDCheck', 'THUCheck', 'FRICheck']
        context = baseData(request, 'allShop')
        context = getPostData(request, context, fields)
        submarkets = request.POST.getlist("Shop_SubMarket")
        user = request.POST.getlist("Shop_User")
        # Get This Shop
        context['Shop'] = get_object_or_404(Shop, ID = id)

        if request.method == 'POST':

            if (context['Shop_Title'] != ''):
                if (len(submarkets) != 0) and (context['Shop_State'] != '') and (context['Shop_City'] != '') and (context['Shop_BigCity'] != ''):

                    week = ''

                    if context['SATCheck'] != '':
                        week += "0-"
                    if context['SUNCheck'] != '':
                        week += "1-"
                    if context['MONCheck'] != '':
                        week += "2-"
                    if context['TUECheck'] != '':
                        week += "3-"
                    if context['WEDCheck'] != '':
                        week += "4-"
                    if context['THUCheck'] != '':
                        week += "5-"
                    if context['FRICheck'] != '':
                        week += "6-"
                
                    alert = Alert.objects.create(Part = '3', FK_User = request.user, Slug = context['Shop'].ID, Seen = True, Status = True, FK_Staff = request.user)

                    if (len(submarkets) != 0):
                        Sub = '-'
                        for sub in submarkets:
                            Sub += sub + '-'

                        SubMarketField = Field.objects.create(Title = 'SubMarket', Value = Sub)
                        alert.FK_Field.add(SubMarketField)
                        # Set New Data
                        for item in context['Shop'].FK_SubMarket.all():
                            context['Shop'].FK_SubMarket.remove(item)
                        for item in submarkets:
                            context['Shop'].FK_SubMarket.add(SubMarket.objects.get(Title = item))

                
                    if context['Shop_Image'] != '':
                        context['Shop'].Image = context['Shop_Image']
                        context['Shop'].save()
                        img_str = 'NewImage' + '#' + str(context['Shop'].Image)
                        ImageField = Field.objects.create(Title = 'Image', Value = img_str)
                        alert.FK_Field.add(ImageField)

                    if context['Shop_Title'] != context['Shop'].Title:
                        context['Shop'].Title = context['Shop_Title']
                        context['Shop'].save()
                        TitleField = Field.objects.create(Title = 'Title', Value = context['Shop_Title'])
                        alert.FK_Field.add(TitleField)

                    if context['Shop_Des'] != context['Shop'].Description:
                        context['Shop'].Description = context['Shop_Des']
                        context['Shop'].save()
                        DescriptionField = Field.objects.create(Title = 'Description', Value = context['Shop_Des'])
                        alert.FK_Field.add(DescriptionField)

                    if context['Shop_Bio'] != context['Shop'].Bio:
                        context['Shop'].Bio = context['Shop_Bio']
                        context['Shop'].save()
                        BioField = Field.objects.create(Title = 'Bio', Value = context['Shop_Bio'])
                        alert.FK_Field.add(BioField)

                    if context['Shop_State'] != context['Shop'].State:
                        context['Shop'].State = context['Shop_State']
                        context['Shop'].save()
                        StateField = Field.objects.create(Title = 'State', Value = context['Shop_State'])
                        alert.FK_Field.add(StateField)

                    if context['Shop_BigCity'] != context['Shop'].BigCity:
                        context['Shop'].BigCity = context['Shop_BigCity']
                        context['Shop'].save()
                        BigCityField = Field.objects.create(Title = 'BigCity', Value = context['Shop_BigCity'])
                        alert.FK_Field.add(BigCityField)

                    if context['Shop_City'] != context['Shop'].City:
                        context['Shop'].City = context['Shop_City']
                        context['Shop'].save()
                        CityField = Field.objects.create(Title = 'City', Value = context['Shop_City'])
                        alert.FK_Field.add(CityField)

                    if week != context['Shop'].Holidays:
                        context['Shop'].Holidays = week
                        context['Shop'].save()
                        HolidaysField = Field.objects.create(Title = 'Holidays', Value = week)
                        alert.FK_Field.add(HolidaysField)
                    
                    if alert.FK_Field.all().count() == 0:
                        alert.delete()

                    return redirect('nakhll_market:Show_Shop_Info',
                    id = context['Shop'].ID)

                else:
                    context['ShowAlart'] = True
                    context['AlartMessage'] =  'راسته، استان، شهرستان و شهر نمی تواند خالی باشد.'

            else:
                context['ShowAlart'] = True
                context['AlartMessage'] =  'عنوان حجره نمی تواند خالی باشد.'



        else:
            # Get Holiday
            week = context['Shop'].Holidays.split('-')
            # Build Class
            class Items:
                def __init__(self, submarket, status):
                    self.SubMarket = submarket
                    self.Status = status

            ItemsList = []

            for item in SubMarket.objects.filter(Available = True, Publish = True):
                new_item = Items(item, False)
                ItemsList.append(new_item)
            
            for item in context['Shop'].FK_SubMarket.all():
                for list_item in ItemsList:
                    if list_item.SubMarket == item:
                        list_item.Status = True



            context['SubMarkets'] = ItemsList
            context['Week'] = week
    else:
        return redirect("nakhll_market:AccountLogin")

    return render(request, 'nakhll_market/management/content/edit_full_shop.html', context)

# Add New Shop Banner
def Add_New_Shop_Banner(request, id, msg = None):
    '''
    TODO send back data to template if request failed.
    '''

    if request.user.is_authenticated :

        fields = ['Banner_Title', 'Banner_URL', 
                'Banner_Description', 'Banner_Builder', 'Banner_URL_Builder',
                'Banner_Seen', 'Banner_Status']
        context = baseData(request, 'allShop')
        context = getPostData(request, context, fields)
        context['Banner_Image'] = request.FILES.get('Banner_Image')

        # This Shop
        context['ThisShop'] = Shop.objects.get(pk = id)

        if request.method == 'POST':

            if (context['Banner_Title'] != '') and (context['Banner_Image'] != ''):

                # Create New Object
                thisbanner = ShopBanner.objects.create(FK_Shop = context['ThisShop'], 
                                                        Title = context['Banner_Title'], 
                                                        Description = context['Banner_Description'], 
                                                        Image = context['Banner_Image'], 
                                                        Available = bool(context['Banner_Seen']), 
                                                        Publish = bool(context['Banner_Status']))
                # Set New Alert
                Alert.objects.create(Part = '4', 
                                    FK_User = request.user, 
                                    Slug = thisbanner.id, 
                                    Seen = True, 
                                    Status = True, 
                                    FK_Staff = request.user)
                # Save Data
                if (context['Banner_URL'] != ''):
                    thisbanner.URL = context['Banner_URL']
                    thisbanner.save()

                if (context['Banner_Builder'] != ''):
                    thisbanner.BannerBuilder = context['Banner_Builder']
                    thisbanner.save()
                
                if (context['Banner_URL_Builder'] != ''):
                    thisbanner.BannerURL = context['Banner_URL_Builder']
                    thisbanner.save()

                return redirect('nakhll_market:Show_Shop_Info',
                id = context['ThisShop'].ID)

            else:

                context['ShowAlart'] = True
                context['AlartMessage'] = 'عنوان و عکس بنر حجره نمی تواند خالی باشد.'
                return render(request, 'nakhll_market/management/content/add_new_shop_banner.html', context)        
        
        else:
            
            return render(request, 'nakhll_market/management/content/add_new_shop_banner.html', context)

    else:

        return redirect("nakhll_market:AccountLogin")


# Add New Shop`s Product
def Add_New_Shop_Product(request, id):

    if request.user.is_authenticated :

        fields = [
            'prod_title', 'slugProd', 'ProdDes', 'ProdSub', 'ProdBio', 'ProdStory', 'prod_Price',
            'Prodoldprice', 'ProdRange', 'ProdPostType', 'product_netweight', 'product_packingweight',
            'product_lengthwithpackaging', 'product_widthwithpackaging', 'product_heightwithpackaging',
            'Banner_Seen', 'Banner_Status'
        ]
        context = baseData(request, 'allShop')
        context = getPostData(request, context, fields)
        context['ThisShop'] = Shop.objects.get(pk=id)
        Image = request.FILES.get("Product_Image")
        category_list = request.POST.getlist("ProdCat")
        Product_PostRange = request.POST.getlist("PostRange")
        Product_ExePostRange = request.POST.getlist("ExePostRange")
        # Get All Category
        context['Categort'] = Category.objects.filter(Publish = True)
        # Get All Submarket
        context['SubMarket'] = SubMarket.objects.filter(Publish = True)
        # Get All PostRange
        context['PostRange'] = PostRange.objects.all()
        
        if request.method == 'POST':

            if (context['prod_title'] != '') and \
                (len(category_list) != 0) and \
                (context['slugProd'] != '') and \
                (context['ProdSub'] != '') and \
                (Image != '') and \
                (context['prod_Price'] != '') and \
                (context['ProdPostType'] != ''):

                if (context['Prodoldprice'] == '') or \
                    ((context['Prodoldprice'] != context['prod_Price']) and \
                    (int(context['Prodoldprice']) > int(context['prod_Price']))):
                    
                    if Product.objects.filter(Slug = context['slugProd']).exists():

                        context['ShowAlart'] = True
                        context['AlartMessage'] = 'محصولی بااین شناسه ثبت شده است.'
                        return render(request, 'nakhll_market/management/content/add_new_shop_full_product.html', context)

                    else:
                        product = Product.objects.create(Title = context['prod_title'], 
                                                        Slug = context['slugProd'], 
                                                        FK_SubMarket = SubMarket.objects.get(ID = context['ProdSub']), 
                                                        Image = Image, 
                                                        FK_Shop = context['ThisShop'], 
                                                        Price = context['prod_Price'], 
                                                        Status = context['ProdPostType'], 
                                                        Available = bool(context['Banner_Seen']), 
                                                        Publish = bool(context['Banner_Status']))

                        for item in category_list:
                            product.FK_Category.add(Category.objects.get(id = item))

                        if len(Product_PostRange) != 0:
                            for item in Product_PostRange:
                                product.FK_PostRange.add(PostRange.objects.get(id = item))
                        
                        if len(Product_ExePostRange) != 0:
                            for item in Product_ExePostRange:
                                product.FK_ExceptionPostRange.add(PostRange.objects.get(id = item))

                        if context['ProdDes'] != '':
                            product.Description = context['ProdDes']

                        if context['ProdBio'] != '':
                            product.Bio = context['ProdBio']

                        if context['ProdStory'] != '':
                            product.Story = context['ProdStory']

                        if context['Prodoldprice'] != '':
                            product.OldPrice = context['Prodoldprice']
                        else:
                            product.OldPrice = '0'

                        product.PostRangeType = context['ProdRange']

                        # Product Weight Info
                        product.Net_Weight = context['product_netweight']
                        product.Weight_With_Packing = context['product_packingweight']
                        # Product Dimensions Info
                        product.Length_With_Packaging = context['product_lengthwithpackaging']
                        product.Width_With_Packaging = context['product_widthwithpackaging']
                        product.Height_With_Packaging = context['product_heightwithpackaging']

                        product.save()
                                                    
                        Alert.objects.create(Part = '6', FK_User = request.user, Slug = product.ID, Seen = True, Status = True, FK_Staff = request.user)

                        return redirect('nakhll_market:Show_Product_Info',
                        Product_Slug = product.Slug)

                else:
                    
                    if context['prod_Price'] == context['Prodoldprice']:

                        context['ShowAlart'] = True
                        context['AlartMessage'] = 'قیمت فروش محصول و قیمت واقعی نمی تواند با هم برابر باشد.'
                        return render(request, 'nakhll_market/management/content/add_new_shop_full_product.html', context)

                    elif int(context['prod_Price']) > int(context['Prodoldprice']):

                        context['ShowAlart'] = True
                        context['AlartMessage'] = 'قیمت واقعی نمیتواند از قیمت فروش محصول کمتر باشد.'
                        return render(request, 'nakhll_market/management/content/add_new_shop_full_product.html', context)

            else:

                context['ShowAlart'] = True
                context['AlartMessage'] = 'عنوان - دسته بندی - حجره - شناسه - عکس - قیمت و نوع ارسال محصول اجباریست.'
                return render(request, 'nakhll_market/management/content/add_new_shop_full_product.html', context)

        else:
            return render(request, 'nakhll_market/management/content/add_new_shop_full_product.html', context)

    else:

        return redirect("nakhll_market:AccountLogin")



# Edit Full Product
def Edit_Full_Product(request, id):

    if request.user.is_authenticated :

        fields = [
            'prod_title', 'ProdDes', 'ProdSub', 'ProdBio', 'ProdStory', 
            'prod_Price','Prodoldprice', 'ProdRange', 'ProdPostType', 
            'product_netweight', 'product_packingweight', 'product_lengthwithpackaging',
            'product_widthwithpackaging', 'product_heightwithpackaging'
            ]
        context = baseData(request, 'allShop')
        context = getPostData(request, context, fields)
        # This Product
        context['Product'] = Product.objects.get(ID = id)
        Image = request.FILES.get("Product_Image")
        category_list = request.POST.getlist("ProdCat")
        Product_PostRange = request.POST.getlist("PostRange")
        Product_ExePostRange = request.POST.getlist("ExePostRange")

        if request.method == 'POST':

            if (context['prod_title'] != '') and \
                (len(category_list) != 0) and \
                (context['ProdSub'] != '') and \
                (context['prod_Price'] != '') and \
                (context['ProdPostType'] != ''):

                if (context['Prodoldprice'] == '') or ((context['Prodoldprice'] != context['prod_Price']) and \
                    (int(context['Prodoldprice']) > int(context['prod_Price']))):

                    alert = Alert.objects.create(
                                                Part = '7', 
                                                FK_User = request.user, 
                                                Slug = context['Product'].ID, 
                                                Seen = True, 
                                                Status = True, 
                                                FK_Staff = request.user
                                                )

                    if context['prod_title'] != context['Product'].Title:
                        context['Product'].Title = context['prod_title']
                        context['Product'].save()
                        TitleField = Field.objects.create(Title = 'Title', Value = context['prod_title'])
                        alert.FK_Field.add(TitleField)

                    if SubMarket.objects.get(ID = context['ProdSub']) != context['Product'].FK_SubMarket:
                        context['Product'].FK_SubMarket = SubMarket.objects.get(ID = context['ProdSub'])
                        context['Product'].save()
                        SubMarketField = Field.objects.create(Title = 'SubMarket', Value = SubMarket.objects.get(ID = context['ProdSub']).Title)
                        alert.FK_Field.add(SubMarketField)
                        
                    if Image != '':
                        context['Product'].Image = Image
                        context['Product'].save()
                        img_str = 'NewImage' + '#' + str(context['Product'].Image)
                        ImageField = Field.objects.create(Title = 'Image', Value = img_str)
                        alert.FK_Field.add(ImageField)

                    if context['prod_Price'] != str(context['Product'].Price):
                        context['Product'].Price = context['prod_Price']
                        context['Product'].save()
                        PriceField = Field.objects.create(Title = 'Price', Value = context['prod_Price'])
                        alert.FK_Field.add(PriceField)

                        if context['Product'].Status != context['ProdPostType']:
                            context['Product'].Status = context['ProdPostType']
                            context['Product'].save()
                            StatusField = Field.objects.create(Title = 'ProdPostType', Value = context['ProdPostType'])
                            alert.FK_Field.add(StatusField)            

                    if context['ProdDes'] != context['Product'].Description:
                        context['Product'].Description = context['ProdDes']
                        context['Product'].save()
                        DescriptionField = Field.objects.create(Title = 'Description', Value = context['ProdDes'])
                        alert.FK_Field.add(DescriptionField)

                    if context['ProdBio'] != context['Product'].Bio:
                        context['Product'].Bio = context['ProdBio']
                        context['Product'].save()
                        BioField = Field.objects.create(Title = 'Bio', Value = context['ProdBio'])
                        alert.FK_Field.add(BioField)

                    if context['ProdStory'] != context['Product'].Story:
                        context['Product'].Story = context['ProdStory']
                        context['Product'].save()
                        StoryField = Field.objects.create(Title = 'Story', Value = context['ProdStory'])
                        alert.FK_Field.add(StoryField)

                    if len(category_list) != 0:
                        Categori = '-'
                        for item in category_list:
                            Categori += item + '-'
                            
                        CategoryField = Field.objects.create(Title = 'Category', Value = Categori)
                        alert.FK_Field.add(CategoryField)

                        for item in context['Product'].FK_Category.all():
                            context['Product'].FK_Category.remove(item)

                        for item in category_list:
                            context['Product'].FK_Category.add(Category.objects.get(id = item))

                    if len(Product_PostRange) != 0:
                        Product_PR = '-'
                        for item in Product_PostRange:
                            Product_PR += item + '-'

                        PostRangeField = Field.objects.create(Title = 'PostRange', Value = Product_PR)
                        alert.FK_Field.add(PostRangeField)

                        for item in context['Product'].FK_PostRange.all():
                            context['Product'].FK_PostRange.remove(item)

                        for item in Product_PostRange:
                            context['Product'].FK_PostRange.add(PostRange.objects.get(id = item))
                        
                    if len(Product_ExePostRange) != 0:

                        Product_EPR = '-'
                        for item in Product_ExePostRange:
                            Product_EPR += item + '-'

                        ExePostRangeField = Field.objects.create(Title = 'ExePostRange', Value = Product_EPR)
                        alert.FK_Field.add(ExePostRangeField)

                        for item in context['Product'].FK_ExceptionPostRange.all():
                            context['Product'].FK_ExceptionPostRange.remove(item)

                        for item in Product_ExePostRange:
                            context['Product'].FK_ExceptionPostRange.add(PostRange.objects.get(id = item))

                    if context['Prodoldprice'] != '':
                        if context['Prodoldprice'] != context['Product'].OldPrice:
                            context['Product'].OldPrice = context['Prodoldprice']
                            context['Product'].save()
                            OldPriceField = Field.objects.create(Title = 'OldPrice', Value = context['Prodoldprice'])
                            alert.FK_Field.add(OldPriceField)
                    else:
                        if context['Prodoldprice'] != context['Product'].OldPrice:
                            context['Product'].OldPrice = '0'
                            context['Product'].save()

                    if context['ProdRange'] != '':

                        if context['Product'].PostRangeType != context['ProdRange']:
                            context['Product'].PostRangeType = context['ProdRange']
                            context['Product'].save()
                            ProdRangeField = Field.objects.create(Title = 'ProdRange', Value = context['ProdRange'])
                            alert.FK_Field.add(ProdRangeField)


                    # Product Weight Info
                    if context['Product'].Net_Weight != context['product_netweight']:
                        context['Product'].Net_Weight = context['product_netweight']
                        context['Product'].save()

                    if context['Product'].Weight_With_Packing != context['product_packingweight']:
                        context['Product'].Weight_With_Packing = context['product_packingweight']
                        context['Product'].save()
                    # Product Dimensions Info
                    if context['Product'].Length_With_Packaging != context['product_lengthwithpackaging']:
                        context['Product'].Length_With_Packaging = context['product_lengthwithpackaging']
                        context['Product'].save()

                    if context['Product'].Width_With_Packaging != context['product_widthwithpackaging']:
                        context['Product'].Width_With_Packaging = context['product_widthwithpackaging']
                        context['Product'].save()

                    if context['Product'].Height_With_Packaging != context['product_heightwithpackaging']:
                        context['Product'].Height_With_Packaging = context['product_heightwithpackaging']
                        context['Product'].save()
                        
                    return redirect('nakhll_market:Show_Product_Info',
                    Product_Slug = context['Product'].Slug)

                else:
                    context['ShowAlart'] = True
                    if context['prod_Price'] == context['Prodoldprice']:
                        context['AlartMessage'] =  'قیمت فروش محصول و قیمت واقعی نمی تواند با هم برابر باشد.'

                    elif int(context['prod_Price']) > int(context['Prodoldprice']):
                        context['AlartMessage'] =  'قیمت واقعی نمیتواند از قیمت فروش محصول کمتر باشد.'

            else:
                context['ShowAlart'] = True
                context['AlartMessage'] =  'عنوان - دسته بندی - حجره - شناسه - عکس - قیمت و نوع ارسال محصول اجباریست.'

        else:
            
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
                
            
            for item in context['Product'].FK_Category.all():
                for i in ItemsList:
                    if i.Category == item:
                        i.Status = True

            PostRangeList = []

            for item in PostRange.objects.all():
                newitem = PostRangeClass(item, False)
                PostRangeList.append(newitem)
                
            
            for item in context['Product'].FK_PostRange.all():
                for i in PostRangeList:
                    if i.PostRange == item:
                        i.Status = True

            ExePostRangeList = []

            for item in PostRange.objects.all():
                newitem = ExePostRange(item, False)
                ExePostRangeList.append(newitem)
                
            
            for item in context['Product'].FK_ExceptionPostRange.all():
                for i in ExePostRangeList:
                    if i.ExePostRange == item:
                        i.Status = True

            context['Categort'] = ItemsList
            context['SubMarket'] = submarkets
            context['ProdRange'] = PostRangeList
            context['ProExePostRange'] = ExePostRangeList
    else:

        return redirect("nakhll_market:AccountLogin")

    return render(request, 'nakhll_market/management/content/edit_full_product.html', context)

# Add New Product Banner
def Add_New_Product_Banner(request, id):

    if request.user.is_authenticated :
        
        context = baseData(request, 'allShop')
        # This Product
        this_product = Product.objects.get(ID = id)
        context['Product'] = this_product


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

                # Create New Object
                thisbanner = ProductBanner.objects.create(FK_Product = this_product, Title = Banner_Title, Image = Banner_Image, Available = bool(Banner_Seen), Publish = bool(Banner_Status))
                # Set New Alert
                Alert.objects.create(Part = '8', FK_User = request.user, Slug = thisbanner.id, Seen = True, Status = True, FK_Staff = request.user)

                return redirect('nakhll_market:Show_Product_Info',
                Product_Slug = this_product.Slug)

            else:
                context['ShowAlart'] = True
                context['AlartMessage'] =  'عنوان و عکس بنر حجره نمی تواند خالی باشد.'

        else:
            pass

    else:
        return redirect("nakhll_market:AccountLogin")
         
    return render(request, 'nakhll_market/management/content/add_new_product_banner.html', context)

        
# Add New Product Attribut
def Add_New_Product_Attribute(request, id):

    if request.user.is_authenticated :

        context = baseData(request, 'allShop')
        this_product = Product.objects.get(ID = id)
        context['Product'] = this_product
        # Get All Attribute
        context['Attributes'] = Attribute.objects.filter(Publish = True)

        if request.method == 'POST':

            try:
                AttrTitle = request.POST["Attribute_Title"]
            except:
                AttrTitle = ''

            try:
                AttrValue = request.POST["Attribute_Value"]
            except:
                AttrValue = ''


            if (AttrTitle != '') and (AttrValue != ''):

                attrtilte = AttrTitle.split('|')
                attrproduct = AttrProduct.objects.create(FK_Product = this_product, FK_Attribute = Attribute.objects.get(Title = attrtilte[0], Unit = attrtilte[1]), Value = AttrValue)

                Alert.objects.create(Part = '11', FK_User = request.user, Slug = attrproduct.id, Seen = True, Status = True, FK_Staff = request.user)

                return redirect('nakhll_market:Add_New_Product_Attribute',
                id = this_product.ID)

            else:
                context['ShowAlart'] = True
                context['AlartMessage'] =  'مقادیر عنوان و واحد نمی تواند خالی باشد.'

        else:
            pass

    else:
        return redirect("nakhll_market:AccountLogin")

    return render(request, 'nakhll_market/management/content/add_new_product_attribute.html', context)

# Add New Product AttrPrice
def Add_New_Product_AttrPrice(request, id):

    if request.user.is_authenticated :
        context = baseData(request)
        # This Product
        this_product = Product.objects.get(ID = id)
        context['Product'] = this_product

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
                    context['ShowAlart'] = True
                    context['AlartMessage'] =  'این ارزش ویژگی تکراری می باشد.'

                else:

                    attrprice = AttrPrice.objects.create(FK_Product = this_product, Value = AttrPrice_Value, ExtraPrice = AttrPrice_Exp, Unit = AttrPrice_Unit, Publish = False)

                    if AttrPrice_Des != '':
                        attrprice.Description = AttrPrice_Des
                        attrprice.save()

                    Alert.objects.create(Part = '17', FK_User = request.user, Slug = attrprice.id, Seen = True, Status = True, FK_Staff = request.user)

            else:
                context['ShowAlart'] = True
                context['AlartMessage'] =  'مقادیر ستاره دار نمی تواند خالی باشد.'

        else:
            pass
        
    else:
        return redirect("nakhll_market:AccountLogin")

    return render(request, 'nakhll_market/management/content/add_new_product_attrprice.html', context)