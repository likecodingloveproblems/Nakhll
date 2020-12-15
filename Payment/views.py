from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.http import HttpResponse, HttpResponseRedirect

from django.views.decorators.http import require_POST 
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from nakhll_market import management_coupon_views
from nakhll_market.models import Shop, Product, Profile, Option_Meta, Newsletters, AttrPrice, Alert
from django.utils import timezone
from .models import Factor, FactorPost ,Wallet,Transaction, PostBarCode, Coupon, Campaign
from .models import PecOrder, PecTransaction, PecConfirmation, PecReverse
from django.contrib.auth.models import User
from django.utils.datastructures import MultiValueDictKeyError
from .forms import forms
import datetime
import jdatetime
from .forms import CartAddProductForm 
from zeep import Client
import threading
import json
import os

try:
    # ## zarin pal
    # MERCHANT= os.environ.get('ZARIN_MERCHANT')
    # client = Client('https://www.zarinpal.com/pg/services/WebGate/wsdl')
    # email = os.environ.get('ZARIN_EMAIL')  # Optional

    ## pec
    PIN = os.environ.get('PEC_PIN')
    saleService = Client('https://pec.shaparak.ir/NewIPGServices/Sale/SaleService.asmx?wsdl')
    confirmService = Client('https://pec.shaparak.ir/NewIPGServices/Confirm/ConfirmService.asmx?wsdl')
    reverseService = Client('https://pec.shaparak.ir/NewIPGServices/Reverse/ReversalService.asmx?wsdl')
    ClientSaleRequestData = saleService.get_type('ns0:ClientSaleRequestData')
    ClientConfirmRequestData = confirmService.get_type('ns0:ClientConfirmRequestData')
    ClientReversalRequestData = reverseService.get_type('ns0:ClientReversalRequestData')

    # GENERAL
    CallbackURL = format(os.environ.get('CALLBACKURL')) # Important: need to edit for realy server.
except:
    print('PEC IS NOT CENNECTED...')
# ------------------------------------------------------ Compaing Functions ----------------------------------------------------

# check First Buy
def Check_Is_First(user_id):
    # Build Result 
    class ResultClass:
        def __init__(self,  message, status):
            self.Message = message
            self.Status = status

    # Get User
    this_user = User.objects.get(id = user_id)
    # Check User Is First Buy
    if (Factor.objects.filter(FK_User = this_user, PaymentStatus = True).count()) == 0:

        # Get Last User Factor
        factor = Factor.objects.filter(FK_User = this_user, PaymentStatus = False)[0]
        factor.FK_Campaign = Campaign.objects.get(id = 1)
        factor.CampaingType = '5'
        factor.save()
        # Set Result
        New_Obj = ResultClass('Shoma Kharid Avali Hastid', True)

    else:

        # Set Result
        New_Obj = ResultClass('Shoma Kharid Avali Mahsob Nemishavaid!', False)
    
    return New_Obj

# ------------------------------------------------------------------------------------------------------------------------------


# Check Factor Not Null
def factor_not_null(factor):
    # Check Cart
    for item in factor.FK_FactorPost.all():
        if item.FK_Product != None:
            if item.FK_Product.Status == '4':
                factor.FK_FactorPost.remove(item)
            elif item.FK_Product.Available == False:
                factor.FK_FactorPost.remove(item)
            elif item.FK_Product.Publish == False:
                factor.FK_FactorPost.remove(item)
        else:
            factor.FK_FactorPost.remove(item)
    
    if factor.FK_FactorPost.all().count() == 0:
        factor.FK_Coupon = None
        factor.FK_Campaign = None
        factor.save()
        return False
    else:
        return True


# Show Cart To User
def show_cart(request):
    
    if request.user.is_authenticated :
        # Get User Info
        
        this_profile = Profile.objects.get(FK_User=request.user)
        this_inverntory = request.user.WalletManager.Inverntory
        # Get Menu Item
        options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
        # Get Nav Bar Menu Item
        navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
        # ------------------------------------------------------------------------        
        User_Factor = Factor.objects.filter(FK_User = request.user, PaymentStatus = False)
        if User_Factor.exists():
            factor = User_Factor[0]
            # Check Coupon Validity
            if factor.FK_Coupon != None:
                if not management_coupon_views.CheckCouponWhenShowCart(request, factor.ID):
                    factor.FK_Coupon = None
                factor.save()
            # Check Cart
            for item in factor.FK_FactorPost.all():
                if item.FK_Product != None:
                    if item.FK_Product.Status == '4':
                        factor.FK_FactorPost.remove(item)
                    elif item.FK_Product.Available == False:
                        factor.FK_FactorPost.remove(item)
                    elif item.FK_Product.Publish == False:
                        factor.FK_FactorPost.remove(item)
                else:
                    factor.FK_FactorPost.remove(item)
            
            if factor.FK_FactorPost.all().count() == 0:
                factor.FK_Coupon = None
                factor.FK_Campaign = None
                factor.save()
        else:
            factor = Factor.objects.create(FK_User = request.user, PaymentStatus = False)

        context = {
            'This_User_Profile':this_profile,
            'This_User_Inverntory': this_inverntory,
            'Options': options,
            'MenuList':navbar,
            'Factor':factor,
        }
        
        return render(request, 'payment/cart/pages/cart.html', context)

    else:
        # i = request.path
        # return redirect('/login/?next=' + i)
        return ("nakhll_market:AccountLogin")


class check_product_send_status:
    def run(self, this_factor):
        shipping_cost_by_customer = []
        area_in_shop_city = []
        post_module = []
        # Check
        if not this_factor.check_order_total_weight():
            shipping_cost_by_customer = this_factor.get_product_by_status(0)
            for item in this_factor.get_product_by_status(1):
                shipping_cost_by_customer.append(item)
            for item in this_factor.get_product_by_status(2):
                shipping_cost_by_customer.append(item)
        else:
            area_in_shop_city = this_factor.get_product_by_status(1)
            post_module = this_factor.get_product_by_status(2)
        # Set Result
        result = {
            "shipping_cost_by_customer": shipping_cost_by_customer,
            "area_in_shop_city": area_in_shop_city,
            "post_module": post_module,
        }
        return result


    
# Show Cart To User
def Set_Send_Info(request):

    if request.user.is_authenticated :
        # Get User Factor
        if request.method == 'POST':
            Factor_FirstName = request.POST["Factor_FirstName"]
            Factor_LastName = request.POST["Factor_LastName"]
            Factor_MobileNumber = request.POST["Factor_MobileNumber"]
            # User Location Info
            Factor_State = request.POST["Factor_State"]
            Factor_BigCity = request.POST["Factor_BigCity"]
            Factor_City = request.POST["Factor_City"]
            Factor_Address = request.POST["Factor_Address"]
            Factor_ZipCode = request.POST["Factor_ZipCode"]
            # User Static PhoneNumbr
            Factor_PhoneNumber = request.POST["Factor_PhoneNumber"]
            Factor_CityPerCode = request.POST["Factor_CityPerCode"]
            # -----------------------------------------------------------------------------
             # Get User Info
            this_profile = Profile.objects.get(FK_User=request.user)
            this_inverntory = request.user.WalletManager.Inverntory
            # Get Menu Item
            options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
            # Get Nav Bar Menu Item
            navbar = Option_Meta.objects.filter(Title = 'nav_menu_items') 
            # ------------------------------------------------------------------------------
            factor = Factor.objects.filter(FK_User_id = request.user, PaymentStatus = False)[0]
            # Check Factor
            if not factor_not_null(factor):
                return redirect("Payment:cartdetail")
            # ------------------------------------------------------------------------------
            # Get User State, BigCity, City Title
            state = ''
            bigcity = ''
            city = ''
            object = None
            with open('Iran.json', encoding = 'utf8') as f:
                object = json.load(f)
            for i in object:
                if (i['divisionType'] == 1) and (i['id'] == int(Factor_State)):
                    state = i['name']
                if (i['divisionType'] == 2) and (i['id'] == int(Factor_BigCity)):
                    bigcity = i['name']
                if (i['divisionType'] == 3) and (i['id'] == int(Factor_City)):
                    if i['name'] == 'مرکزی':
                        for j in object:
                            if (j['divisionType'] == 2) and (j['id'] == i['parentCountryDivisionId']):
                                city = j['name']
                    else:
                        city = i['name']
            # Set Data To Factor
            factor.MobileNumber = Factor_MobileNumber
            factor.PhoneNumber = Factor_PhoneNumber
            factor.CityPerCode = Factor_CityPerCode
            factor.State = state
            factor.BigCity = bigcity
            factor.City = city
            factor.Address = Factor_Address
            factor.ZipCode = Factor_ZipCode
            factor.Description = ' دریافت کننده : ' + Factor_FirstName + ' ' + Factor_LastName
            factor.OrderDate = datetime.datetime.today()
            factor.save()
            # -------------------------------------------------------------------------------
            cart_products = check_product_send_status().run(factor)
            shipping_cost_by_customer = cart_products["shipping_cost_by_customer"]
            area_in_shop_city = cart_products["area_in_shop_city"]
            post_module = cart_products["post_module"]
            if factor.get_end_price() > int(this_inverntory):
                wallet_pay = False
            else:
                wallet_pay = True
            
            context = {
                'This_User_Profile':this_profile,
                'This_User_Inverntory': this_inverntory,
                'Options': options,
                'MenuList':navbar,
                'Factor':factor,
                'SCBC_List':shipping_cost_by_customer,
                'AISC_List':area_in_shop_city,
                'PM_List':post_module,
                'PM_Price':factor.caculate_product_when_status_is_post(),
                'Wallet_Pay_Status':wallet_pay,

            }
            
            return render(request, 'payment/cart/pages/pay.html', context)

        else:
            # Get User Info
            this_profile = Profile.objects.get(FK_User=request.user)
            this_inverntory = request.user.WalletManager.Inverntory
            # Get Menu Item
            options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
            # Get Nav Bar Menu Item
            navbar = Option_Meta.objects.filter(Title = 'nav_menu_items') 
            # ----------------------------------------------------------------------
            factor = Factor.objects.filter(FK_User_id = request.user, PaymentStatus = False)[0]
            # Check Cart
            if not factor_not_null(factor):
                return redirect("Payment:cartdetail")

            context = {
                'This_User_Profile':this_profile,
                'This_User_Inverntory': this_inverntory,
                'Options': options,
                'MenuList':navbar,
                'Factor':factor,
            }

            return render(request, 'payment/cart/pages/sendinfo.html', context)

    else:

        return redirect("nakhll_market:AccountLogin")



def Pay_Detail(request):
    if request.user.is_authenticated:
        # Get User Info
        
        this_profile = Profile.objects.get(FK_User=request.user)
        this_inverntory = request.user.WalletManager.Inverntory
        # Get Menu Item
        options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
        # Get Nav Bar Menu Item
        navbar = Option_Meta.objects.filter(Title = 'nav_menu_items') 
        # ------------------------------------------------------------------------------
        factor = Factor.objects.filter(FK_User_id = request.user, PaymentStatus = False)[0]
        # Check Cart
        if not factor_not_null(factor):
            return redirect("Payment:cartdetail")
        shipping_cost_by_customer = factor.get_product_by_status(0)
        area_in_shop_city = factor.get_product_by_status(1)
        post_module = factor.get_product_by_status(2)
        if factor.get_end_price() > int(this_inverntory):
            wallet_pay = False
        else:
            wallet_pay = True

        context = {
            'This_User_Profile':this_profile,
            'This_User_Inverntory': this_inverntory,
            'Options': options,
            'MenuList':navbar,
            'Factor':factor,
            'SCBC_List':shipping_cost_by_customer,
            'AISC_List':area_in_shop_city,
            'PM_List':post_module,
            'PM_Price':factor.caculate_product_when_status_is_post(),
            'Wallet_Pay_Status':wallet_pay,
        }
        
        return render(request, 'payment/cart/pages/pay.html', context)
    else:
        return redirect("nakhll_market:AccountLogin")



def Final_Factor(request):
    if request.user.is_authenticated:

        if request.method == 'POST':
            # Get Date
            pay_type = request.POST["pay_status_btn"]
            # Get User Info
            this_profile = Profile.objects.get(FK_User=request.user)
            this_inverntory = request.user.WalletManager.Inverntory
            # Get Menu Item
            options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
            # Get Nav Bar Menu Item
            navbar = Option_Meta.objects.filter(Title = 'nav_menu_items') 
            # ------------------------------------------------------------------------------
            factor = Factor.objects.filter(FK_User_id = request.user, PaymentStatus = False)[0]
            # Set Pay Type
            if pay_type == 'pay_pec' or pay_type == 'pay_zarin':
                factor.PaymentType = '1'
            elif pay_type == 'pay_wallet':
                factor.PaymentType = '2'
            factor.save()
            # Check Cart
            if not factor_not_null(factor):
                return redirect("Payment:cartdetail")
            
            context = {
                'This_User_Profile':this_profile,
                'This_User_Inverntory': this_inverntory,
                'Options': options,
                'MenuList':navbar,
                'Factor':factor,
                'bank_port':pay_type,
            }
            
            return render(request, 'payment/cart/pages/finalfactor.html', context)
        else:
            return redirect("Payment:Pay_Detail")
    else:
        return redirect("nakhll_market:AccountLogin")



def send_request_first(request, factor_id, bank_port):
    factor = get_object_or_404(Factor, ID = factor_id)
    Inventory_true = True
    for factpost in factor.FK_FactorPost.all():
        if factpost.FK_Product.Status == '1':
            if factpost.FK_Product.Inventory < factpost.ProductCount:
                Inventory_true = False
    if  Inventory_true == True:
        amounts = factor.get_end_price()
        if amounts >=10000 :
            mobile = factor.MobileNumber
            return send_request(request, factor, amounts, mobile, bank_port)
    else:
        redirect('Payment:final_factor')



def send_request(request, factor, amount, mobile, bank_port): 
    if request.user.is_authenticated :
        description = 'first_name:{}, last_name:{}'.format(factor.FK_User.first_name, factor.FK_User.last_name)
        # set factor TotalPrice
        factor.TotalPrice = amount
        factor.save()
        if bank_port == 'pay_pec':
            pecOrder = PecOrder(AdditionalData=description, Originator=mobile, Amount=int(amount), FactorNumber=factor.FactorNumber)
            pecOrder.save()
            requestData = ClientSaleRequestData(LoginAccount=PIN, Amount=int(amount), OrderId=pecOrder.id, CallBackUrl=CallbackURL, AdditionalData=description, Originator=mobile)
            result = saleService.service.SalePaymentRequest(requestData)
            pecOrder.Message = result['Message']
            pecOrder.Token = result['Token']
            pecOrder.Status = result['Status']
            pecOrder.save()
            if result['Status'] == 0:
                return redirect('https://pec.shaparak.ir/NewIPG/?token={}'.format(result['Token']))
            else:
                return HttpResponse(result['Message'])
        elif bank_port == 'pay_zarin':
            result = client.service.PaymentRequest(MERCHANT, amount, description, email, mobile, CallbackURL)
            if result.Status == 100:
                return redirect('https://www.zarinpal.com/pg/StartPay/' + str(result.Authority))
            else:
                return HttpResponse('Error code: ' + str(result.Status))
        else:
            return HttpResponse('با عرض پوزش.\n شیوه پرداخت مورد نظر تعریف نشده است.')
        
    else:

        return redirect("nakhll_market:AccountLogin")


def reverseTransaction(PIN, Token, OrderId):
    requestData = ClientReversalRequestData(LoginAccount=PIN, Token=Token)
    res = reverseService.service.ReversalRequest(requestData)
    try:
        PecReverse.objects.create(
            Status=res['Status'], 
            Token=res['Token'],
            Message=res['Massage'],
            OrderId=OrderId
            )
    except:
        print('exception in saving new PecReverse Token:{}'.format(res['Token']))
    return res

@csrf_exempt
def verify(request):
    # Get User Info
    if request.META['HTTP_ORIGIN'].startswith('https://pec.shaparak.ir') and request.META['HTTP_REFERER'].startswith('https://pec.shaparak.ir'):
        # this request is from pec
        Token = request.POST.get('Token')
        OrderId = request.POST.get('OrderId')
        TerminalNo = request.POST.get('TerminalNo')
        RRN = request.POST.get('RRN')
        status = request.POST.get('status')
        HashCardNumber = request.POST.get('HashCardNumber')
        Amount = request.POST.get('Amount').replace(',','')
        DiscountedAmount = request.POST.get('SwAmount').replace(',','')
        STraceNo = request.POST.get('STraceNo')
        try:
            PecTransaction.objects.create(
                                    Token=Token,
                                    OrderId=OrderId, 
                                    TerminalNo=TerminalNo, 
                                    RRN=RRN, 
                                    status=status,
                                    HashCardNumber=HashCardNumber,
                                    Amount=Amount,
                                    DiscountedAmount=DiscountedAmount,
                                    STraceNo=STraceNo
                                    )
        except:
            print('PecTransaction can not save. OrderId:{}, Token:{}'.format(OrderId, Token))
        try:
            pecOrder = PecOrder.objects.get(pk=OrderId)
        except:
            return HttpResponse('شماره درخواست تراکنش موجود نمی باشد.\nشماره تراکنش:{}'.format(OrderId))
        try:
            factor = Factor.objects.get(FactorNumber=pecOrder.FactorNumber)
        except:
            return HttpResponse('فاکتور درخواست مورد نظر موجود نمی باشد.\nشماره فاکتور:{}'.format(pecOrder.FactorNumber))
        user = factor.FK_User
        request.user = user
        this_profile = get_object_or_404(Profile, FK_User = user)
        this_inverntory = get_object_or_404(Wallet, FK_User = user).Inverntory
        # Get Menu Item
        options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
        # Get Nav Bar Menu Item
        navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
        # --------------------------------------------------------------------
        attrpricelist = AttrPrice.objects.all()
        try:
            transaction=Transaction.objects.filter(FK_User = user)
        except:
            transaction=None
        try:
            factor=Factor.objects.get(FK_User = user, PaymentStatus=False)
        except:
            factor=None
            return HttpResponse('خطای پرداخت تراکنش با پشتیبانی تماس بگیرید. وجه مورد نظر به حساب تان برگشت داده شده است.')

        message=""
        if int(status) == 0 and float(RRN) > 0 and int(factor.TotalPrice) == int(Amount):
            # transaction is correct
            requestData = ClientConfirmRequestData(LoginAccount=PIN, Token=Token)
            result = confirmService.service.ConfirmPayment(requestData)
            try:
                PecConfirmation.objects.create(
                    Status=result['Status'], 
                    CardNumberMasked=result['CardNumberMasked'],
                    Token=result['Token'],
                    RRN=result['RRN'],
                    OrderId=OrderId
                )
            except:
                print('PecConfirmation can not save! Token: {}, OrderId:{}'.format(Token, OrderId))

            if result['Status'] == 0:
                # transaction confirmed correctly
                try:
                    factor = Factor.objects.get(FK_User = user, PaymentStatus = False)
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

                        factor.OrderDate = datetime.datetime.today()
                        factor.save()
                    except:
                        getCoupon: None
                        factor.OrderDate = datetime.datetime.today()
                        factor.save()

                    # ------- Remove FactorPost AttrPrice -------
                    Factor_res = ''
                    for factpost in factor.FK_FactorPost.all():
                        factpost.EndPrice = factpost.get_total_item_price()
                        print(factpost.get_total_item_price())
                        factpost.save()
                        for item in factpost.FK_AttrPrice.all():
                            Factor_res += Factor_res + ' قیمت ویژگی : ' + item.Value +' | '+ item.Unit + ' | ' + 'با مبلغ اضافه '+ item.ExtraPrice + ' ### \n'
                        Factor_res += 'ابعاد محصول '+ factpost.FK_Product.Title + factpost.FK_Product.Length_With_Packaging +' * '+ factpost.FK_Product.Width_With_Packaging +' * '+ factpost.FK_Product.Height_With_Packaging +'\n وزن خالص :'+ factpost.FK_Product.Net_Weight +' - وزن با بسته بندی :'+ factpost.FK_Product.Weight_With_Packing
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
                    alert = Alert.objects.create(Part = '12', FK_User = user, Slug = factor.ID)
                    des_trans=' پرداخت برای فاکتور '+factor.FactorNumber
                    pricefactori = factor.get_end_price()
                    transaction = Transaction.objects.create(FK_User = user, Price = pricefactori, Type = '2', Description = des_trans)
                    message = 'تراکنش موفق .\nشماره پیگیری: ' + str(result['RRN'])
                except:
                    # transaction is correct and confirmed but factor is not build correctly
                    try: 
                        response = reverseTransaction(PIN, Token, OrderId)
                        message = 'تراکنش موفق نبوده و مبلغ کسر شده به حساب شما برگشت داده شده است. لطفا با پشتیبانی تماس حاصل فرمایید.'
                    except:
                        response = {'Status': 'FAIL'}
                        message = 'تراکنش موفق بوده و لیکن فاکتور صادر نشده است. برای دریافت وجه پرداختی با پشتیبانی تماس حاصل فرمایید.'

                    message =  '\nشماره پیگیری:{}' + str(result['RRN']) 
            else:
                # transaction can not confirmed
                try:
                    response = reverseTransaction(PIN, Token, OrderId)
                except:
                    response = {'Status': 'FAIL'}
                message = 'تراکنش ناموفق .\nوضعیت خرید: {}. وضعیت برگشت:{}'.format(result['Status'], response['Status']) 
        else:
            message = 'تراکنش ناموفق یا توسط شما لغو گردید. وجه مورد نظر به حساب تان برگشت داده شده است. \n کد خطا:{}'.format(status)
        
        context = {
            'This_User_Profile':this_profile,
            'This_User_Inverntory': this_inverntory,
            'Options': options,
            'MenuList':navbar,
            'Transaction':transaction,
            'Messege':message,
            'Attrpricelist':attrpricelist,
        }
        return render(request, 'nakhll_market/pages/successful.html', context)

    else:
        # zarin pal
        this_profile = get_object_or_404(Profile, FK_User = request.user)
        this_inverntory = get_object_or_404(Wallet, FK_User = request.user).Inverntory
        # 
        # this_profile = Profile.objects.get(FK_User=request.user)
        # this_inverntory = request.user.WalletManager.Inverntory
        # Get Menu Item
        options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
        # Get Nav Bar Menu Item
        navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
        # --------------------------------------------------------------------
        attrpricelist = AttrPrice.objects.all()
        try:
            transaction=Transaction.objects.filter(FK_User = request.user)
        except:
            transaction=None
        try:
            factor=Factor.objects.get(FK_User = request.user, PaymentStatus=False)
        except:
            factor=None
            return HttpResponse('خطای پرداخت تراکنش با پشتیبانی تماس بگیرید')

        message=""
        if request.GET.get('Status') == 'OK':
            # TODO it will make Exception because amount is not defined and is not GLOBAL
            result = client.service.PaymentVerification(MERCHANT, request.GET['Authority'], amount)
            if result.Status == 100:
                try:
                    factor = Factor.objects.get(FK_User = request.user, PaymentStatus = False)
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

                        factor.OrderDate = datetime.datetime.today()
                        factor.save()
                    except:
                        getCoupon: None
                        factor.OrderDate = datetime.datetime.today()
                        factor.save()

                    # ------- Remove FactorPost AttrPrice -------
                    Factor_res = ''
                    for factpost in factor.FK_FactorPost.all():
                        factpost.EndPrice = factpost.get_total_item_price()
                        print(factpost.get_total_item_price())
                        factpost.save()
                        for item in factpost.FK_AttrPrice.all():
                            Factor_res += Factor_res + ' قیمت ویژگی : ' + item.Value +' | '+ item.Unit + ' | ' + 'با مبلغ اضافه '+ item.ExtraPrice + ' ### \n'
                        Factor_res += 'ابعاد محصول '+ factpost.FK_Product.Title + factpost.FK_Product.Length_With_Packaging +' * '+ factpost.FK_Product.Width_With_Packaging +' * '+ factpost.FK_Product.Height_With_Packaging +'\n وزن خالص :'+ factpost.FK_Product.Net_Weight +' - وزن با بسته بندی :'+ factpost.FK_Product.Weight_With_Packing
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
                    des_trans=' پرداخت برای فاکتور '+factor.FactorNumber
                    pricefactori = factor.get_end_price()
                    transaction = Transaction.objects.create(FK_User = request.user, Price = pricefactori, Type = '2', Description = des_trans)
                    message = 'تراکنش موفق .\nشماره پیگیری: ' + str(result.RefID)
                except:
                    message = 'تراکنش موفق .\nشماره پیگیری: ' + str(result.RefID)+'\n خطای سبد خرید، با شماره پیگیری خود به پشتیبانی مراجعه کنید'
            elif result.Status == 101:
                message ='تراکنش ارسال شد : ' + str(result.Status)
            else:
                message = 'تراکنش ناموفق .\nوضعیت: ' + str(result.Status) 
        else:
            message = 'تراکنش ناموفق یا توسط شما لغو گردید'
        
        context = {
            'This_User_Profile':this_profile,
            'This_User_Inverntory': this_inverntory,
            'Options': options,
            'MenuList':navbar,
            'Transaction':transaction,
            'Messege':message,
            'Attrpricelist':attrpricelist,
        }
        return render(request, 'nakhll_market/pages/successful.html', context)


def add_to_cart(request ,ID):
    if request.user.is_authenticated :
        item = get_object_or_404(Product, ID = ID)
        if (item.Status != '4') and (item.Inventory != 0):
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
                    return redirect("Payment:cartdetail")
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
                    return redirect("Payment:cartdetail")
            else:
                order = Factor.objects.create(FK_User = request.user, PaymentStatus = False)
                Factor_item = FactorPost(FK_Product = item, FK_User = request.user)
                Factor_item.save()

                order.FK_FactorPost.add(Factor_item)
                order.save()

                return redirect("Payment:cartdetail")
        else:
            return redirect('nakhll_market:Re_ProductsDetail',
                shop_slug = item.FK_Shop.Slug,
                product_slug = item.Slug,
                status = True,
                msg = 'محصول مدنظر شما در حال حاضر موجود نمی باشد!')   
    else:
       return redirect("nakhll_market:AccountLogin")



def remove_from_cart(request, ID):
    if request.user.is_authenticated :
        FactorPost_Item = get_object_or_404(FactorPost, ID = ID)
        Factor_qs = Factor.objects.filter(FK_User = request.user, PaymentStatus = False)
        if Factor_qs.exists():
            order = Factor_qs[0]
            # check if the order item is in the order
            if order.FK_FactorPost.filter(ID = ID).exists():   
                for item in FactorPost_Item.FK_AttrPrice.all():
                        FactorPost_Item.FK_AttrPrice.remove(item)
                order.FK_FactorPost.remove(FactorPost_Item)
                FactorPost_Item.delete()
                # Chech Coupon
                if order.FK_Coupon != None:
                    if order.get_total_coupon_test(order.FK_Coupon.id) < int(order.FK_Coupon.MinimumAmount):
                        order.FK_Coupon = None
                        order.save()
                return redirect("Payment:cartdetail")
            else:
                return redirect("Payment:cartdetail")
        else:
            return redirect("Payment:cartdetail")
    else:
       return redirect("nakhll_market:AccountLogin")

def remove_single_item_from_cart(request, ID):
    if request.user.is_authenticated:
        FactorPost_Item = get_object_or_404(FactorPost, ID = ID)
        Factor_qs = Factor.objects.filter(FK_User = request.user, PaymentStatus = False)
        if Factor_qs.exists():
            order = Factor_qs[0]
            # Check Factor Item
            if order.FK_FactorPost.filter(ID = ID).exists():
                if FactorPost_Item.ProductCount > 1:
                    FactorPost_Item.ProductCount -= 1
                    FactorPost_Item.save()
                    # Chech Coupon
                    if order.FK_Coupon != None:
                        if order.get_total_coupon_test(order.FK_Coupon.id) < int(order.FK_Coupon.MinimumAmount):
                            order.FK_Coupon = None
                            order.save()
                    return redirect("Payment:cartdetail")
                else:
                    for item in FactorPost_Item.FK_AttrPrice.all():                   
                            FactorPost_Item.FK_AttrPrice.remove(item)
                    order.FK_FactorPost.remove(FactorPost_Item)
                    FactorPost_Item.delete()
                    # Chech Coupon
                    if order.FK_Coupon != None:
                        if order.get_total_coupon_test(order.FK_Coupon.id) < int(order.FK_Coupon.MinimumAmount):
                            order.FK_Coupon = None
                            order.save()
                    
                    return redirect("Payment:cartdetail")
            else:
                return redirect("Payment:cartdetail")
        else:
            return redirect("Payment:cartdetail")
    else:
        return redirect("nakhll_market:AccountLogin")



def add_single_item_from_cart(request, ID):
    if request.user.is_authenticated :
        FactorPost_Item = get_object_or_404(FactorPost, ID = ID)
        if (FactorPost_Item.FK_Product.Status != '4') and (int(FactorPost_Item.FK_Product.Inventory) > int(FactorPost_Item.ProductCount) ):
            Factor_qs = Factor.objects.filter(FK_User = request.user, PaymentStatus = False)
            if Factor_qs.exists():
                order = Factor_qs[0]
                # check if the order item is in the order
                if order.FK_FactorPost.filter(ID = ID).exists():  
                    FactorPost_Item.ProductCount += 1
                    FactorPost_Item.save()
                    # Chech Coupon
                    if order.FK_Coupon != None:
                        if (int(order.FK_Coupon.MaximumAmount) != 0) and (order.get_total_coupon_test(order.FK_Coupon.id) > int(order.FK_Coupon.MaximumAmount)):
                            order.FK_Coupon = None
                            order.save()
                    return redirect("Payment:cartdetail")
                else:
                    return redirect("Payment:cartdetail")
            else:
                return redirect("Payment:cartdetail")
        else:
            return redirect("Payment:cartdetail")
    else:
       return redirect("nakhll_market:AccountLogin")




    
# unsuccessful Page
def unsuccessful(request):
    # Get User Info
    
    this_profile = Profile.objects.get(FK_User=request.user)
    this_inverntory = request.user.WalletManager.Inverntory
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
    }

    return render(request, 'nakhll_market/pages/unsuccessful.html', context)




# Add Product To Cart With Attribute Price Page
def AddProductToCartWithAttrPrice(request, ID):
    # Check User Status
    if request.user.is_authenticated :
        if request.method == 'POST':
            # Get This Product
            this_product = get_object_or_404(Product, ID = ID)
            if (this_product.Status != '4') and (this_product.Inventory != 0):
                # Get All Attribute Price
                attrpricelist = request.POST.getlist("attrpriceitem")
                price_attribute_list = []
                # Add To List
                for item in attrpricelist:
                    if AttrPrice.objects.filter(id = item).exists():
                        price_attribute_list.append(AttrPrice.objects.get(id = item))
                
                if Factor.objects.filter(FK_User = request.user, PaymentStatus = False).exists():
                    this_order = Factor.objects.filter(FK_User = request.user, PaymentStatus = False)[0]
                    # Check Order Item
                    if this_order.FK_FactorPost.filter(FK_Product = this_product, FK_User = request.user).exists():
                        this_order_items = this_order.FK_FactorPost.filter(FK_Product = this_product, FK_User = request.user)
                        # Check Price Attribute
                        if len(price_attribute_list) == 0:
                            if this_order_items.filter(FK_AttrPrice = None).exists():
                                this_item = this_order_items.get(FK_AttrPrice = None)
                                this_item.ProductCount += 1
                                this_item.save() 
                            else:
                                this_item = FactorPost.objects.create(FK_Product = this_product, FK_User = request.user)
                                this_order.FK_FactorPost.add(this_item)
                        else:
                            for item in price_attribute_list:
                                this_order_items = this_order_items.filter(FK_AttrPrice__id = item.id)
                            this_item = None
                            for item in this_order_items:
                                if item.FK_AttrPrice.all().count() == len(attrpricelist):
                                    this_item = item
                            if (len(this_order_items) != 0) and (this_item != None):
                                this_item.ProductCount += 1
                                this_item.save()
                            else:
                                this_item = FactorPost.objects.create(FK_Product = this_product, FK_User = request.user)
                                for item in attrpricelist:
                                    if AttrPrice.objects.filter(id = item).exists():
                                        this_item.FK_AttrPrice.add(item)
                                this_order.FK_FactorPost.add(this_item)
                        # Chech Coupon
                        if this_order.FK_Coupon != None:
                            if (int(this_order.FK_Coupon.MaximumAmount) != 0) and (this_order.get_total_coupon_test(this_order.FK_Coupon.id) > int(this_order.FK_Coupon.MaximumAmount)):
                                this_order.FK_Coupon = None
                                this_order.save()
                        return redirect("Payment:cartdetail")
                    else:
                        this_item = FactorPost.objects.create(FK_Product = this_product, FK_User = request.user)

                        for item in attrpricelist:
                            if AttrPrice.objects.filter(id = item).exists():
                                this_item.FK_AttrPrice.add(item)
                        this_order.FK_FactorPost.add(this_item)
                        # Chech Coupon
                        if this_order.FK_Coupon != None:
                            if (int(this_order.FK_Coupon.MaximumAmount) != 0) and (this_order.get_total_coupon_test(this_order.FK_Coupon.id) > int(this_order.FK_Coupon.MaximumAmount)):
                                this_order.FK_Coupon = None
                                this_order.save()
                        return redirect("Payment:cartdetail")
                else:
                    this_order = Factor.objects.create(FK_User = request.user, PaymentStatus = False)
                    this_item = FactorPost.objects.create(FK_Product = this_product, FK_User = request.user)

                    for item in attrpricelist:
                        if AttrPrice.objects.filter(id = item).exists():
                            this_item.FK_AttrPrice.add(item)
                    this_order.FK_FactorPost.add(this_item)
                    # Chech Coupon
                    if this_order.FK_Coupon != None:
                        if (int(this_order.FK_Coupon.MaximumAmount) != 0) and (this_order.get_total_coupon_test(this_order.FK_Coupon.id) > int(this_order.FK_Coupon.MaximumAmount)):
                            this_order.FK_Coupon = None
                            this_order.save()
                    return redirect("Payment:cartdetail")
            else:
                return redirect('nakhll_market:Re_ProductsDetail',
                shop_slug = this_product.FK_Shop.Slug,
                product_slug = this_product.Slug,
                status = True,
                msg = 'محصول مدنظر شما در حال حاضر موجود نمی باشد!')
    else:
       return redirect("nakhll_market:AccountLogin")



def accept_factor_product(request, ID):
    if request.user.is_authenticated:
        # get this factor
        this_factor = get_object_or_404(Factor, ID = ID)
        # user`s item in this factor
        user_item = []
        for item in this_factor.FK_FactorPost.all():
            if item.FK_Product.FK_Shop.FK_ShopManager == request.user:
                user_item.append(item)
        user_item = list(dict.fromkeys(user_item))
        # change user`s item factor status
        for item in user_item:
            item.ProductStatus = '2'
            item.save()
        # get this factor status
        this_factor_status = True
        for item in this_factor.FK_FactorPost.all():
            if (item.ProductStatus != '0') and (item.ProductStatus != '2'):
                this_factor_status = False
        # change this factor status
        if this_factor_status:
            this_factor.OrderStatus = '2'
            this_factor.save()
        # Set Alert
        if Alert.objects.filter(Part = '20', FK_User = request.user, Slug = ID).exists():
            return redirect("Profile:Factor")
        else:
            Alert.objects.create(Part = '20', FK_User = request.user, Slug = ID)
        return redirect("Profile:Factor")
    else:
        return redirect("nakhll_market:AccountLogin")



def cansel_factor_product (request, ID):
    if request.user.is_authenticated :    
        # get this factor
        this_factor = get_object_or_404(Factor, ID = ID)
        # user`s item in this factor
        user_item = []
        for item in this_factor.FK_FactorPost.all():
            if item.FK_Product.FK_Shop.FK_ShopManager == request.user:
                user_item.append(item)
        user_item = list(dict.fromkeys(user_item))
        # change user`s item factor status
        for item in user_item:
            item.ProductStatus = '0'
            if item.FK_Product.Status == '1':
                item.FK_Product.Inventory += item.ProductCount
                item.FK_Product.save()
            item.save()
        # get this factor status
        this_factor_status = True
        for item in this_factor.FK_FactorPost.all():
            if item.ProductStatus != '0':
                this_factor_status = False
        # change factor status
        if this_factor_status:
            this_factor.OrderStatus = '4'
            this_factor.save()
        # set alert
        if Alert.objects.filter(Part = '13', FK_User = request.user, Slug = this_factor.ID, Seen = False).exists():
            return redirect("Profile:Factor")
        else:
            Alert.objects.create(Part = '13', FK_User = request.user, Slug = this_factor.ID)
        return redirect("Profile:Factor")
    else:
        return redirect("nakhll_market:AccountLogin")


# Show Send Info For User
def send_factor(request, ID, status = None, msg = None):
    if request.user.is_authenticated:
        if request.method == 'POST':
            # get data
            try:
                Barcode_Send = request.POST["Post_Barcode"]
            except:
              Barcode_Send = None
            try:
                Price_Send = request.POST["Post_Price"]
            except:
                Price_Send = None
            try:
                User_Send = request.POST["Post_UserSend"]
            except:
                User_Send = None
            try:
                Post_Send_Type = request.POST["Post_SendType"]
            except:
                Post_Send_Type = None
            try:
                Post_Send_Date = request.POST["Post_SendDate"]
            except:
                Post_Send_Date = None
            try:
                Post_Document = request.FILES["Post_Image"]
            except MultiValueDictKeyError:
                Post_Document = None
            Factor_Product = request.POST.getlist("Products")
            # convert date
            this_date = Post_Send_Date.split('-')
            Jthis_date = jdatetime.date(int(this_date[0]), int(this_date[1]), int(this_date[2]))
            Gthis_date = jdatetime.JalaliToGregorian(Jthis_date.year, Jthis_date.month, Jthis_date.day)
            finaldate = "%d-%d-%d" % (Gthis_date.gyear, Gthis_date.gmonth, Gthis_date.gday)
            if ((Barcode_Send != None) and (Barcode_Send != '')) and ((Price_Send != None) and (Price_Send != '')) and ((User_Send != None) and (User_Send != '')) and ((Post_Send_Type != None) and (Post_Send_Type != '')) and ((Post_Send_Date != None) and (Post_Send_Date != '')) and (len(Factor_Product) != 0):
                # chack and set data
                if not PostBarCode.objects.filter(FK_Factor = get_object_or_404(Factor, ID = ID), User_Sender = User_Send, PostPrice = Price_Send, BarCode = Barcode_Send, SendDate = finaldate, SendType = Post_Send_Type).exists():
                    # create new barcode
                    barcode = PostBarCode.objects.create(FK_Factor = get_object_or_404(Factor, ID = ID), User_Sender = User_Send, PostPrice = Price_Send, BarCode = Barcode_Send, SendDate = finaldate, SendType = Post_Send_Type)
                    # add image
                    if (Post_Document != None) and (Post_Document != ''):
                        barcode.Image = Post_Document
                        barcode.save()
                    # add product to barcode
                    for item in Factor_Product:
                        if Product.objects.filter(ID = item).exists():
                            barcode.FK_Products.add(Product.objects.get(ID = item))
                    # set alert
                    if Alert.objects.filter(Part = '21', FK_User = request.user, Slug = barcode.id).exists():
                        return redirect('nakhll_market:Factor')
                    else:
                        Alert.objects.create(Part = '21', FK_User = request.user, Slug = barcode.id)
                else:
                    return redirect('Payment:re_send_factor',
                    ID = ID,
                    status = True,
                    msg = 'شما قبلا برای این سفارش اطلاعات ارسال را کامل نمودید!')

                return redirect('nakhll_market:Factor')
            else:
                return redirect('Payment:re_send_factor',
                ID = ID,
                status = True,
                msg = 'فیلد های یارکد پستی، هزینه ارسال، نام ارسال کننده، نوع ارسال، تاریخ ارسال و وارد کردن محصولات ارسال شده اجباری می با شد!')
        else:
            this_profile = Profile.objects.get(FK_User=request.user)
            this_inverntory = request.user.WalletManager.Inverntory
            # Get Menu Item
            options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
            # Get Nav Bar Menu Item
            navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
            # ------------------------------------------------------------------------
            # get this factor
            factor = get_object_or_404(Factor, ID = ID)
            # get user`s products
            userallproducts = []
            for item in factor.FK_FactorPost.all():
                if item.FK_Product.FK_Shop.FK_ShopManager == request.user:
                    userallproducts.append(item.FK_Product)
            # get start day for calender
            day_past = jdatetime.timedelta(days = 30)
            start_day = jdatetime.date.today() - day_past
            start_day = "%d/%d/%d" % (start_day.year, start_day.month, start_day.day)
            # value
            message = None
            show = False
            if status != None:
                if str(status):
                   message = msg
                   show = True  
    
            context = {
                'This_User_Profile':this_profile,
                'This_User_Inverntory': this_inverntory,
                'Options': options,
                'MenuList':navbar,
                'Factor_Product':userallproducts,
                'Factor':factor,
                'Start_Day':start_day,
                'ShowAlart':show,
                'AlartMessage':message,
            }

            return render(request, 'nakhll_market/profile/pages/sendfactor.html', context)
    else:
        return redirect("nakhll_market:AccountLogin")


def delete_coupon(request,id):
    if request.user.is_authenticated:    
        # Get This Factor
        try:
            factor = Factor.objects.filter(FK_User_id = request.user, PaymentStatus = False)[0]
        except:
            factor = None
        # Delete Coupon
        if factor != None:
            factor.FK_Coupon = None
            factor.save()
        return redirect("Payment:Pay_Detail")
    else:
        return redirect("nakhll_market:AccountLogin")

# ---------------------------------------------------- Sell Statistics ---------------------------------------------------------------

def UserSellStatistic():
    # Get 4 Last Month Date
    Date_List = []
    # Build Date Class
    class Date:
        def __init__(self, start, end):
            self.Start = start
            self.End = end
    # Get Today Date
    today = jdatetime.date(1398,3,31)
    # Set Date
    this_month = today.month
    this_year = today.year
    # Day
    # Get First Date
    first_day = None
    # Get Second Date
    second_day = None
    # Get Third Date
    third_day = None
    # Get Fourth Date
    fourth_day = None

    if today.month <= 3:
        # Get First Date
        first_day = Date("%d-%d-%d" % (today.year, this_month, 1), "%d-%d-%d" % (today.year, this_month, 31))
        print(today.month)
        if today.month == 1:
            # Get Second Date
            second_day = Date("%d-%d-%d" % (this_year - 1, 12, 1), "%d-%d-%d" % (this_year - 1, 12, 30))
            # Get Third Date
            third_day = Date("%d-%d-%d" % (this_year - 1, 11, 1), "%d-%d-%d" % (this_year - 1, 11, 30))
            # Get Fourth Date
            fourth_day = Date("%d-%d-%d" % (this_year - 1, 10, 1), "%d-%d-%d" % (this_year - 1, 10, 30))
        elif today.month == 2:
            # Get Second Date
            second_day = Date("%d-%d-%d" % (this_year, this_month - 1, 1), "%d-%d-%d" % (this_year, this_month - 1, 31))
            # Get Third Date
            third_day = Date("%d-%d-%d" % (this_year - 1, 12, 1), "%d-%d-%d" % (this_year - 1, 12, 30))
            # Get Fourth Date
            fourth_day = Date("%d-%d-%d" % (this_year - 1, 11, 1), "%d-%d-%d" % (this_year - 1, 11, 30))
        else:
            # Get Second Date
            second_day = Date("%d-%d-%d" % (this_year, this_month - 1, 1), "%d-%d-%d" % (this_year, this_month - 1, 31))
            # Get Third Date
            third_day = Date("%d-%d-%d" % (this_year, this_month - 2, 1), "%d-%d-%d" % (this_year, this_month - 2, 31))
            # Get Fourth Date
            fourth_day = Date("%d-%d-%d" % (this_year - 1, 12, 1), "%d-%d-%d" % (this_year - 1, 12, 30))

    else:
        
        if this_month > 6:
            # Get First Date
            first_day = Date("%d-%d-%d" % (today.year, this_month, 1), "%d-%d-%d" % (today.year, this_month, 30))
        else:
            # Get First Date
            first_day = Date("%d-%d-%d" % (today.year, this_month, 1), "%d-%d-%d" % (today.year, this_month, 31))
        if this_month - 1 > 6:
            # Get Second Date
            second_day = Date("%d-%d-%d" % (this_year, this_month - 1, 1), "%d-%d-%d" % (this_year, this_month - 1, 30))
        else:
            # Get Second Date
            second_day = Date("%d-%d-%d" % (this_year, this_month - 1, 1), "%d-%d-%d" % (this_year, this_month - 1, 31))
        if this_month - 2 > 6:
            # Get Third Date
            third_day = Date("%d-%d-%d" % (this_year, this_month - 2, 1), "%d-%d-%d" % (this_year, this_month - 2, 30))
        else: 
            # Get Third Date
            third_day = Date("%d-%d-%d" % (this_year, this_month - 2, 1), "%d-%d-%d" % (this_year, this_month - 2, 31))
        if this_month - 3 > 6:
            # Get Fourth Date
            fourth_day = Date("%d-%d-%d" % (this_year, this_month - 3, 1), "%d-%d-%d" % (this_year, this_month - 3, 30))
        else: 
            # Get Fourth Date
            fourth_day = Date("%d-%d-%d" % (this_year, this_month - 3, 1), "%d-%d-%d" % (this_year, this_month - 3, 31))

    # Add To List
    Date_List.append(first_day)
    Date_List.append(second_day)
    Date_List.append(third_day)
    Date_List.append(fourth_day)

    for item in Date_List:
        print(item.Start + ' - ' + item.End)
    

   


# ------------------------------------------------------------- End ------------------------------------------------------------------

# -----------------------------------------------------------  Wallet Sections ------------------------------------------------------

# Charging User Wallet

def send_request_wallet(request): 
    if request.user.is_authenticated:

        if request.method == 'POST':

            try:
                price = request.POST["wallet_price"]
            except:
                price = 0

            if price != 0:
                get_prise_list = price.split(',')
                convert_prise_to_int = ''
                for item in get_prise_list:
                    convert_prise_to_int +=item
                # Charging
                chargeprice = int(convert_prise_to_int)
                amounts = chargeprice / 10
                if amounts >= 1000:
                    # global amount
                    amount = amounts
                    # global description
                    description = ' شارژ کیف پول'+ request.user.first_name +' '+request.user.last_name +"("+request.user.username+ ")"   # Required
                    # global mobile
                    mobile = get_object_or_404(Profile, FK_User = request.user).MobileNumber
                    # global CallbackURL
                    CallbackURL = 'http://localhost:8000/cart/verify_wallet/'
                else:
                    return redirect("nakhll_market:Wallet")
                result = client.service.PaymentRequest(MERCHANT, amount, description, email, mobile, CallbackURL)
                if result.Status == 100:
                    return redirect('https://www.zarinpal.com/pg/StartPay/' + str(result.Authority))
                else:
                    return HttpResponse('Error code: ' + str(result.Status))
            else:
                return redirect("nakhll_market:Wallet")
    else:
        return redirect("nakhll_market:AccountLogin")



def verify_wallet(request):
    message = None
    status_pay = False

    if request.GET.get('Status') == 'OK':
        user_wallet = get_object_or_404(Wallet, FK_User = request.user)
        result = client.service.PaymentVerification(MERCHANT, request.GET['Authority'], amount)
        if result.Status == 100:
            try:
                des_trans = ' پرداخت برای شارژ کیف پول  '+ request.user.first_name + request.user.last_name + '('+ request.user.username + ')'
                # Charging Wallet
                user_wallet = Wallet.objects.get(FK_User = request.user)
                inverntory_wallet = int(user_wallet.Inverntory)
                Amount = int(amount)*10
                inverntory_wallet += int(Amount)
                user_wallet.Inverntory = str(inverntory_wallet)
                user_wallet.save()
                # Set Transaction
                Transaction.objects.create(FK_User = request.user, Price = amount, Type = '1', FK_Wallet = request.user , Description = des_trans)
                message = 'تراکنش موفق .\nشماره پیگیری: ' + str(result.RefID)
                status_pay = True
            except:
                message = 'تراکنش موفق .\nشماره پیگیری: ' + str(result.RefID)+'\n خطای سبد خرید، با شماره پیگیری خود به پشتیبانی مراجعه کنید'
                status_pay = True
        elif result.Status == 101:
            message ='تراکنش ارسال شد : ' + str(result.Status)
            status_pay = True
        else:
            message = 'تراکنش ناموفق .\nوضعیت: ' + str(result.Status) 
            status_pay = False
    else:
        message = 'تراکنش ناموفق یا توسط شما لغو گردید'
        status_pay = False
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
    
    context = {
            'This_User_Profile':this_profile,
            'This_User_Inverntory': this_inverntory,
            'Options': options,
            'MenuList':navbar,
            'Message':message,
            'Status':status_pay,
    }

    return render(request, 'nakhll_market/profile/pages/wallet.html', context)
