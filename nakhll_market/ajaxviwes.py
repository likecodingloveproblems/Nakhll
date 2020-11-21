from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from datetime import datetime
import jdatetime

from django.contrib.auth.models import User

from .models import Shop, Profile, Product, AttrPrice, Alert, BankAccount
from Payment.models import Factor, FactorPost, Wallet, Transaction, Coupon

import io

from django.http.response import HttpResponse

from xlsxwriter.workbook import Workbook
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.conf import settings

# --------------------------------------------------------------------------------------------------------------------------------------


# Check Username With Ajax
def check_new_username(request):
    response_data = {} 

    try: 
        new_username = request.POST.get("username")
        if User.objects.filter(username = new_username).exists():
            response_data['status'] = True
            response_data['msg'] = 'Username Is Exists'
            return JsonResponse(response_data)
        else:
            response_data['status'] = True
            response_data['msg'] = 'Username Is Not Exists'
            return JsonResponse(response_data)
    except:
        response_data['status'] = False
        response_data['msg'] = 'Error In Get Data'
        return JsonResponse(response_data)

# Check NatioalCode With Ajax
def check_new_nationalcode(request):
    response_data = {} 

    try: 
        new_nationalcode = request.POST.get("nationalcode")
        if Profile.objects.filter(NationalCode = new_nationalcode).exists():
            response_data['status'] = True
            response_data['msg'] = 'Natioalcode Is Exists'
            return JsonResponse(response_data)
        else:
            response_data['status'] = True
            response_data['msg'] = 'Natioalcode Is Not Exists'
            return JsonResponse(response_data)
    except:
        response_data['status'] = False
        response_data['msg'] = 'Error In Get Data'
        return JsonResponse(response_data)

# Check PhoneNumber With Ajax
def check_new_phonenumber(request):
    response_data = {} 

    try: 
        new_phonenumber = request.POST.get("phonenumber")
        if Profile.objects.filter(MobileNumber = new_phonenumber).exists():
            response_data['status'] = True
            response_data['msg'] = 'is_exists'
            return JsonResponse(response_data)
        else:
            response_data['status'] = True
            response_data['msg'] = 'is_not_exists'
            return JsonResponse(response_data)
    except:
        response_data['status'] = False
        response_data['msg'] = 'Error In Get Data'
        return JsonResponse(response_data)

# Check Shop Slug With Ajax
def check_new_shop_slug(request):
    response_data = {} 

    try: 
        new_shop_slug = request.POST.get("shop_slug")
        if Shop.objects.filter(Slug = new_shop_slug).exists():
            response_data['status'] = True
            response_data['msg'] = 'Slug Is Exists'
            return JsonResponse(response_data)
        else:
            response_data['status'] = True
            response_data['msg'] = 'Slug Is Not Exists'
            return JsonResponse(response_data)
    except:
        response_data['status'] = False
        response_data['msg'] = 'Error In Get Data'
        return JsonResponse(response_data)


# Check Product Order Zoon
def check_zoon(request):

    response_data = {} 
    if request.POST.get('action') == 'POST':
        # Get User Factor
        factor = Factor.objects.get(FK_User = request.user, PaymentStatus = False)
        # Product List
        product = []
        # Get Data Form HTML
        state = request.POST.get("State")
        bigcity = request.POST.get("BigCity")
        city = request.POST.get("City")
        # Check Zoon
        for item in factor.FK_FactorPost.all():
            if item.FK_Product.PostRangeType == '1':
                for exc in item.FK_Product.FK_ExceptionPostRange.all():
                    if (exc.BigCity != '') and (exc.City == ''):
                        if (exc.State == state) and (exc.BigCity == bigcity):
                            product.append(item.FK_Product)
                    elif (exc.BigCity != '') and (exc.City != ''):
                        if (exc.State == state) and (exc.BigCity == bigcity) and (exc.City == city):
                            product.append(item.FK_Product)
                    else:
                        if exc.State == state:
                            product.append(item.FK_Product)
            elif item.FK_Product.PostRangeType == '2':
                chech = False
                for this in item.FK_Product.FK_PostRange.all():
                    if this.State == state:
                        chech = True
                if chech:
                    for exc in item.FK_Product.FK_ExceptionPostRange.all():
                        if (exc.BigCity != '') and (exc.City == ''):
                            if (exc.State == state) and (exc.BigCity == bigcity):
                                product.append(item.FK_Product)
                        elif (exc.BigCity != '') and (exc.City != ''):
                            if (exc.State == state) and (exc.BigCity == bigcity) and (exc.City == city):
                                product.append(item.FK_Product)
                else:
                    product.append(item.FK_Product)
            elif item.FK_Product.PostRangeType == '3':
                chech = False
                for this in item.FK_Product.FK_PostRange.all():
                    if (this.State == state) and (this.BigCity == bigcity):
                        chech = True
                if chech:
                    for exc in item.FK_Product.FK_ExceptionPostRange.all():
                        if (exc.BigCity != '') and (exc.City != ''):
                            if (exc.State == state) and (exc.BigCity == bigcity) and (exc.City == city):
                                product.append(item.FK_Product)
                else:
                    product.append(item.FK_Product)
            elif item.FK_Product.PostRangeType == '4':
                chech = False
                for this in item.FK_Product.FK_PostRange.all():
                    if (this.State == state) and (this.BigCity == bigcity):
                        if this.City == '':
                            if this.City == city:
                                chech = True
                        else:
                            chech = True
                if chech:
                    for exc in item.FK_Product.FK_ExceptionPostRange.all():
                        if (exc.BigCity != '') and (exc.City != ''):
                            if (exc.State == state) and (exc.BigCity == bigcity) and (exc.City != city):
                                product.append(item.FK_Product)
                else:
                    product.append(item.FK_Product)
            
        if len(product) == 0:
            response_data['status'] = True
            response_data['des'] = None
            return JsonResponse(response_data)
        else:
            response_data['status'] = False
            des = ''
            for item in product:
                des += item.Title + '###'
            response_data['des'] = des
            return JsonResponse(response_data)


# Check Factor Send Info With Ajax
def check_factor_send_info(request):
    response_data = {}
    try:
        id = request.POST.get("factor_id")
        if Factor.objects.filter(ID = id).exists(): 
            this_factor = Factor.objects.get(ID = id)
            if ((this_factor.PhoneNumber == '') or (this_factor.PhoneNumber == None)) or ((this_factor.MobileNumber == '') or (this_factor.MobileNumber == None)) or ((this_factor.State == '') or (this_factor.State == None)) or ((this_factor.BigCity == '') or (this_factor.BigCity == None)) or ((this_factor.City == '') or (this_factor.City == None)) or ((this_factor.Address == '') or (this_factor.Address == None)) or ((this_factor.ZipCode == '') or (this_factor.ZipCode == None)) or ((this_factor.Description == '') or (this_factor.Description == None)):
                response_data['status'] = False
                response_data['msg'] = 'Information Is Not Complete'
                return JsonResponse(response_data)
            else:
                response_data['status'] = True
                response_data['msg'] = 'Complete Information'
                return JsonResponse(response_data)
        else:
            response_data['status'] = False
            response_data['msg'] = 'This Factor Not Exists'
            return JsonResponse(response_data)
    except:
        response_data['status'] = False
        response_data['msg'] = 'Call Function Error'
        return JsonResponse(response_data)


# Check User Profile Info With Ajax
def check_user_profile_info(request):
    response_data = {}
    try:
        this_user_profile = get_object_or_404(Profile, FK_User = request.user)
        if ((this_user_profile.CityPerCode == '') or (this_user_profile.CityPerCode == None)) or ((this_user_profile.PhoneNumber == '') or (this_user_profile.PhoneNumber == None)) or ((this_user_profile.State == '') or (this_user_profile.State == None)) or ((this_user_profile.BigCity == '') or (this_user_profile.BigCity == None)) or ((this_user_profile.City == '') or (this_user_profile.City == None)) or ((this_user_profile.Address == '') or (this_user_profile.Address == None)) or ((this_user_profile.ZipCode == '') or (this_user_profile.ZipCode == None)):
            response_data['status'] = False
            response_data['msg'] = 'Information Is Not Complete'
            return JsonResponse(response_data)
        else:
            response_data['status'] = True
            response_data['msg'] = 'Information Is Complete'
            return JsonResponse(response_data)
    except:
        response_data['status'] = False
        response_data['msg'] = 'Call Function Error'
        return JsonResponse(response_data)


# Check Product Slug With Ajax
def check_new_product_slug(request):
    response_data = {}

    try:
        new_product_slug = request.POST.get("product_slug")
        if Product.objects.filter(Slug = new_product_slug).exists():
            response_data['status'] = True
            response_data['msg'] = 'Slug Is Exists'
            return JsonResponse(response_data)
        else:
            response_data['status'] = True
            response_data['msg'] = 'Slug Is Not Exists'
            return JsonResponse(response_data)
    except:
        response_data['status'] = False
        response_data['msg'] = 'Error In Get Data'
        return JsonResponse(response_data)


# Check Factor Inventory Slug With Ajax
def Check_Factor_Inventory(request):
    response_data = {}
    # Product Is False List
    product_is_list = ''
    # Inventory Status
    inventory_status = True
    try:
        factor_id = request.POST.get("factor_id")
        factor = get_object_or_404(Factor, ID = factor_id)
        for item in factor.FK_FactorPost.all():
            if item.FK_Product.Status == '1':
                if item.FK_Product.Inventory < item.ProductCount:
                    product_is_list += item.FK_Product.Title + ', '
                    inventory_status = False

        response_data['status'] = inventory_status
        response_data['products'] = product_is_list
        return JsonResponse(response_data)
    except:
        response_data['status'] = False
        response_data['products'] = 'Error'
        return JsonResponse(response_data)


# Check Product Inventory With Ajax
def Check_Product_Inventory(request):
    response_data = {}
    # Inventory Status
    inventory_status = True
    try:
        count = request.POST.get("count")
        product_id = request.POST.get("product_id")
        product = get_object_or_404(Product, ID = product_id)
        if product.Inventory < count:
            inventory_status = False 

        response_data['status'] = inventory_status
        return JsonResponse(response_data)
    except:
        response_data['status'] = False
        response_data['msg'] = 'Error'
        return JsonResponse(response_data)


# Add Singel Product From Cart With Ajax
def Add_Single_Item_From_Cart(request):
    response_data = {}
    # Get Factor Item
    item_id = request.POST.get("item_id")
    FactorPost_Item = get_object_or_404(FactorPost, ID = item_id)
    if Factor.objects.filter(FK_User = request.user, PaymentStatus = False).exists():
        order = Factor.objects.filter(FK_User = request.user, PaymentStatus = False)[0]
        # check if the order item is in the order
        if order.FK_FactorPost.filter(ID = item_id).exists():
            if FactorPost_Item.FK_Product.Status == '1':
                if FactorPost_Item.FK_Product.Inventory <= FactorPost_Item.ProductCount:
                    response_data['status'] = False
                    response_data['msg'] = FactorPost_Item.FK_Product.Title
                    return JsonResponse(response_data)
                else:
                    FactorPost_Item.ProductCount += 1
                    FactorPost_Item.save()
                    response_data['status'] = True
                    response_data['p_count'] = FactorPost_Item.ProductCount
                    response_data['i_price'] = FactorPost_Item.get_total_item_price()
                    response_data['f_price'] = order.get_total()
                    return JsonResponse(response_data)
            else:
                if FactorPost_Item.FK_Product.Status == '4':
                    response_data['status'] = False
                    response_data['msg'] = FactorPost_Item.FK_Product.Title
                    return JsonResponse(response_data)
                else:
                    FactorPost_Item.ProductCount += 1
                    FactorPost_Item.save()
                    response_data['status'] = True
                    response_data['p_count'] = FactorPost_Item.ProductCount
                    response_data['i_price'] = FactorPost_Item.get_total_item_price()
                    response_data['f_price'] = order.get_total()
                    return JsonResponse(response_data)
        else:
            response_data['status'] = False
            response_data['msg'] = 'Error'
            return JsonResponse(response_data)
    else:
        response_data['status'] = False
        response_data['msg'] = 'Error'
        return JsonResponse(response_data)


# Remove Singel Product From Cart With Ajax
def Remove_Single_Item_From_Cart(request):
    response_data = {}
    # Get Factor Item
    item_id = request.POST.get("item_id")
    FactorPost_Item = get_object_or_404(FactorPost, ID = item_id)

    if Factor.objects.filter(FK_User = request.user, PaymentStatus = False).exists():
        order = Factor.objects.filter(FK_User = request.user, PaymentStatus = False)[0]
        # Check Factor Item
        if order.FK_FactorPost.filter(ID = item_id).exists():
            if FactorPost_Item.ProductCount > 1:
                FactorPost_Item.ProductCount -= 1
                FactorPost_Item.save()
                response_data['status'] = True
                response_data['p_count'] = FactorPost_Item.ProductCount
                response_data['i_price'] = FactorPost_Item.get_total_item_price()
                response_data['f_price'] = order.get_total()
                response_data['dlt'] = False
                return JsonResponse(response_data)
            else:
                for item in FactorPost_Item.FK_AttrPrice.all():                   
                    FactorPost_Item.FK_AttrPrice.remove(item)
                order.FK_FactorPost.remove(FactorPost_Item)
                FactorPost_Item.delete()
                response_data['status'] = True
                response_data['dlt'] = True
                return JsonResponse(response_data)
        else:
            response_data['status'] = False
            response_data['msg'] = 'Error'
            return JsonResponse(response_data)
    else:
        response_data['status'] = False
        response_data['msg'] = 'Error'
        return JsonResponse(response_data)



# Pay Factor by wallet With Ajax
def Pay_Factor_by_wallet(request):
    response_data = {}
    try:
        factor_id = request.POST.get("factor_id")
        factor = get_object_or_404(Factor, ID = factor_id)
        wallet = get_object_or_404(Wallet , FK_User = request.user)
        val1 = int(factor.get_end_price())
        val2 = int(wallet.Inverntory)
        if val1 > val2 :
            response_data['status'] = False
            response_data['msg'] = 'موجودی کیف پول شما برای پرداخت این فاکتور کافی نمی باشد.'
            return JsonResponse(response_data) 
        else:
            if factor.PaymentType == '1':
                response_data['status'] = False
                response_data['msg'] = 'خطایی در شیوه پرداخت رخ داده است!'
                
                return JsonResponse(response_data)

            elif factor.PaymentType == '2':
                inverntory_wallet = int(wallet.Inverntory) - int(factor.get_end_price())
                wallet.Inverntory = str(inverntory_wallet)
                wallet.save()
                factor.PaymentStatus = True
                factor.OrderStatus='3'
                factor.TotalPrice = factor.get_end_price()
                factor.PostPrice = factor.get_postprice()
                factor.DiscountRate = factor.Coupon_price_min()

                try:
                    getCoupon = Coupon.objects.get(id = factor.FK_Coupon.id)
                    if getCoupon.DiscountStatus == '0':
                        factor.DiscountType = '1'
                        factor.save()
                    elif getCoupon.DiscountStatus == '1':
                        factor.DiscountType = '2'
                        factor.save()
                    factor.OrderDate = datetime.now()
                    factor.save()
                except:
                    getCoupon: None
                    factor.OrderDate = datetime.now()
                    factor.save()

                # ------- Remove FactorPost AttrPrice -------
                Factor_res = ''
                for factpost in factor.FK_FactorPost.all():
                    factpost.EndPrice = factpost.get_total_item_price()
                    print(factpost.get_total_item_price())
                    factpost.save()
                    for item in factpost.FK_AttrPrice.all():
                        Factor_res += Factor_res + ' قیمت ویژگی : ' + item.Value +'|'+ item.Unit + '|' + 'با مبلغ اضافه '+ item.ExtraPrice + '### \n'
                    Factor_res += 'ابعاد محصول'+ factpost.FK_Product.Title + factpost.FK_Product.Length_With_Packaging +'*'+ factpost.FK_Product.Width_With_Packaging +'*'+ factpost.FK_Product.Height_With_Packaging +'\n وزن خالص :'+ factpost.FK_Product.Net_Weight +'- وزن با بسته بندی :'+ factpost.FK_Product.Weight_With_Packing
                    try:
                        if factpost.FK_Product.Status == '1':
                            factpost.FK_Product.Inventory -= factpost.ProductCount     
                            factpost.FK_Product.save()
                            if int(factpost.FK_Product.Inventory) == 0 :
                                factpost.FK_Product.Status = '4'
                                factpost.FK_Product.save()
                            elif int(factpost.FK_Product.Inventory) < 0:
                                factpost.FK_Product.Status = '4'
                                factpost.FK_Product.Inventory = 0
                                factpost.FK_Product.save()
                    except:
                        factpost.FK_Product.Status = '4'
                        factpost.FK_Product.Inventory = 0
                        factpost.FK_Product.save()
                factpost.Description = Factor_res
                factpost.save()
                for factpost in factor.FK_FactorPost.all():
                    for item in factpost.FK_AttrPrice.all():
                        factpost.FK_AttrPrice.remove(item)
                # --------------------- End -----------------
                alert = Alert.objects.create(Part = '12', FK_User = request.user, Slug = factor.ID)
                des_trans=' پرداخت از کیف پول برای فاکتور '+ factor.FactorNumber
                pricefactori = factor.get_end_price()
                transaction = Transaction.objects.create(FK_User = request.user, Price = pricefactori, Type = '6', Description = des_trans)
                response_data['status'] = True
                response_data['msg'] = 'پرداخت از کیف پول شما به موفقیت انجام شد لطفا منتظر بمانید.'
                return JsonResponse(response_data)
    except:
        response_data['status'] = False
        response_data['msg'] = 'خطایی رخ داده است مجدد اقدام نمایید یا با پشتیبانی سایت تماس بگیرید.'
        return JsonResponse(response_data)




# Add New Email With Ajax
def Add_New_Email(request):
    response_data = {}
    # Get Email
    this_email = request.POST.get("email")

    if not Newsletters.objects.filter(Email = this_email).exists():
        # Add New Data
        Newsletters.objects.create(Email = this_email)
        response_data['status'] = True
        response_data['msg'] = 'Email New Email'
        return JsonResponse(response_data)
    else:
        response_data['status'] = False
        response_data['msg'] = 'Email Is Exist'
        return JsonResponse(response_data)



# Check User Back Account Info With Ajax
def check_user_bank_account_info(request):
    response_data = {}
    try:
        this_user_profile = get_object_or_404(Profile, FK_User = request.user)
        if not BankAccount.objects.filter(FK_Profile = this_user_profile).exists():
            response_data['status'] = False
            response_data['msg'] = 'Information Is Not Complete'
            return JsonResponse(response_data)
        else:
            response_data['status'] = True
            response_data['msg'] = 'Information Is Complete'
            return JsonResponse(response_data)
    except:
        response_data['status'] = False
        response_data['msg'] = 'Call Function Error'
        return JsonResponse(response_data)



# Add To Cart WithOur Price Attribute With Ajax
def add_to_cart_without_price_attribute(request):
    response_data = {}
    try:
        if Product.objects.filter(ID = request.POST.get("product_id")).exists():
            # Get This Product
            this_prodcut = get_object_or_404(Product, ID = request.POST.get("product_id"))
            # Check Peoduct Status
            if (this_prodcut.Status == '4') or (this_prodcut.Inventory == 0):
                response_data['status'] = False
                response_data['code'] = '400'
                response_data['msg'] = 'Product Not Available'
                return JsonResponse(response_data)
            else:
                new_item = None
                if Factor.objects.filter(FK_User = request.user, PaymentStatus = False).exists():
                    # Get Last User Factor
                    user_factor = Factor.objects.filter(FK_User = request.user, PaymentStatus = False)[0]
                    if user_factor.FK_FactorPost.filter(FK_Product = this_prodcut, FK_User = request.user).exists():
                        # Get Item
                        for factor_item in user_factor.FK_FactorPost.filter(FK_Product = this_prodcut, FK_User = request.user):
                            if factor_item.FK_AttrPrice.count() == 0:
                                new_item = factor_item
                        new_item.ProductCount += 1
                        new_item.save()
                        response_data['status'] = True
                        response_data['code'] = '200'
                        response_data['msg'] = 'Add Item Count'
                        return JsonResponse(response_data)
                    else:
                        new_item = FactorPost.objects.create(FK_Product = this_prodcut, FK_User = request.user)
                        user_factor.FK_FactorPost.add(new_item)
                        response_data['status'] = True
                        response_data['code'] = '201'
                        response_data['msg'] = 'Create New Item'
                        return JsonResponse(response_data)
                else:
                    user_factor = Factor.objects.create(FK_User = request.user, PaymentStatus = False)
                    new_item = FactorPost.objects.create(FK_Product = this_prodcut, FK_User = request.user)
                    user_factor.FK_FactorPost.add(new_item)
                    response_data['status'] = True
                    response_data['code'] = '201'
                    response_data['msg'] = 'Create New Factor And Add Product'
                    return JsonResponse(response_data)
        else:
            response_data['status'] = False
            response_data['code'] = '404'
            response_data['msg'] = 'Product Not Found'
            return JsonResponse(response_data)
    except:
        response_data['status'] = False
        response_data['code'] = '500'
        response_data['msg'] = 'Error'
        return JsonResponse(response_data)



# Add To Cart With Price Attribute With Ajax
def add_to_cart_with_price_attribute(request):
    if request.user.is_authenticated:
        response_data = {}
        try:
            if Product.objects.filter(ID = request.POST.get("product_id")).exists():
                # Get This Product
                this_product = get_object_or_404(Product, ID = request.POST.get("product_id"))
                # Get Price Attribute id
                price_attribute_list = request.POST.getlist("attrpriceitem")
                # Get Attribute Price Object
                attr_price_list = []
                for item in price_attribute_list:
                    if AttrPrice.objects.filter(id = item):
                        attr_price_list.append(AttrPrice.objects.get(id = item))
                # Check Peoduct Status
                if (this_product.Status == '4') or (this_product.Inventory == 0):
                    response_data['status'] = False
                    response_data['code'] = '404'
                    response_data['msg'] = 'Product Not Available'
                    return JsonResponse(response_data)
                else:
                    new_item = None
                    if Factor.objects.filter(FK_User = request.user, PaymentStatus = False).exists():
                        # Get Last User Factor
                        user_factor = Factor.objects.filter(FK_User = request.user, PaymentStatus = False)[0]
                        this_order_items = user_factor.FK_FactorPost.filter(FK_Product = this_product, FK_User = request.user)
                        if len(attr_price_list) != 0:
                            for item in attr_price_list:
                                this_order_items = this_order_items.filter(FK_AttrPrice__id = item.id)
                            for item in this_order_items:
                                if item.FK_AttrPrice.all().count() == len(attr_price_list):
                                    new_item = item
                            if (len(this_order_items) != 0) and (new_item != None):
                                if int(new_item.FK_Product.Inventory) > int(new_item.ProductCount):
                                    new_item.ProductCount += 1
                                    new_item.save()
                                    response_data['status'] = True
                                    response_data['code'] = '200'
                                    response_data['msg'] = 'Add Item Count'
                                    return JsonResponse(response_data)
                                else:
                                    response_data['status'] = False
                                    response_data['code'] = '404'
                                    response_data['msg'] = 'Inventory Is Not Enough'
                                    return JsonResponse(response_data)                                 
                            else:
                                new_item = FactorPost.objects.create(FK_Product = this_product, FK_User = request.user)
                                # Add Price Attribute
                                for item in attr_price_list:
                                    new_item.FK_AttrPrice.add(item)
                                user_factor.FK_FactorPost.add(new_item)
                                response_data['status'] = True
                                response_data['code'] = '201'
                                response_data['msg'] = 'Craete New Item'
                                return JsonResponse(response_data)
                        else:
                            if user_factor.FK_FactorPost.filter(FK_Product = this_product, FK_User = request.user).exists():
                                # Get Item
                                new_item = this_order_items.get(FK_AttrPrice = None)
                                if int(new_item.FK_Product.Inventory) > int(new_item.ProductCount):
                                    new_item.ProductCount += 1
                                    new_item.save()
                                    response_data['status'] = True
                                    response_data['code'] = '200'
                                    response_data['msg'] = 'Add Item Count'
                                    return JsonResponse(response_data)
                                else:
                                    response_data['status'] = False
                                    response_data['code'] = '404'
                                    response_data['msg'] = 'Inventory Is Not Enough'
                                    return JsonResponse(response_data)
                            else:
                                new_item = FactorPost.objects.create(FK_Product = this_product, FK_User = request.user)
                                user_factor.FK_FactorPost.add(new_item)
                                response_data['status'] = True
                                response_data['code'] = '201'
                                response_data['msg'] = 'Create New Item'
                                return JsonResponse(response_data)               
                    else:
                        user_factor = Factor.objects.create(FK_User = request.user, PaymentStatus = False)
                        new_item = FactorPost.objects.create(FK_Product = this_product, FK_User = request.user)
                        if len(attr_price_list) != 0:
                            # Add Price Attribute
                            for item in attr_price_list:
                                new_item.FK_AttrPrice.add(item)
                        user_factor.FK_FactorPost.add(new_item)
                        response_data['status'] = True
                        response_data['code'] = '201'
                        response_data['msg'] = 'Create New Factor And Add Product'
                        return JsonResponse(response_data)
            else:
                response_data['status'] = False
                response_data['code'] = '400'
                response_data['msg'] = 'Product Not Found'
                return JsonResponse(response_data)
        except Exception as e:
            response_data['status'] = False
            response_data['code'] = '500'
            response_data['msg'] = str(e)
            return JsonResponse(response_data)
    else:
        response_data['status'] = False
        response_data['code'] = '401'
        response_data['msg'] = 'User Not Logged In'
        return JsonResponse(response_data)




# Add User Location Info With Ajax
def add_user_location_info(request):
    response_data = {}
    try:
        # Get User id
        this_user = request.POST.get("user_id")
        # Get Data
        user_phone_number = request.POST.get("user_phonenumber")
        user_city_precode = request.POST.get("user_city_precode")
        user_state = request.POST.get("user_state")
        user_bigcity = request.POST.get("user_bigcity")
        user_city = request.POST.get("user_city")
        user_address = request.POST.get("user_address")
        user_zipcode = request.POST.get("user_zipcode")
        # Get Profile
        this_profile = Profile.objects.get(FK_User_id = this_user)
        # Set Date
        this_profile.ZipCode = user_zipcode
        this_profile.Address = user_address
        this_profile.State = user_state
        this_profile.BigCity = user_bigcity
        this_profile.City = user_city
        this_profile.PhoneNumber = user_phone_number
        this_profile.CityPerCode = user_city_precode
        this_profile.save()
        response_data['status'] = True
        response_data['msg'] = 'Success'
        return JsonResponse(response_data)
    except Exception as e:
        response_data['status'] = False
        response_data['msg'] = str(e)
        return JsonResponse(response_data)


def get_factor_excel_file(request, id):
    # create io file
    output = io.BytesIO()
    # get factor
    this_factor = get_object_or_404(Factor, ID = id)
    # create xlsx
    workbook = Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet(this_factor.FactorNumber)
    # set row
    row = 0
    # set factor filed
    worksheet.write(row, 0, 'شماره سریال')
    worksheet.write(row, 1, 'تاریخ خرید')
    worksheet.write(row, 2, 'کل هزینه')
    worksheet.write(row, 3, 'هزینه پست')
    worksheet.write(row, 4, 'میزان تخفیف')
    worksheet.write(row, 5, 'نوع تخفیف')
    worksheet.write(row, 6, 'وضعیت فاکتور')
    worksheet.write(row, 7, 'نوع پرداخت')
    worksheet.write(row, 8, 'توضیحات')
    # set factor data
    row += 1
    worksheet.write(row, 0, this_factor.FactorNumber)
    worksheet.write(row, 1, str(jdatetime.date.fromgregorian(day = this_factor.OrderDate.date().day, month = this_factor.OrderDate.date().month, year = this_factor.OrderDate.date().year)))
    worksheet.write(row, 2, this_factor.TotalPrice)
    worksheet.write(row, 3, this_factor.PostPrice)
    worksheet.write(row, 4, this_factor.DiscountRate)
    worksheet.write(row, 5, this_factor.get_coupon_status())
    worksheet.write(row, 6, this_factor.get_factor_status())
    worksheet.write(row, 7, this_factor.get_factor_payment_type())
    worksheet.write(row, 8, this_factor.Description)
    # set user filed
    row += 2
    worksheet.write(row, 0, 'نام خریدار')
    worksheet.write(row, 1, 'موبایل')
    worksheet.write(row, 2, 'کد پستی')
    worksheet.write(row, 3, 'پیش شماره شهر')
    worksheet.write(row, 4, 'شماره ثابت')
    worksheet.write(row, 5, 'استان')
    worksheet.write(row, 6, 'شهرستان')
    worksheet.write(row, 7, 'شهر')
    worksheet.write(row, 8, 'آدرس')
    # set user data
    row += 1
    worksheet.write(row, 0, this_factor.FK_User.first_name + ' ' + this_factor.FK_User.last_name)
    worksheet.write(row, 1, this_factor.MobileNumber)
    worksheet.write(row, 2, this_factor.ZipCode)
    worksheet.write(row, 3, this_factor.CityPerCode)
    worksheet.write(row, 4, this_factor.PhoneNumber)
    worksheet.write(row, 5, this_factor.State)
    worksheet.write(row, 6, this_factor.BigCity)
    worksheet.write(row, 7, this_factor.City)
    worksheet.write(row, 8, this_factor.Address)
    # set product filed
    row += 2
    worksheet.write(row, 0, 'نام محصول')
    worksheet.write(row, 1, 'قیمت')
    worksheet.write(row, 2, 'تعداد')
    worksheet.write(row, 3, 'نام حجره')
    worksheet.write(row, 4, 'مدیریت حجره')
    # set product data
    row += 1
    for item in this_factor.FK_FactorPost.all():
        worksheet.write(row, 0, item.FK_Product.Title)
        worksheet.write(row, 1, item.FK_Product.Price)
        worksheet.write(row, 2, item.ProductCount)
        worksheet.write(row, 3, item.FK_Product.FK_Shop.Title)
        worksheet.write(row, 4, item.FK_Product.FK_Shop.FK_ShopManager.first_name + ' ' + item.FK_Product.FK_Shop.FK_ShopManager.last_name)
        row += 1

    workbook.close()

    output.seek(0)

    response = HttpResponse(output.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response['Content-Disposition'] = "attachment; filename = " + str(this_factor.FactorNumber) + ".xlsx"

    output.close()

    return response