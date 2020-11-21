from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from kavenegar import *
import threading
from datetime import datetime, date
import jdatetime
import threading



from django.contrib.auth.models import User
from .models import Alert, Product, Profile, Shop, Category, Option_Meta, Market, SubMarket, Message, User_Message_Status, Alert
from Payment.models import Coupon, Wallet, Factor

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

# ---------------------------------------------------------------------------------------------------------------------------------------



# Send SMS
class SendSMS(threading.Thread):

    def __init__(self, users, coupon_id):
        self.coupon = Coupon.objects.get(id = coupon_id)
        self.All_User = users

    def message(self):
        title = 'کوپن تخفیف ' + self.coupon.Title
        txt = 'کوپن تخفیف ' + self.coupon.Title + ' با سریال ' + self.coupon.SerialNumber + ' تا تاریخ ' + str(self.coupon.EndDate) + ' قابل استفاده می باشد. ' + '\n توضیحات بیشتر : \n' + self.coupon.Description
        # Save New Message
        new_message = Message.objects.create(Title = title, Text = txt, FK_Sender = self.coupon.FK_Creator)
        for item in self.All_User:
            this_user = get_object_or_404(User, id = item)
            new_obj = User_Message_Status.objects.create(FK_User = this_user)
            new_message.FK_Users.add(new_obj)

    def run(self):
        # Send Message
        self.message()
        # Get User Phone Number
        # PhoneNumber = Profile.objects.get(FK_User = self.user).MobileNumber
        # # Send SMS
        # url = 'https://api.kavenegar.com/v1/4E41676D4B514A4143744C354E6135314E4F47686B33594B747938794D30426A784A692F3579596F3767773D/verify/lookup.json' 
        # params = {'receptor': PhoneNumber, 'token' : self.user.username, 'token2' : self.coupon.SerialNumber, 'template' : 'addnewcoupom-nakhll'}
        # requests.post(url, params = params)



# ---------------------------------------------------------------------------------------------------------------------------------------



# Save Edite Management Coupon
def SaveEditManagementCoupon(request, id):
    # Check User Status
    if request.user.is_authenticated :
        if request.method == 'POST':
            Filter_Shops = request.POST.getlist("copun_shops")

            Filter_Products = request.POST.getlist("copun_products")

            Filter_Users = request.POST.getlist("copun_users")
            
            Filter_Categories = request.POST.getlist("copun_categories")
            # ---------------------------------------------------------------------
            # Get Coupon
            copun = Coupon.objects.get(id = id)
            # Set Log
            shop_log = ''
            product_log = ''
            user_log = ''
            category_log = ''

            # Remove Shop Coupon Filters
            for item in copun.FK_Shops.all():
                copun.FK_Shops.remove(item)    
            # Add Shop Coupon Filters
            if len(Filter_Shops) != 0:
                for item in Filter_Shops:
                    New_Shop = Shop.objects.get(ID = item)
                    shop_log += New_Shop.Slug + '#'
                    copun.FK_Shops.add(New_Shop)
                    copun.save()

            # Remove Products Coupon Filters
            for item in copun.FK_Products.all():
                copun.FK_Products.remove(item)   
            # Add Products Coupon Filters
            if len(Filter_Products) != 0:
                for item in Filter_Products:
                    New_Product = Product.objects.get(ID = item)
                    product_log += New_Product.Slug + '#'
                    copun.FK_Products.add(New_Product)
                    copun.save()

            # Remove Users Coupon Filters
            for item in copun.FK_Users.all():
                copun.FK_Users.remove(item)  
            # Add Users Coupon Filters
            if len(Filter_Users) != 0:
                for item in Filter_Users:
                    New_User = User.objects.get(id = item)
                    user_log += New_User.username + '#'
                    copun.FK_Users.add(New_User)
                    copun.save()

            # Remove Categories Coupon Filters
            for item in copun.FK_Categories.all():
                copun.FK_Categories.remove(item)  
            # Add Categories Coupon Filters
            if len(Filter_Categories) != 0:
                for item in Filter_Categories:
                    New_Category = Category.objects.get(id = item)
                    category_log += New_Category.Slug + '#'
                    copun.FK_Categories.add(New_Category)
                    copun.save()

            # Save Log
            if (copun.Log == '') or (copun.Log == None):
                copun.Log = shop_log + '\n' + product_log + '\n' + user_log + '\n' + category_log + '\n' +  '(' + copun.FK_Creator.username + '/' + str(jdatetime.date.today()) + ')' + '\n'
                copun.save()
            else:
                copun.Log = '------------------>' + '\n' + shop_log + '\n' + product_log + '\n' + user_log + '\n' + category_log + '\n' +  '(' + copun.FK_Creator.username + '/' + str(jdatetime.date.today()) + ')' + '\n'
                copun.save()

            return redirect("nakhll_market:ManagementCoupunList")
        else:
            return redirect("nakhll_market:EditManagementCoupon", id = copun.id)
    else:
        return redirect("nakhll_market:AccountLogin")


# Edite Management Coupon
def EditManagementCoupon(request, id):
    # Check User Status
    if request.user.is_authenticated:
        if request.method == 'POST':
            Filter_Shops = request.POST.getlist("Shop_Select")

            Filter_Markets = request.POST.getlist("Market_Select")

            Filter_SubMarkets = request.POST.getlist("SubMarket_Select")

            Filter_Categories = request.POST.getlist("Category_Select")

            if (len(Filter_Shops) != 0) or (len(Filter_Markets) != 0) or (len(Filter_SubMarkets) != 0) or (len(Filter_Categories) != 0):
                # Get All Shops With Markets And SubMarkets Filter
                Sub_MarketList = []
                if len(Filter_Markets) != 0:
                    for item in Filter_Markets:
                        Sub_MarketList += list(SubMarket.objects.filter(Publish = True, FK_Market = item))

                if len(Filter_SubMarkets) != 0:
                    for item in Filter_SubMarkets:
                        Sub_MarketList.append(SubMarket.objects.get(ID = item))

                Sub_MarketList = list(dict.fromkeys(Sub_MarketList))

                # Get Shop Filter
                pubshops = []

                for item in Sub_MarketList:
                    pubshops += list(Shop.objects.filter(Publish = True, FK_SubMarket__in = Sub_MarketList))

                pubshops = list(dict.fromkeys(pubshops))

                # Get All Products With Shops And Categories Filter
                pubproducts = []

                if len(Filter_Shops) != 0:
                    for item in Filter_Shops:
                        pubproducts+= list(Product.objects.filter(Publish = True, FK_Shop = item))

                if len(Filter_Categories) != 0:
                    for item in Filter_Categories:
                        this_category = Category.objects.get(id = item)
                        pubproducts+= list(Product.objects.filter(Publish = True, FK_Category = this_category))

                pubproducts = list(dict.fromkeys(pubproducts))

                # ------------------ No Filter --------------------------------
                if (len(Filter_Shops) == 0) and (len(Filter_Categories) == 0):
                    # Get All Product
                    pubproducts = Product.objects.filter(Publish = True)

                if (len(Filter_Markets) == 0) and (len(Filter_SubMarkets) == 0):
                    # Get All Shop
                    pubshops = Shop.objects.filter(Publish = True)
                # --------------------------------------------------------------
                # Get All Detiles Copuns
                class Itemclass:
                    def __init__(self, item, status):
                        self.Item = item
                        self.Status = status

                MarketList = []
                for item in Market.objects.filter(Publish = True):
                    if str(item.ID) in Filter_Markets:
                        print(item.Slug)
                        MarketList.append(Itemclass(item, True))
                    else:
                        MarketList.append(Itemclass(item, False))

                SubMarketList = []
                for item in SubMarket.objects.filter(Publish = True):
                    if str(item.ID) in Filter_SubMarkets:
                        SubMarketList.append(Itemclass(item, True))
                    else:
                        SubMarketList.append(Itemclass(item, False))

                ShopList = []
                for item in Shop.objects.filter(Publish = True, Available = True):
                    if str(item.ID) in Filter_Shops:
                        ShopList.append(Itemclass(item, True))
                    else:
                        ShopList.append(Itemclass(item, False))

                CategoryList = []
                for item in Category.objects.filter(Publish = True):
                    if str(item.id) in Filter_Categories:
                        CategoryList.append(Itemclass(item, True))
                    else:
                        CategoryList.append(Itemclass(item, False))
                # -----------------------------------------------------------------------
                # Get Coupon
                coupon = get_object_or_404(Coupon, id = id)
                # get all detiles coupons
                User_List = []
                if coupon.FK_Users.all().count() != 0:
                    for item in User.objects.filter(is_active = True):
                        if item in coupon.FK_Users.all():
                            User_List.append(Itemclass(item, True))
                        else:
                            User_List.append(Itemclass(item, False))
                else:
                    for item in User.objects.filter(is_active = True):
                        User_List.append(Itemclass(item, False))

                Shop_List = []
                if coupon.FK_Shops.count() != 0:
                    for item in Shop.objects.filter(Publish = True, Available = True):
                        if item in coupon.FK_Shops.all():
                            Shop_List.append(Itemclass(item, True))
                        else:
                            Shop_List.append(Itemclass(item, False))
                else:
                    for item in Shop.objects.filter(Publish = True, Available = True):
                        Shop_List.append(Itemclass(item, False))

                Category_List = []
                if coupon.FK_Categories.count() != 0:
                    for item in Category.objects.filter(Publish = True):
                        if item in coupon.FK_Categories.all():
                            Category_List.append(Itemclass(item, True))
                        else:
                            Category_List.append(Itemclass(item, False))
                else:
                    for item in Category.objects.filter(Publish = True):
                        Category_List.append(Itemclass(item, False))
                        
                Product_List = []
                if coupon.FK_Products.count() != 0:
                    for item in Product.objects.filter(Publish = True, Available = True):
                        if item in coupon.FK_Products.all():
                            Product_List.append(Itemclass(item, True))
                        else:
                            Product_List.append(Itemclass(item, False))
                else:
                    for item in Product.objects.filter(Publish = True, Available = True):
                        Product_List.append(Itemclass(item, False))
                # -----------------------------------------------------------------------
                # Get User Info
                This_User_Info = GetUserInfo().run(request)
                this_profile = This_User_Info["user_profiel"]
                this_inverntory = This_User_Info["user_inverntory"]
                # Get Menu Item
                options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
                # Get Nav Bar Menu Item
                navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
                # ----------------------------------------------------------------------
           
                context = {
                    'This_User_Profile':this_profile,
                    'This_User_Inverntory': this_inverntory,
                    'Options': options,
                    'MenuList':navbar,
                    'AllUsers':User_List,
                    'AllProducts':Product_List,
                    'AllShops':Shop_List,
                    'AllCategories':Category_List,
                    'Categories':CategoryList,
                    'Shops':ShopList,
                    'SubMarkets':SubMarketList,
                    'Markets':MarketList,
                    'UserCoupon':coupon.id,
                }

                return render(request, 'nakhll_market/management/coupon/editmanagementcoupon.html', context)

            elif (len(Filter_Shops) == 0) or (len(Filter_Markets) == 0) or (len(Filter_SubMarkets) == 0) or (len(Filter_Categories) == 0):
                return redirect("nakhll_market:ManagementCoupunList")
        else:
            # Get User Info
            This_User_Info = GetUserInfo().run(request)
            this_profile = This_User_Info["user_profiel"]
            this_inverntory = This_User_Info["user_inverntory"]
            # Get Menu Item
            options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
            # Get Nav Bar Menu Item
            navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
            # ----------------------------------------------------------------------
            # get this coupon
            coupon = get_object_or_404(Coupon, id = id)
            # get all detiles coupons
            class Itemclass:
                def __init__(self, item, status):
                    self.Item = item
                    self.Status = status

            User_List = []
            if coupon.FK_Users.count() != 0:
                for item in User.objects.filter(is_active = True):
                    if item in coupon.FK_Users.all():
                        User_List.append(Itemclass(item, True))
                    else:
                        User_List.append(Itemclass(item, False))
            else:
                for item in User.objects.filter(is_active = True):
                    User_List.append(Itemclass(item, False))

            Shop_List = []
            if coupon.FK_Shops.count() != 0:
                for item in Shop.objects.filter(Publish = True, Available = True):
                    if item in coupon.FK_Shops.all():
                        Shop_List.append(Itemclass(item, True))
                    else:
                        Shop_List.append(Itemclass(item, False))
            else:
                for item in Shop.objects.filter(Publish = True, Available = True):
                    Shop_List.append(Itemclass(item, False))

            Category_List = []
            if coupon.FK_Categories.count() != 0:
                for item in Category.objects.filter(Publish = True):
                    if item in coupon.FK_Categories.all():
                        Category_List.append(Itemclass(item, True))
                    else:
                        Category_List.append(Itemclass(item, False))
            else:
                for item in Category.objects.filter(Publish = True):
                    Category_List.append(Itemclass(item, False))

            Product_List = []
            if coupon.FK_Products.count() != 0:
                for item in Product.objects.filter(Publish = True, Available = True):
                    if item in coupon.FK_Products.all():
                        Product_List.append(Itemclass(item, True))
                    else:
                        Product_List.append(Itemclass(item, False))
            else:
                for item in Product.objects.filter(Publish = True, Available = True):
                    Product_List.append(Itemclass(item, False))
            # -------------------------------------------------------------------------------
            # show market list
            MarketList = []
            for item in Market.objects.filter(Publish = True):
                MarketList.append(Itemclass(item, False))
            # show submarket lits
            SubMarketList = []
            for item in SubMarket.objects.filter(Publish = True):
                SubMarketList.append(Itemclass(item, False))
            # show shop lits
            ShopList = []
            for item in Shop.objects.filter(Publish = True, Available = True):
                ShopList.append(Itemclass(item, False))
            # show category lits
            CategoryList = []
            for item in Category.objects.filter(Publish = True):
                CategoryList.append(Itemclass(item, False))

            context = {
                'This_User_Profile':this_profile,
                'This_User_Inverntory': this_inverntory,
                'Options': options,
                'MenuList':navbar,
                'AllUsers':User_List,
                'AllProducts':Product_List,
                'AllShops':Shop_List,
                'AllCategories':Category_List,
                'Categories':CategoryList,
                'Shops':ShopList,
                'SubMarkets':SubMarketList,
                'Markets':MarketList,
                'UserCoupon':coupon.id,
            }

            return render(request, 'nakhll_market/management/coupon/editmanagementcoupon.html', context)
    else:
        return redirect("nakhll_market:AccountLogin")



# Delete Management Coupon
def DeleteManagementCoupon(request, id):

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
        # -----------------------------------------------------------------------
        # Get Coupon
        try:
            coupon = Coupon.objects.get(id = id, Publish = True, Available = True)
        except Coupon.DoesNotExist:
            return redirect("nakhll_market:ManagementCoupunList")
        # coupon = get_object_or_404(Coupon, id = id, Publish = True, Available = True)
        # Change Coupon Status
        coupon.Publish = False
        coupon.Available = False
        coupon.save()
        # Get All User Copuns
        allusercopun = Coupon.objects.filter(DiscountStatus = '0', Publish = True)

        context = {
            'Users':user,
            'Profile':profile,
            'Wallet': wallets,
            'Options': options,
            'MenuList':navbar,
            'AllUserCupons':allusercopun,
            'ShowAlert':True,
            'AlartMessage':'کوپن مدنظر شما حذف شد!',
        }

        return render(request, 'nakhll_market/management/coupon/managecuponlist.html', context)

    else:
        return redirect("nakhll_market:AccountLogin")



# Filter Management Coupon
def FilterManagementCoupon(request, id):
    # Check User Status
    if request.user.is_authenticated :

        if request.method == 'POST':

            Filter_Shops = request.POST.getlist("Shop_Select")

            Filter_Markets = request.POST.getlist("Market_Select")

            Filter_SubMarkets = request.POST.getlist("SubMarket_Select")

            Filter_Categories = request.POST.getlist("Category_Select")
                
            # ---------------------------------------------------------------------
            # Get All Shops With Markets And SubMarkets Filter
            Sub_MarketList = []

            if len(Filter_Markets) != 0:
                for i in Filter_Markets:
                    for j in SubMarket.objects.filter(Publish = True):
                        if j.FK_Market == Market.objects.get(ID = i):
                            Sub_MarketList.append(j)

            if len(Filter_SubMarkets) != 0:
                for i in Filter_SubMarkets:
                    Sub_MarketList.append(SubMarket.objects.get(ID = i))

            Sub_MarketList = list(dict.fromkeys(Sub_MarketList))

            # Get Shop Filter
            pubshops = []

            for i in Sub_MarketList:
                for j in Shop.objects.filter(Publish = True):
                    for k in j.FK_SubMarket.all():
                        if k == i:
                            pubshops.append(j)

            pubshops = list(dict.fromkeys(pubshops))

            # Get All Products With Shops And Categories Filter
            pubproducts = []

            if len(Filter_Shops) != 0:
                for i in Filter_Shops:
                    for j in Product.objects.filter(Publish = True):
                        if j.FK_Shop == Shop.objects.get(ID = i):
                            pubproducts.append(j)

            if len(Filter_Categories) != 0:
                for i in Filter_Categories:
                    for j in Product.objects.filter(Publish = True):
                        for k in j.FK_Category.all():
                            if k == Category.objects.get(id = i):
                                pubproducts.append(j)

            pubproducts = list(dict.fromkeys(pubproducts))

            # ------------------ No Filter --------------------------------
            if (len(Filter_Shops) == 0) and (len(Filter_Categories) == 0):
                # Get All Product
                pubproducts = Product.objects.filter(Publish = True)

            if (len(Filter_Markets) == 0) and (len(Filter_SubMarkets) == 0):
                # Get All Shop
                pubshops = Shop.objects.filter(Publish = True)
            # --------------------------------------------------------------
            # Build Market Class
            class MarketClass:
                def __init__(self, item, status):
                    self.Market = item
                    self.Status = status

            MarketList = []

            for market_item in Market.objects.filter(Publish = True):
                New_Item = MarketClass(market_item, False)
                MarketList.append(New_Item)

            for market_item in Filter_Markets:
                for i in MarketList:
                    if i.Market == Market.objects.get(ID = market_item):
                        i.Status = True

            # Build SubMarket Class
            class SubMarketClass:
                def __init__(self, item, status):
                    self.SubMarket = item
                    self.Status = status

            SubMarketList = []

            for submarket_item in SubMarket.objects.filter(Publish = True):
                New_Item = SubMarketClass(submarket_item, False)
                SubMarketList.append(New_Item)

            for submarket_item in Filter_SubMarkets:
                for i in SubMarketList:
                    if i.SubMarket == SubMarket.objects.get(ID = submarket_item):
                        i.Status = True

            # Build Shop Class
            class ShopClass:
                def __init__(self, item, status):
                    self.Shop = item
                    self.Status = status

            ShopList = []

            for shop_item in Shop.objects.filter(Publish = True):
                New_Item = ShopClass(shop_item, False)
                ShopList.append(New_Item)

            for shop_item in Filter_Shops:
                for i in ShopList:
                    if i.Shop == Shop.objects.get(ID = shop_item):
                        i.Status = True

            # Build Category Class
            class CategoryClass:
                def __init__(self, item, status):
                    self.Category = item
                    self.Status = status

            CategoryList = []

            for category_item in Category.objects.filter(Publish = True):
                New_Item = CategoryClass(category_item, False)
                CategoryList.append(New_Item)

            for item in CategoryList:
                for i in Filter_Categories:
                    if item.Category.id == i:
                        item.Status = True

            # Get All Users
            pubusers = User.objects.filter(is_active = True)
            # Get All Catrgory
            pubcategories = Category.objects.filter(Publish = True)
            #-----------------------------------------------------------------------
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
                'AllUsers':pubusers,
                'AllProducts':pubproducts,
                'AllShops':pubshops,
                'AllCategories':pubcategories,
                'Categories':CategoryList,
                'Shops':ShopList,
                'SubMarkets':SubMarketList,
                'Markets':MarketList,
                'UserCoupon':id,
            }

            return render(request, 'nakhll_market/management/coupon/manageaddshopincoupon.html', context)

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
            # Build Market Class
            class MarketClass:
                def __init__(self, item, status):
                    self.Market = item
                    self.Status = status

            MarketList = []

            for market_item in Market.objects.filter(Publish = True):
                New_Item = MarketClass(market_item, False)
                MarketList.append(New_Item)


            # Build SubMarket Class
            class SubMarketClass:
                def __init__(self, item, status):
                    self.SubMarket = item
                    self.Status = status

            SubMarketList = []

            for submarket_item in SubMarket.objects.filter(Publish = True):
                New_Item = SubMarketClass(submarket_item, False)
                SubMarketList.append(New_Item)


            # Build Shop Class
            class ShopClass:
                def __init__(self, item, status):
                    self.Shop = item
                    self.Status = status

            ShopList = []

            for shop_item in Shop.objects.filter(Publish = True):
                New_Item = ShopClass(shop_item, False)
                ShopList.append(New_Item)

            # Build Category Class
            class CategoryClass:
                def __init__(self, item, status):
                    self.Category = item
                    self.Status = status

            CategoryList = []

            for category_item in Category.objects.filter(Publish = True):
                New_Item = CategoryClass(category_item, False)
                CategoryList.append(New_Item)

            # Get All Shops
            pubshops = Shop.objects.filter(Publish = True)
            # Get All Product
            pubproducts = Product.objects.filter(Publish = True)
            # Get All Users
            pubusers = User.objects.filter(is_active = True)
            # Get All Catrgory
            pubcategories = Category.objects.filter(Publish = True)

            context = {
                'Users':user,
                'Profile':profile,
                'Wallet': wallets,
                'Options': options,
                'MenuList':navbar,
                'AllUsers':pubusers,
                'AllProducts':pubproducts,
                'AllShops':pubshops,
                'AllCategories':pubcategories,
                'Categories':CategoryList,
                'Shops':ShopList,
                'SubMarkets':SubMarketList,
                'Markets':MarketList,
                'UserCoupon':id,
                'ShowAlart':True,
                'AlartMessage':'کوپن شما ثبت شد، لطفا محدودیت های آن را وارد نمایید.',
            }

            return render(request, 'nakhll_market/management/coupon/manageaddshopincoupon.html', context)
    else:
        return redirect("nakhll_market:AccountLogin")


# add object in coupon
def thread_add_object_to_coupon(this_coupon, shops, products, users, categories):
    # set log
    shop_log = ''
    product_log = ''
    user_log = ''
    category_log = ''
    # check shops
    if len(shops) != 0:
        for item in shops:
            if Shop.objects.filter(ID = item).exists():
                this_shop = Shop.objects.get(ID = item)
                shop_log += this_shop.Slug + '#'
                this_coupon.FK_Shops.add(this_shop)
    # check products
    if len(products) != 0:
        for item in products:
            if Product.objects.filter(ID = item).exists():
                this_product = Product.objects.get(ID = item)
                product_log += this_product.Slug + '#'
                this_coupon.FK_Products.add(this_product)
    # check users
    if len(users) != 0:
        for item in users:
            if User.objects.filter(id = item).exists():
                this_user = User.objects.get(id = item)
                user_log += this_user.username + '#'
                this_coupon.FK_Users.add(this_user)
    # check categories
    if len(categories) != 0:
        for item in categories:
            if Category.objects.filter(id = item).exists():
                this_category = Category.objects.get(id = item)
                category_log += this_category.Slug + '#'
                this_coupon.FK_Categories.add(this_category)
    # save this log
    if (this_coupon.Log == '') or (this_coupon.Log == None):
        this_coupon.Log = shop_log + '\n' + product_log + '\n' + user_log + '\n' + category_log + '\n' +  '(' + this_coupon.FK_Creator.username + '/' + str(jdatetime.date.today()) + ')' + '\n'
        this_coupon.save()


# add filter to coupon
def AddFilterManagementCoupon(request, id):
    # Check User Status
    if request.user.is_authenticated:
        if request.method == 'POST':
            # get data
            Filter_Shops = request.POST.getlist("copun_shops")
            Filter_Products = request.POST.getlist("copun_products")
            Filter_Users = request.POST.getlist("copun_users")
            Filter_Categories = request.POST.getlist("copun_categories")
            # ---------------------------------------------------------------------
            # get this coupon
            copun = get_object_or_404(Coupon,id = id)
            # add shops and products in coupon
            thread = threading.Thread(target = thread_add_object_to_coupon, args = (copun, Filter_Shops, Filter_Products, Filter_Users, Filter_Categories))
            thread.start()
            # send sms or message
            if len(Filter_Users) != 0:
                SendSMS(Filter_Users, id).run()
            # coupon status
            copun.Publish = True
            copun.save()
            return redirect("nakhll_market:ManagementCoupunList")
        else:
            return redirect("nakhll_market:AddManagementCoupun")
    else:
        return redirect("nakhll_market:AccountLogin")


# check coupon serial
def check_coupon_serial(Coupon_Serial):
    status = True
    # chack status
    if Coupon.objects.filter(Publish = True, Available = True, EndDate__gte = date.today(), SerialNumber = Coupon_Serial).exists():
        status = False
    return status


# create new coupon
def AddManagementCopun(request):
    # Check User Status
    if request.user.is_authenticated:
        if request.method == 'POST':
            # get data
            try:
                Copun_Title = request.POST["copun_title"]
            except:
                Copun_Title = None
            try:
                Copun_Des = request.POST["copun_des"]
            except:
                Copun_Des = None
            try:
                Copun_Serial = request.POST["copun_serial"]
            except:
                Copun_Serial = None
            try:
                Copun_SatrtDay = request.POST["Copun_SatatDay"]
            except:
                Copun_SatrtDay = None
            try:
                Copun_EndDay = request.POST["Copun_EndDay"]
            except:
                Copun_EndDay = None
            try:
                Copun_DiscountType = request.POST["Copun_DiscountType"]
            except:
                Copun_DiscountType = None
            try:
                Copun_DiscountRate = request.POST["Copun_DiscountRate"]
            except:
                Copun_DiscountRate = None
            try:
                Copun_MinimumAmount = request.POST["Copun_MinimumAmount"]
            except:
                Copun_MinimumAmount = None
            try:
                Copun_MaximumAmount = request.POST["Copun_MaximumAmount"]
            except:
                Copun_MaximumAmount = None
            try:
                Copun_NumberOfUse = request.POST["Copun_NumberOfUse"]
            except:
                Copun_NumberOfUse = None
            # check data - and data
            if ((Copun_Title != None) and (Copun_Title != '')) and ((Copun_DiscountRate != None) and (Copun_DiscountRate != '')) and ((Copun_EndDay != None) and (Copun_EndDay != '')) and ((Copun_SatrtDay != None) and (Copun_SatrtDay != '')) and ((Copun_NumberOfUse != None) and (Copun_NumberOfUse != '')):
                # check coupon serial
                status = True
                while (status):
                    if (Copun_Serial != None) and (Copun_Serial != ''):
                        # call check serial coupon function
                        if check_coupon_serial(Copun_Serial):
                            # create new coupon
                            copun = Coupon.objects.create(Title = Copun_Title, SerialNumber = Copun_Serial, FK_Creator = request.user, StartDate = Copun_SatrtDay, EndDate = Copun_EndDay, DiscountRate = Copun_DiscountRate, DiscountStatus = '0', NumberOfUse = Copun_NumberOfUse, DiscountType = Copun_DiscountType)
                            status = False
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
                            context = {
                                'This_User_Profile':this_profile,
                                'This_User_Inverntory': this_inverntory,
                                'Options': options,
                                'MenuList':navbar,
                                'ShowAlart':True,
                                'AlartMessage':'در این بازه زمانی کوپن دیگری با این سریال موجود است.',
                            }

                            return render(request, 'nakhll_market/management/coupon/addmanagecoupon.html', context)
                    else:
                        # create new coupon with random serial
                        copun = Coupon.objects.create(Title = Copun_Title, FK_Creator = request.user, StartDate = Copun_SatrtDay, EndDate = Copun_EndDay, DiscountRate = Copun_DiscountRate, DiscountStatus = '0', NumberOfUse = Copun_NumberOfUse, DiscountType = Copun_DiscountType)
                        status = False
                # <--- end while --->
                # add minimum amount
                if (Copun_MinimumAmount != None) and (Copun_MinimumAmount != ''):
                    copun.MinimumAmount = Copun_MinimumAmount
                    copun.save()
                else:
                    copun.MinimumAmount = 0
                    copun.save()
                # add maximum amount
                if (Copun_MaximumAmount != None) and (Copun_MaximumAmount != ''):
                    copun.MaximumAmount = Copun_MaximumAmount
                    copun.save()
                else:
                    copun.MaximumAmount = 0
                    copun.save()
                # add description
                if (Copun_Des != None) and (Copun_Des != ''):
                    copun.Description = Copun_Des
                    copun.save()
                #-----------------------------------------------------------------------
                # Get User Info
                This_User_Info = GetUserInfo().run(request)
                this_profile = This_User_Info["user_profiel"]
                this_inverntory = This_User_Info["user_inverntory"]
                # Get Menu Item
                options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
                # Get Nav Bar Menu Item
                navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
                # --------------------------------------------------------------------
                class ObjectClass:
                    def __init__(self, item, status):
                        self.Item = item
                        self.Status = status
                # show market class
                show_market_list = []
                for item in Market.objects.filter(Publish = True):
                    show_market_list.append(ObjectClass(item, False))
                # show submarket class
                show_submarket_list = []
                for item in SubMarket.objects.filter(Publish = True):
                    show_submarket_list.append(ObjectClass(item, False))
                # show shop class
                show_shop_list = []
                for item in Shop.objects.filter(Publish = True, Available = True):
                    show_shop_list.append(ObjectClass(item, False))
                # show category class
                show_category_list = []
                for item in Category.objects.filter(Publish = True):
                    show_category_list.append(ObjectClass(item, False))
                # get shops
                pubshops = Shop.objects.filter(Publish = True, Available = True)
                # get products
                pubproducts = Product.objects.filter(Publish = True, Available = True)
                # get users
                pubusers = User.objects.filter(is_active = True)
                # get catrgories
                pubcategories = Category.objects.filter(Publish = True)

                context = {
                    'This_User_Profile':this_profile,
                    'This_User_Inverntory': this_inverntory,
                    'Options': options,
                    'MenuList':navbar,
                    'AllUsers':pubusers,
                    'AllProducts':pubproducts,
                    'AllShops':pubshops,
                    'AllCategories':pubcategories,
                    'Categories':show_category_list,
                    'Shops':show_shop_list,
                    'SubMarkets':show_submarket_list,
                    'Markets':show_market_list,
                    'UserCoupon':copun.id,
                    'ShowAlart':True,
                    'AlartMessage':'کوپن شما ثبت شد، لطفا محدودیت های آن را وارد نمایید.',
                }

                return render(request, 'nakhll_market/management/coupon/manageaddshopincoupon.html', context)
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

                context = {
                    'This_User_Profile':this_profile,
                    'This_User_Inverntory': this_inverntory,
                    'Options': options,
                    'MenuList':navbar,
                    'ShowAlart':True,
                    'AlartMessage':'فیلد های عنوان، تاریخ شروع، تاریخ انقضاء، میزان تخفیف و تعداد دفعات مجاز نمی تواند خالی باشد!',
                }

                return render(request, 'nakhll_market/management/coupon/addmanagecoupon.html', context)
        else:
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
            }

            return render(request, 'nakhll_market/management/coupon/addmanagecoupon.html', context)
    else:
        return redirect("nakhll_market:AccountLogin")




# Management Coupun List
def ManagementCopunList(request):
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
        # get all copuns
        couponlist = Coupon.objects.filter(DiscountStatus = '0', Available = True, Publish = True).order_by('id')

        context = {
            'This_User_Profile':this_profile,
            'This_User_Inverntory': this_inverntory,
            'Options': options,
            'MenuList':navbar,
            'AllUserCupons':couponlist,
        }

        return render(request, 'nakhll_market/management/coupon/managecuponlist.html', context)
    else:
        return redirect("nakhll_market:AccountLogin")


# Check Coupon When Show Cart
def CheckCouponWhenShowCart(request, ID):
    userFactor = Factor.objects.get(ID = ID)
    coupon = userFactor.FK_Coupon
    if coupon.Publish:
        if coupon.Available:
            if coupon.EndDate >= jdatetime.date.today():
                if coupon.FK_Users.all().count() != 0:
                    IsUser = False
                    for item in coupon.FK_Users.all():
                        if item == request.user:
                            IsUser = True
                    if IsUser:
                        if Factor.objects.filter(FK_User = request.user, Publish = True, PaymentStatus = True, FK_Coupon = coupon).count() < int(coupon.NumberOfUse):
                            # Build Product Class
                            class ProductClass:
                                def __init__(self, item, status):
                                    self.Product = item
                                    self.Status = status
                            # Coupon Producs List
                            Product_List = []
                            if coupon.FK_Shops.all().count() != 0:
                                for item in coupon.FK_Shops.all():
                                    for product in Product.objects.filter(Publish = True, FK_Shop = item):
                                        New = ProductClass(product, False)
                                        Product_List.append(New)
                            if coupon.FK_Products.all().count() != 0:
                                for item in coupon.FK_Products.all():
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
                                if coupon.MinimumAmount != '0':
                                    if userFactor.get_total_coupon_test(coupon.id) >= int(coupon.MinimumAmount):
                                        if coupon.MaximumAmount != '0':
                                            if userFactor.get_total_coupon_test(coupon.id) <= int(coupon.MaximumAmount):
                                                # Add Coupn To Factor
                                                userFactor.FK_Coupon = coupon
                                                userFactor.save()
                                                return True
                                            else:
                                                return False
                                        else:
                                            # Add Coupn To Factor
                                            userFactor.FK_Coupon = coupon
                                            userFactor.save()
                                            return True
                                    else:
                                        return False
                                else:
                                    # Add Coupn To Factor
                                    userFactor.FK_Coupon = coupon
                                    userFactor.save()
                                    return True
                            else:
                                return False
                        else:
                            return False
                    else:
                        return False
                else:
                    if Factor.objects.filter(FK_User = request.user, Publish = True, PaymentStatus = True, FK_Coupon = coupon).count() < int(coupon.NumberOfUse):
                        # Build Product Class
                        class ProductClass:
                            def __init__(self, item, status):
                                self.Product = item
                                self.Status = status
                        # Coupon Producs List
                        Product_List = []
                        if coupon.FK_Shops.all().count() != 0:
                            for item in coupon.FK_Shops.all():
                                for product in Product.objects.filter(Publish = True, FK_Shop = item):
                                    New = ProductClass(product, False)
                                    Product_List.append(New)
                        if coupon.FK_Products.all().count() != 0:
                            for item in coupon.FK_Products.all():
                                New = ProductClass(item, False)
                                Product_List.append(New)
                        Product_List = list(dict.fromkeys(Product_List))
                        for factor_item in userFactor.FK_FactorPost.all():    
                            for item in Product_List:
                                if factor_item.FK_Product.ID == item.Product.ID:
                                    item.Status = True
                        # Chechk Coupon
                        if len(Product_List) != 0:
                            for item in Product_List:
                                if item.Status == True:
                                    Check = True
                        else:
                            Check = True
                        if Check:
                            if coupon.MinimumAmount != '0':
                                if userFactor.get_total_coupon_test(coupon.id) >= int(coupon.MinimumAmount):
                                    if coupon.MaximumAmount != '0':
                                        if userFactor.get_total_coupon_test(coupon.id) <= int(coupon.MaximumAmount):
                                            # Add Coupn To Factor
                                            userFactor.FK_Coupon = coupon
                                            userFactor.save()
                                            return True
                                        else:
                                            return False
                                    else:
                                            # Add Coupn To Factor
                                            userFactor.FK_Coupon = coupon
                                            userFactor.save()
                                            return True
                                else:
                                    return False
                            else:
                                # Add Coupn To Factor
                                userFactor.FK_Coupon = coupon
                                userFactor.save()
                                return True 
                        else:
                            return False                               
                    else:
                        return False
            else:
                return False
        else:
            return False
    else:
        return False