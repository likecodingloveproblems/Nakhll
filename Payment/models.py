from django.db import models
from django.contrib.auth.models import User
from nakhll_market.models import Shop, Product, AttrPrice, Category, Option_Meta, Profile
from django.utils.deconstruct import deconstructible
import uuid, random, string, os, time
from django_jalali.db import models as jmodels
from django.shortcuts import reverse
from datetime import datetime, date 
import jdatetime
import math

# Rename Method
@deconstructible
class PathAndRename():
    def __init__(self, sub_path):
        self.path = sub_path

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        rand_strings = ''.join( random.choice(string.ascii_letters+string.digits) for i in range(6))
        filename = '{}.{}'.format(rand_strings, ext)

        return os.path.join(self.path, filename)

# Random Copon Code        
@deconstructible
class BuildCoponCode():
    def __init__(self, Code_Size):
        self.size = Code_Size
        self.code = ''.join(random.choice(string.ascii_lowercase+string.digits) for i in range(self.size))

    def __call__(self):
        result_str = self.code

        return result_str

# Random Camping Code        
@deconstructible
class BuildCampingCode():
    def __init__(self, Code_Size):
        self.size = Code_Size
        self.code = ''.join(random.choice(string.ascii_lowercase+string.digits) for i in range(self.size))

    def __call__(self):
        result_str = '-'.join(['CP',self.code])

        return result_str

# # Random Factor Code        
# @deconstructible
# class BuildFactorCode():
#     def __init__(self, Code_Size):
#         self.size = Code_Size

#     def __call__(self):
#         random_str = ''.join( random.choice(string.ascii_lowercase + string.digits) for i in range(self.size))
#         return (random_str)

def check_factor_number(number):
    try:
        int(number)
        return True
    except:
        return False

# Random Factor Code        
@deconstructible
class BuildFactorCode():
    def __init__(self, Code_Size):
        self.size = Code_Size

    def __call__(self):
        start = '1'
        if Factor.objects.filter(FactorNumber = self.extend(start)).exists():
            i = 1
            last = Factor.objects.latest('OrderDate').FactorNumber
            if not check_factor_number(last):
                last = '1'
            while 1:
                value = self.extend(str(int(last) + i))
                if not Factor.objects.filter(FactorNumber = value).exists():
                    return value
                else:
                    i += 1
        else:
            return self.extend(start)

    def extend(self, value):
        count = self.size - len(value)
        if count == 0:
            return value
        else:
            result = ''
            while count > 0:
                result += '0'
                count -= 1
            result += value
            return result

#----------------------------------------------------------------------------------------------------------------------------------

# Wallet (کیف پول) Model 
class Wallet(models.Model):
    ID=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    FK_User=models.OneToOneField(User, on_delete=models.SET_NULL, verbose_name='صاحب کیف پول', related_name='WalletManager', null=True)
    Inverntory=models.CharField(verbose_name='موجودی کیف پول', max_length=15, default='0')
    CreditCard=models.CharField(verbose_name='موجودی کارت اعتباری', max_length=15, default='0')
    CREDITCARD_STATUS =(
        (True,'دارد'),
        (False,'ندارد'),
    )
    CreditCardStatus=models.BooleanField(verbose_name='وضعیت کارت اعتباری', choices=CREDITCARD_STATUS, default=False)

    # Output Customization Based On User
    def __str__(self):
        return "{}".format(self.FK_User)

    # Ordering With DateCreate
    class Meta:
        ordering = ('ID',)
        verbose_name = "کیف پول"
        verbose_name_plural = "کیف پول ها"

#----------------------------------------------------------------------------------------------------------------------------------

# Transaction (تراکنش) Model 
class Transaction(models.Model):
    ID=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    FK_Wallet=models.ForeignKey(Wallet, on_delete=models.SET_NULL, verbose_name='کیف پول', related_name='TransactionWallet', null=True)
    FK_User=models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='ثبت کننده', related_name='TransactionUser', null=True)
    Price=models.CharField(verbose_name='مبلغ', max_length=15)
    Description=models.TextField(verbose_name='توضیحات تراکنش', blank=True)
    Date=models.DateTimeField(verbose_name='تاریخ انجام تراکنش', auto_now_add=True)
    TYPE_STATUS =(
        ('1','شارژ کیف پول'),
        ('2','خرید آنلاین'),
        ('3','فروش'),
        ('4','مدیریت'),
        ('5','تسویه حساب'),
        ('6','خرید با کیف پول'),
        ('7','شارژ بن کارت'),
        ('8','خرید با بن کارت'),
    )
    Type=models.CharField(verbose_name='نوع عملیات', max_length=1, choices=TYPE_STATUS)

    def get_type(self):
        if self.Type == '1':
            return 'شارژ کیف پول'
        elif self.Type == '2':
            return 'خرید آنلاین'
        elif self.Type == '3':
            return 'فروش'
        elif self.Type == '4':
            return 'مدیریت'
        elif self.Type == '5':
            return 'تسویه حساب'
        elif self.Type == '6':
            return 'خرید با کیف پول'
        elif self.Type == '7':
            return 'شارژ بن کارت'
        elif self.Type == '8':
            return 'خرید با بن کارت'

    # Output Customization Based On Wallet
    def __str__(self):
        return "{}".format(self.FK_Wallet)

    # Ordering With DateCreate
    class Meta:
        ordering = ('Date',)
        verbose_name = "تراکنش"
        verbose_name_plural = "تراکنش ها"

#----------------------------------------------------------------------------------------------------------------------------------

# Installment (قسط) Model
class Installment(models.Model):
    Title=models.CharField(verbose_name='عنوان', max_length=100, db_index=True)
    Description=models.TextField(verbose_name='توضیحات', blank=True)
    FK_UserCreator=models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='سازنده', related_name='User_Creator', null=True)
    Company=models.CharField(verbose_name='میزان مشارکت بازار نخل', max_length=15)
    Entity=models.CharField(verbose_name='میزان مشارکت سازمان', max_length=15)
    FK_Receiver=models.ManyToManyField(User, verbose_name='گیرندگان اقساط', related_name='User_Installment', blank=True)
    FK_Product=models.ManyToManyField(Product, verbose_name='محصولات', related_name='Product_Installment', blank=True)
    FK_Shop=models.ManyToManyField(Shop, verbose_name='حجره ها', related_name='Shop_Installment', blank=True)
    StartDate=jmodels.jDateTimeField(verbose_name='تاریخ شروع خرید اقساطی')
    EndDate=jmodels.jDateTimeField(verbose_name='تاریخ پایان خرید اقساطی')
    AVAILABLE_STATUS =(
        (True,'فعال'),
        (False,'غیر فعال'),
    )
    PUBLISH_STATUS =(
        (True,'منتشر شده'),
        (False,'در انتظار تایید'),
    )
    Available=models.BooleanField(verbose_name='وضعیت ثبت خرید اقساطی', choices=AVAILABLE_STATUS, default=True)
    Publish=models.BooleanField(verbose_name='وضعیت انتشار خرید اقساطی', choices=PUBLISH_STATUS, default=False)
    FK_User=models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='تایید کننده', related_name='Installment_Accept', blank=True, null=True)
    
    # Output Customization Based On Title
    def __str__(self):
        return "{}".format(self.Title)

    # Ordering With DateCreate
    class Meta:
        ordering = ('id',)
        verbose_name = "قسط"
        verbose_name_plural = "اقساط" 

#----------------------------------------------------------------------------------------------------------------------------------

# Invitation (دعوت نامه) Model
class Invitation(models.Model):
    FK_Shop=models.ForeignKey(Shop, on_delete=models.SET_NULL, verbose_name='حجره', related_name='Shop_Invitation', null=True)
    Status=models.BooleanField(verbose_name='وضعیت درخواست', default=False)
    
    # Output Customization Based On Title
    def __str__(self):
        return "{} - {}".format(self.FK_Shop, self.Status)

    # Ordering With DateCreate
    class Meta:
        ordering = ('id',)
        verbose_name = "دعوت نامه"
        verbose_name_plural = "دعوت نامه ها"

#----------------------------------------------------------------------------------------------------------------------------------

# Campaign (کمپین) Model
class Campaign(models.Model):
    Title=models.CharField(verbose_name='عنوان', max_length=100, db_index=True)
    Description=models.TextField(verbose_name='توضیحات', blank=True)
    FK_Creator=models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='سازنده', related_name='Campaign_Creator', null=True)
    DISCOUNT_TYPE=(
        ('1','درصدی'),
        ('2','اعتباری'),
        ('3','ارسال رایگان'),
    )
    DiscountType=models.CharField(verbose_name='نوع تخفیف', max_length=1, choices=DISCOUNT_TYPE, default='1')
    DiscountRate=models.CharField(verbose_name='میزان تخفیف', max_length=7, blank=True)
    FK_InvitationShops=models.ManyToManyField('Invitation', verbose_name='حجره های دعوت شده', related_name='Campaign_Invitation_Shop', blank=True)
    FK_Shops=models.ManyToManyField(Shop, verbose_name='حجره های مجاز', related_name='ShopCampaign', blank=True)
    FK_Products=models.ManyToManyField(Product, verbose_name='محصولات مجاز', related_name='ProductCampaign', blank=True)
    FK_Categories=models.ManyToManyField(Category, verbose_name='دسته بندی های مجاز', related_name='CategoryCampaign', blank=True)
    CAMPAGIN_TYPE=(
        ('0','تولد'),
        ('1','مناسبتی'),
        ('2','انجمنی'),
        ('3','فروش اولی'),
        ('4','خرید اولی'),
    )
    CampaignType=models.CharField(verbose_name='نوع کمپین', max_length=1, choices=CAMPAGIN_TYPE)
    DISCOUNT_TYPE =(
        ('0','مدیریتی'),
        ('1','حجره ای'),
    )
    DiscountStatus=models.CharField(verbose_name='نوع تخفیف', max_length=1, choices=DISCOUNT_TYPE, blank=True)
    TextRequest=models.TextField(verbose_name='متن پیام دعوت نامه', blank=True)
    MinimumAmount=models.CharField(verbose_name='حداقل مبلغ خرید', max_length=15, blank=True, default='0')
    MaximumAmount=models.CharField(verbose_name='حداکثر مبلغ خرید', max_length=15, blank=True, default='0')
    StartDate=jmodels.jDateField(verbose_name='تاریخ شروع کمپین')
    EndDate=jmodels.jDateField(verbose_name='تاریخ پایان کمپین')
    AVAILABLE_STATUS =(
        (True,'فعال'),
        (False,'غیر فعال'),
    )
    PUBLISH_STATUS =(
        (True,'منتشر شده'),
        (False,'در انتظار تایید'),
    )
    Available=models.BooleanField(verbose_name='وضعیت ثبت کمپین', choices=AVAILABLE_STATUS, default=True)
    Publish=models.BooleanField(verbose_name='وضعیت انتشار کمپین', choices=PUBLISH_STATUS, default=False)
    FK_User=models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='تایید کننده', related_name='Campaign_Accept', blank=True, null=True)

    # Output Customization Based On Creator, Serial Number
    def __str__(self):
        return "{} ({})".format(self.Title, self.FK_Creator)

    # Ordering With StartDate
    class Meta:
        ordering = ('StartDate',)
        verbose_name = "کمپین"
        verbose_name_plural = "کمپین ها"
    
#----------------------------------------------------------------------------------------------------------------------------------

# Coupon (کوپن) Model
class Coupon(models.Model):
    Title=models.CharField(verbose_name='عنوان کوپن', max_length=100, db_index=True)
    Description=models.TextField(verbose_name='توضیحات', blank=True)
    FK_Creator=models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='سازنده کوپن', related_name='Coupon_Creator', null=True)
    SerialNumber=models.CharField(verbose_name='سریال کوپن', max_length=30, default=BuildCoponCode(8))
    StartDate=jmodels.jDateField(verbose_name='تاریخ ساخت کوپن')
    EndDate=jmodels.jDateField(verbose_name='تاریخ انقضا کوپن')
    DISCOUNT_TYPE=(
        ('1','درصدی'),
        ('2','اعتباری'),
    )
    DiscountType=models.CharField(verbose_name='نوع تخفیف', max_length=1, choices=DISCOUNT_TYPE, default='1')
    DiscountRate=models.CharField(verbose_name='میزان تخفیف', max_length=7)
    DISCOUNT_TYPE =(
        ('0','مدیریتی'),
        ('1','حجره ای'),
    )
    DiscountStatus=models.CharField(verbose_name='نوع نخفیف', max_length=1, choices=DISCOUNT_TYPE, blank=True)
    MinimumAmount=models.CharField(verbose_name='حداقل مبلغ خرید', max_length=15, blank=True, default='0')
    MaximumAmount=models.CharField(verbose_name='حداکثر مبلغ خرید', max_length=15, blank=True, default='0')
    NumberOfUse=models.PositiveSmallIntegerField(verbose_name='دفعات مجاز استفاده', default=1)
    TextRequest=models.TextField(verbose_name='متن پیام دعوت نامه', blank=True)
    FK_InvitationShops=models.ManyToManyField('Invitation', verbose_name='حجره های دعوت شده', related_name='Coupon_Invitation_Shop', blank=True)
    FK_Shops=models.ManyToManyField(Shop, verbose_name='حجره های مجاز', related_name='ShopCoupon', blank=True)
    FK_Products=models.ManyToManyField(Product, verbose_name='محصولات مجاز', related_name='ProductCoupon', blank=True) 
    FK_Categories=models.ManyToManyField(Category, verbose_name='دسته بندی های مجاز', related_name='CategoryCoupon', blank=True)  
    FK_Users=models.ManyToManyField(User, verbose_name='کاربران مجاز', related_name='UserCoupon', blank=True)
    PUBLISH_STATUS =(
        (True,'منتشر شده'),
        (False,'در انتظار تایید'),
    )
    AVAILABLE_STATUS =(
        (True,'فعال'),
        (False,'غیر فعال'),
    )
    Available=models.BooleanField(verbose_name='وضعیت ثبت کوپن', choices=AVAILABLE_STATUS, default=True)
    Publish=models.BooleanField(verbose_name='وضعیت انتشار کوپن', choices=PUBLISH_STATUS, default=False)
    FK_User=models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='تایید کننده', related_name='Coupon_Accept', blank=True, null=True) 
    Log=models.TextField(verbose_name='لاگ', blank=True)

    def __str__(self):
        return "{} ({})".format(self.FK_Creator, self.SerialNumber)

    def get_user_fullname(self):
        try:
            return self.FK_Creator.first_name + ' ' + self.FK_Creator.last_name
        except:
            return None

    def get_discount_status(self):
        Status = {
            "0" : 'مدیریتی',
            "1" : 'حجره ای',
        }
        return Status[self.DiscountStatus]

    def get_discount_type(self):
        Status = {
            "1" : 'درصدی',
            "2" : 'اعتباری',
        }
        return Status[self.DiscountType]

    # Ordering With DateCreate
    class Meta:
        ordering = ('id',)
        verbose_name = "کوپن"
        verbose_name_plural = "کوپن ها"

#----------------------------------------------------------------------------------------------------------------------------------

# FactorPost (محصولات فاکتور) Model
class FactorPost (models.Model):
    ID=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    FK_Product=models.ForeignKey(Product, on_delete=models.SET_NULL, verbose_name='محصول', related_name='Factor_Product', null=True)
    FK_User=models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='کاربر خریدار', related_name='item_Product', blank=True, null=True) 
    PRODUCT_STATUS=(
        ('0','لغو سفارش'),
        ('1','منتظر تایید حجره دار'),
        ('2','در حال آماده سازی'),
        ('3','ارسال شده'),
    )
    ProductStatus=models.CharField(verbose_name='وضعیت محصول', max_length=1, choices=PRODUCT_STATUS, default='1')
    ProductCount=models.PositiveIntegerField(verbose_name='تعداد محصول', default=1)
    FK_AttrPrice=models.ManyToManyField(AttrPrice, verbose_name='ویژگی های انتخابی', related_name='attrPrice_Factor', blank=True)
    Description=models.TextField(verbose_name='توضیحات', blank=True, null=True)
    EndPrice=models.CharField(verbose_name='قیمت نهایی', max_length=15, default=0)

    def __str__(self):
        return "{} - {}".format(self.ID, self.FK_Product)

    def get_status(self):
        Status = {
            "0" : 'لغو سفارش',
            "1" : 'منتظر تایید حجره دار',
            "2" : 'در حال آماده سازی',
            "3" : 'ارسال شده',
        }
        return Status[self.ProductStatus]

    def get_total_item_price(self):
        prodprice = int(self.FK_Product.Price)
        prodcount = self.ProductCount
        c = prodprice * prodcount
        c = c + self.get_item_attr_price()
        return c

    def get_item_attr_price(self):
        atrprice = 0
        if self.FK_AttrPrice.all() != None:
            for AttrPrice in self.FK_AttrPrice.all():
                atrprice = int(atrprice)
                atrprice += int(AttrPrice.ExtraPrice)
        return atrprice * int(self.ProductCount)
    
    def get_total_item_post_price(self):
        posttype = int(self.FK_Product.PostType)
        if posttype == 1:
            a = 100000 
            # if a >=2000000 :
            #     return 0
            # else:
            return a
        if posttype == 3:
            return 0
        if posttype == 2:
            b = int(self.FK_Product.PostPrice)
            if b>=2000000 :
                return 0
            else :
                return b
    
    def get_one_price(self):
        return int(int(self.EndPrice) / self.ProductCount)

    def get_total_old_item_price(self):
        return self.ProductCount * int(self.FK_Product.OldPrice)

    def get_total_product_weight_with_count(self):
        return self.FK_Product.get_total_product_weight() * self.ProductCount
    
    def get_caculate_post(self):
        try:
            # Get Costs Per Kg Added
            try:
                cost_add = int(Option_Meta.objects.get(Title = 'shipping_costs_per_kilogram_added').Value_1)
            except:
                cost_add = 20000
            post_price = 0
            total_weight = self.get_total_product_weight_with_count()
            if total_weight > 1000:
                total_weight -= 1000
                post_price += (math.ceil(total_weight / 1000) * cost_add)
            return post_price
        except:
            return 0
    
    # Ordering With DateCreate
    class Meta:
        ordering = ('ID',)
        verbose_name = "محصول فاکتور"
        verbose_name_plural = "محصول فاکتور ها"
        
#----------------------------------------------------------------------------------------------------------------------------------

# Factor (فاکتور) Model 
class Factor(models.Model):
    ID=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    FactorNumber=models.CharField(verbose_name='شماره فاکتور', max_length=10, unique=True, default=BuildFactorCode(10))
    FK_User=models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='صاحب فاکتور', related_name='UserFactor', null=True)
    Description=models.TextField(verbose_name='توضیحات سبد خرید',max_length=350, blank=True)
    CountrPreCode=models.CharField(verbose_name='کد کشور', max_length=6, default='098')
    MobileNumber=models.CharField(verbose_name='شماره موبایل', max_length=11, blank=True)
    ZipCode=models.CharField(verbose_name='کد پستی', max_length=10, blank=True)
    Address=models.CharField(verbose_name='آدرس', max_length=300, blank=True)
    Location=models.CharField(verbose_name='موقعیت مکانی', max_length=150, blank=True, help_text='طول و عرض جغرافیایی')
    FaxNumber=models.CharField(verbose_name='شماره فکس', max_length=8, blank=True)
    CityPerCode=models.CharField(verbose_name='پیش شماره', max_length=6, default='034')
    City=models.CharField(verbose_name='شهر', max_length=50, blank=True)
    BigCity=models.CharField(verbose_name='شهرستان', max_length=50, blank=True)
    State =models.CharField(verbose_name='استان', max_length=50, blank=True)
    PhoneNumber=models.CharField(verbose_name='شماره تلفن ثابت', max_length=8, blank=True)
    FK_FactorPost=models.ManyToManyField(FactorPost, verbose_name='محصولات فاکتور', related_name='Factor_Products', blank=True)
    FACTOR_TYPE=(
        ('1','فاکتور چاپی'),
        ('2','فاکتور الکترونیکی'),
    )
    FactorType=models.CharField(verbose_name='نحوه تحویل فاکتور', max_length=1, choices=FACTOR_TYPE, default='1')
    SHOPINFO_STATUS=(
        (True,'نمایش اطلاعات حجره'),
        (False,'عدم نمایش اطلاعات حجره'),
    )
    ShopInfo=models.BooleanField(verbose_name='وضعیت نمایش اطلاعات حجره', choices=SHOPINFO_STATUS, default=True)
    USERINFO_STATUS=(
        (True,'نمایش اطلاعات شخصی'),
        (False,'عدم نمایش اطلاعات شخصی'),
    )
    UserInfo=models.BooleanField(verbose_name='وضعیت نمایش اطلاعات شخصی کاربر', choices=USERINFO_STATUS, default=True)
    FK_Coupon=models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, verbose_name='کد تخفیف', blank=True)
    DiscountRate=models.PositiveIntegerField(verbose_name='میزان تخفیف', default=0)
    DISCOUNT_TYPE =(
        ('0','بدون کوپن'),
        ('1','مدیریتی'),
        ('2','حجره ای'),
    )
    DiscountType=models.CharField(verbose_name='نوع نخفیف', max_length=1, choices=DISCOUNT_TYPE, blank=True, default='0')
    FK_Campaign=models.ForeignKey(Campaign, on_delete=models.SET_NULL, null=True, verbose_name='کد کمپین', blank=True)
    CAMPAING_TYPE =(
        ('0','بدون کمپین'),
        ('1','تولد'),
        ('2','مناسبتی'),
        ('3','انجمنی'),
        ('4','فروش اولی'),
        ('5','خرید اولی'),
    )
    CampaingType=models.CharField(verbose_name='نوع کمپین', max_length=1, choices=CAMPAING_TYPE, blank=True, default='0')
    PostPrice=models.CharField(verbose_name='هزینه پست', max_length=15)
    TotalPrice=models.CharField(verbose_name='هزینه کل', max_length=15)
    PAYMENT_STATUS =(
        (True,'پرداخت شد'),
        (False,'پرداخت نشده'),
    )
    PaymentStatus=models.BooleanField(verbose_name='وضعیت پرداخت', choices=PAYMENT_STATUS, default=False)
    PAYMENT_TYPE =(
        ('0','پرداخت در محل'),
        ('1','پرداخت آنلاین'),
        ('2','پرداخت با کیف پول'),
        ('3','پرداخت با بن کارت'),
        ('4','پرداخت با آنلاین - کیف پول'),
        ('5','پرداخت با آنلاین - بن کارت'),
        ('6','پرداخت با کیف پول - بن کارت'),
     )
    PaymentType=models.CharField(verbose_name='نوع پرداخت', max_length=1, choices=PAYMENT_TYPE, default='1')
    OrderDate=models.DateTimeField(verbose_name='تاریخ خرید', auto_now_add=True)
    DeliveryDate=jmodels.jDateField(verbose_name='تاریخ تحویل', null=True, blank=True)
    ORDER_STATUS =(
        ('0','سفارش تحویل داده شده است'),
        ('1','سفارش آماده است'),
        ('2','سفارش در حال آماده سازی است'),
        ('3','منتظر بررسی'),
        ('4','سفارش لغو شده است'),
        ('5','سفارش ارسال شده است'),
    )
    OrderStatus=models.CharField(verbose_name='وضعیت سفارش', max_length=1, choices=ORDER_STATUS, default='3')
    CHECKOUT_STATUS =(
        (True,'تسویه شده'),
        (False,'تسویه نشده'),
    )
    Checkout=models.BooleanField(verbose_name='وضعیت تسویه حساب فاکتور', choices=CHECKOUT_STATUS, default=False)
    PUBLISH_STATUS =(
        (True,'منتشر شده'),
        (False,'در انتظار تایید'),
    )
    Publish=models.BooleanField(verbose_name='وضعیت انتشار فاکتور', choices=PUBLISH_STATUS, default=False)
    FK_Staff=models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='تایید کننده', related_name='Factor_Accept', blank=True, null=True)
    FK_Staff_Checkout=models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='تسویه کننده', related_name='Factor_Checkout', blank=True, null=True) 

    # Output Customization Based On User, ID
    def __str__(self):
        return "{} ({})".format(self.FK_User, self.FactorNumber)

    def get_factor_payment_type(self):
        if self.PaymentType == '0':
            return 'پرداخت در محل'
        elif self.PaymentType == '1':
            return 'پرداخت آنلاین'
        elif self.PaymentType == '2':
            return 'پرداخت با کیف پول'
        elif self.PaymentType == '3':
            return 'پرداخت با بن کارت'
        elif self.PaymentType == '4':
            return 'پرداخت با آنلاین - کیف پول'
        elif self.PaymentType == '5':
            return 'پرداخت با آنلاین - بن کارت'
        elif self.PaymentType == '6':
            return 'پرداخت با کیف پول - بن کارت'

    def get_factor_status(self):
        if self.PaymentType == '0':
            return 'سفارش تحویل داده شده است'
        elif self.PaymentType == '1':
            return 'سفارش آماده است'
        elif self.PaymentType == '2':
            return 'سفارش در حال آماده سازی است'
        elif self.PaymentType == '3':
            return 'منتظر بررسی'
        elif self.PaymentType == '4':
            return 'سفارش لغو شده است'
        elif self.PaymentType == '5':
            return 'سفارش ارسال شده است'

    def get_coupon_status(self):
        if self.DiscountType == '0':
            return 'بدون کوپن'
        elif self.DiscountType == '1':
            return 'مدیریتی'
        elif self.DiscountType == '2':
            return 'حجره ای'

    def accept_factor_product(self):
        return reverse("Payment:accept_factor_product", kwargs={
            'ID': self.ID
        })
    
    def send_factor_page(self):
        return reverse("Payment:send_factor_page", kwargs={
            'ID': self.ID
        })

    def cansel_factor_product(self):
        return reverse("Payment:cansel_factor_product", kwargs={
            'ID': self.ID
        })
    
    def Coupon_price_min(self):
        Coupon_price = 0
        if self.FK_Coupon != None :
            if self.FK_Coupon.DiscountType == '1':
                #darsadi
                cp = int(Coupon.objects.get(id = self.FK_Coupon.id).DiscountRate)
                xdcp = self.get_total_coupon() * cp / 100
                return int(xdcp)
            elif self.FK_Coupon.DiscountType == '2':
                if self.get_total_coupon() <= int(self.FK_Coupon.DiscountRate):
                    return self.get_total_coupon()
                else:
                    return int(self.FK_Coupon.DiscountRate)
                    
        else:
            return int(Coupon_price)

    def get_total_coupon (self):
        Coupon_price = 0
        if self.FK_Coupon != None :
            # Get Coupon
            copun = Coupon.objects.get(id = self.FK_Coupon.id)
            # Coupon Producs List
            Product_List = []
            # Total Price
            Total = 0
            if (copun.FK_Shops.all()) or (copun.FK_Products.all()):
                if copun.FK_Shops.all():
                    for item in copun.FK_Shops.all():
                        Product_List += list(Product.objects.filter(Publish = True, FK_Shop = item, Available = True))
                if copun.FK_Products.all():
                    Product_List += list(copun.FK_Products.all())
                Product_List = list(dict.fromkeys(Product_List))
                for item in self.FK_FactorPost.filter(FK_Product__in = Product_List):
                    Total += item.get_total_item_price()
            else:
                for item in self.FK_FactorPost.all():
                    Total += item.get_total_item_price()
            return Total
        else:
            return int(Coupon_price)

    def get_total_coupon_test(self, id):
        # Get Coupon
        copun = Coupon.objects.get(id = id)
        # Coupon Producs List
        Product_List = []
        # Total Price
        Total = 0

        if (copun.FK_Shops.all().count() != 0) or (copun.FK_Products.all().count() != 0):
            if copun.FK_Shops.all():
                for item in copun.FK_Shops.all():
                    Product_List += list(Product.objects.filter(Publish = True, FK_Shop = item, Available = True))
            if copun.FK_Products.all():
                Product_List += list(copun.FK_Products.all())
            Product_List = list(dict.fromkeys(Product_List))
            for item in self.FK_FactorPost.filter(FK_Product__in = Product_List):
                Total += item.get_total_item_price()
        else:
            for item in self.FK_FactorPost.all():
                Total += item.get_total_item_price()
        return Total

    def get_total_user(self, user):
        total = 0
        for FactorPost in self.FK_FactorPost.all():
            if FactorPost.FK_Product.FK_Shop.FK_Shop.FK_ShopManager == user:
                a = FactorPost.get_total_item_price()
                total += a
        return total

    def get_total_user_factor_item(self, user_id):
        total = 0
        this_user = User.objects.get(id = user_id)
        for item in self.FK_FactorPost.all():
            if item.FK_Product.FK_Shop.FK_ShopManager == this_user:
                total += item.get_total_item_price()
        return total

    def get_total(self):
        total = 0
        for FactorPost in self.FK_FactorPost.all():
            a = FactorPost.get_total_item_price()
            total += a
        return total

    def get_total_end(self):
        total = 0
        for FactorPost in self.FK_FactorPost.all():
            a = int(FactorPost.EndPrice)
            total += a
        return total

    def get_cost_within_the_city(self):
        try:
            return int(Option_Meta.objects.get(Title = 'shipping_cost_within_the_city').Value_1)
        except:
            return 80000
        
    def get_fixed_shipping_costs(self):
        try:
            return int(Option_Meta.objects.get(Title = 'shipping_costs_per_room').Value_1)
        except:
            return 120000

    def check_coupon_products(self):
        # get coupon product
        Product_List = []
        if self.FK_Coupon.FK_Shops.all():
            for item in self.FK_Coupon.FK_Shops.all():
                Product_List += list(Product.objects.filter(Publish = True, FK_Shop = item, Available = True))
        if self.FK_Coupon.FK_Products.all():
            Product_List += list(self.FK_Coupon.FK_Products.all())
        Product_List = list(dict.fromkeys(Product_List))
        status = True
        for item in self.FK_FactorPost.all():
            if not item.FK_Product in Product_List:
                status = False
        return status

    def post_price_other_coupon_products(self):
        # get coupon product
        Product_List = []
        if self.FK_Coupon.FK_Shops.all():
            for item in self.FK_Coupon.FK_Shops.all():
                Product_List += list(Product.objects.filter(Publish = True, FK_Shop = item, Available = True))
        if self.FK_Coupon.FK_Products.all():
            Product_List += list(self.FK_Coupon.FK_Products.all())
        Product_List = list(dict.fromkeys(Product_List))
        # post price
        post_price = 0
        city_price = False
        shop = []
        for item in self.FK_FactorPost.all():
            if not item.FK_Product in Product_List:
                if item.FK_Product.FK_Shop.City == self.City:
                    city_price = True
                else:
                    if item.get_total_product_weight_with_count() != 0:
                        post_price += item.get_caculate_post()
                        shop.append(item.FK_Product.FK_Shop)
                    else:
                        shop.append(item.FK_Product.FK_Shop)
        shop = list(dict.fromkeys(shop))
        if len(shop) != 0:
            post_price += len(shop) * self.get_fixed_shipping_costs()
        if city_price:
            post_price += self.get_cost_within_the_city()
        return post_price

    def get_postprice(self):
        # Check Order Weight
        post_price = 0
        if (self.FK_Coupon != None) and (self.FK_Coupon.SerialNumber == 'nil-market') and (self.City == 'کرمان'):
            if self.check_coupon_products():
                return post_price
            else:
                if self.City == 'کرمان':
                    post_price += self.post_price_other_coupon_products()
                    return post_price
                else:
                    if (len(self.get_product_by_status(0)) == 0) and (self.check_order_total_weight()):
                        if len(self.get_product_by_status(1)) != 0:
                            post_price += self.get_cost_within_the_city()
                        if len(self.get_product_by_status(2)) != 0:
                            post_price += self.caculate_product_when_status_is_post()
                        return post_price
                    else:
                        return post_price
        else:
            if (len(self.get_product_by_status(0)) == 0) and (self.check_order_total_weight()):
                if len(self.get_product_by_status(1)) != 0:
                    post_price += self.get_cost_within_the_city()
                if len(self.get_product_by_status(2)) != 0:
                    post_price += self.caculate_product_when_status_is_post()
                return post_price
            else:
                return post_price

    def get_total_attr_price(self):
        totalAttr = 0
        for FactorPost in self.FK_FactorPost.all():
            bb = FactorPost.get_item_attr_price()
            totalAttr += bb
        return int(totalAttr)

    def get_end_price(self):
        c = self.get_total() - self.Coupon_price_min()
        if c < 0:
            c = 0
        if self.check_order_total_weight():
            c += self.get_postprice()
        if c <= 0:
            c = 10000
        return c

    def get_products_price(self):
        return (int(self.TotalPrice) + int(self.DiscountRate)) - int(self.PostPrice)

    # New Post Price
    def check_order_total_weight(self):
        total_order_weighte = 0
        for item in self.FK_FactorPost.all():
            total_order_weighte += item.get_total_product_weight_with_count()
        if (total_order_weighte > 40000) or (len(self.get_product_by_status(0)) != 0):
            if (len(self.get_product_by_status(0)) == 0) and (self.FK_Coupon != None) and (self.FK_Coupon.SerialNumber == 'nil-market') and (self.City == 'کرمان'):
                return True
            else:
                return False
        else:
            return True

    # Get Prodcut List By Status
    # 0 --> Shipping costs are borne by the customer
    # 1 --> Post in the city
    # 2 --> Send by regular mail
    def get_product_by_status(self, type):
        result = []
        # type = 0
        if type == 0:
            for item in self.FK_FactorPost.all():
                if item.FK_Product.check_product_post_status():
                    result.append(item)
        elif type == 1:
            for item in self.FK_FactorPost.all():
                if not item.FK_Product.check_product_post_status():
                    if (self.State == item.FK_Product.FK_Shop.State) and (self.BigCity == item.FK_Product.FK_Shop.BigCity) and (self.City == item.FK_Product.FK_Shop.City):
                        result.append(item)
        elif type == 2:
            for item in self.FK_FactorPost.all():
                if not item.FK_Product.check_product_post_status():
                    if (self.State != item.FK_Product.FK_Shop.State) or (self.BigCity != item.FK_Product.FK_Shop.BigCity) or (self.City != item.FK_Product.FK_Shop.City):
                        result.append(item)
        result = list(dict.fromkeys(result))
        return result

    # Get Caculate Prodcut When Status = 2
    def caculate_product_when_status_is_post(self):
        result = 0
        shop = []
        for item in self.get_product_by_status(2):
            if item.get_total_product_weight_with_count() != 0:
                result += item.get_caculate_post()
                shop.append(item.FK_Product.FK_Shop)
            else:
                shop.append(item.FK_Product.FK_Shop)
        shop = list(dict.fromkeys(shop))
        if len(shop) != 0:
            result += len(shop) * self.get_fixed_shipping_costs()
        return result

    def get_message_when_shipping_cost_by_customer(self):
        return 'حداقل هزینه ارسال 200 هزار تومان می باشد.'
            

    def get_send_user_factor(self, request):
        for item in self.FK_FactorPost.filter(ProductStatus = '3'):
            if item.FK_Product.FK_Shop.FK_ShopManager == request.user:
                return True
        return False

    def get_wait_user_factor(self, request):
        for item in self.FK_FactorPost.filter(ProductStatus = '1'):
            if item.FK_Product.FK_Shop.FK_ShopManager == request.user:
                return True
        return False

    def get_inpreparation_factor(self, request):
        for item in self.FK_FactorPost.filter(ProductStatus = '2'):
            if item.FK_Product.FK_Shop.FK_ShopManager == request.user:
                return True
        return False

    def get_cancel_factor(self, request):
        for item in self.FK_FactorPost.filter(ProductStatus = '0'):
            if item.FK_Product.FK_Shop.FK_ShopManager == request.user:
                return True
        return False

    def get_user_nation_code(self):
        try:
            return Profile.objects.get(FK_User = self.FK_User).NationalCode
        except:
            return None

    def get_user_fullname(self):
        try:
            return self.FK_User.first_name + ' ' + self.FK_User.last_name
        except:
            return None

    # Ordering With DateCreate
    class Meta:
        ordering = ('ID',)
        verbose_name = "فاکتور"
        verbose_name_plural = "فاکتور ها"

#----------------------------------------------------------------------------------------------------------------------------------

# PostBarCode (بارکد) Model
class PostBarCode (models.Model):
    FK_Factor=models.ForeignKey(Factor, on_delete=models.SET_NULL, verbose_name='شماره فاکتور', related_name='Factor_PostBarCode', null=True)
    User_Sender=models.TextField(verbose_name='فرستنده محصولات', blank=True)
    FK_Products=models.ManyToManyField(Product, verbose_name='محصول ارسال شده', related_name='Product_Sender', blank=True)
    BarCode=models.CharField(verbose_name='بارکد پستی', max_length=24)
    PostPrice=models.CharField(verbose_name='هزینه ارسال', max_length=15, default='0')
    SendDate=models.DateField(verbose_name='تاریخ ارسال مرسوله', null=True)
    CreateDate=models.DateField(verbose_name='تاریخ ایجاد', auto_now_add=True, null=True)
    SEND_TYPE =(
        ('0','درون شهری'),
        ('1','پست معمولی'),
        ('2','پس کرایه'),
    )
    SendType=models.CharField(verbose_name='وضعیت ارسال', max_length=1, choices=SEND_TYPE, default='1')
    Image=models.ImageField(verbose_name='عکس ارسال سفارش', upload_to=PathAndRename('media/Pictures/Barcode/'), null=True)

    def __str__(self):
        return "فاکتور : {} - بارکد پستی : {}".format(self.FK_Factor, self.BarCode)

    def get_send_type(self):
        SendType = {
            "0" : 'درون شهری',
            "1" : 'پست معمولی',
            "2" : 'پس کرایه',
        }
        return SendType[self.SendType]

    def get_date(self):
        try:
            date_format = "%Y-%m-%d"
            thisdate = datetime.strptime(str(self.SendDate), date_format)
            return jdatetime.date.fromgregorian(day = thisdate.day, month = thisdate.month, year = thisdate.year)
        except:
            return None

    class Meta:
        ordering = ('id',)
        verbose_name = "بارکد پستی"
        verbose_name_plural = "بارکد هایی پستی"
        
#----------------------------------------------------------------------------------------------------------------------------------

# ManegerFactor (فاکتور مدیریت) Model
class ManegerFactor (models.Model):
    ID=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    ManegerFactorNumber=models.CharField(verbose_name='شماره فاکتور', max_length=8, unique=True, default=BuildFactorCode(8))
    FK_Sender=models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='واریز کننده', related_name='User_Sender_MF', blank=True, null=True)
    FK_Receiver=models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='گیرنده', related_name='User_Receiver_MF', blank=True, null=True)
    Description=models.TextField(verbose_name='توضیحات فاکتور',max_length=350, blank=True)
    Date=models.DateTimeField(verbose_name='تاریخ', auto_now_add=True)
    Price=models.CharField(verbose_name='مبلغ', max_length=15)

    # Output Customization ID
    def __str__(self):
        return "{}".format(self.ManegerFactorNumber)

    # Ordering With DateCreate
    class Meta:
        ordering = ('ID',)
        verbose_name = "فاکتور مدیریت"
        verbose_name_plural = "فاکتور های مدیریت"
 
#----------------------------------------------------------------------------------------------------------------------------------

# PEC (اطلاعات مورد نیاز درگاه پرداخت تجارت الکترونیک پارسیان)
class PecOrder(models.Model):
    AdditionalData = models.CharField(verbose_name='نام و نام خانوادگی خریدار', max_length=500)
    Originator = models.CharField(verbose_name='شماره موبایل خریدار', max_length=50)
    Amount = models.IntegerField(verbose_name='هزینه خرید')
    FactorNumber = models.CharField(verbose_name='شماره فاکتور', max_length=10, default='0')
    Message = models.CharField(verbose_name='پیام پارسیان', max_length=127, null=True, blank=True)
    Status = models.IntegerField(verbose_name='کد وضعیت', null=True, blank=True)
    Token = models.BigIntegerField(verbose_name='توکن', null=True, blank=True)

class PecTransaction(models.Model):
    Token = models.BigIntegerField(verbose_name='توکن')
    OrderId = models.BigIntegerField(verbose_name='شماره تراکنش')
    TerminalNo = models.IntegerField(verbose_name='شماره ترمینال')
    RRN = models.BigIntegerField(verbose_name='شماره یکتایی')
    status = models.IntegerField(verbose_name='کد وضعیت')
    HashCardNumber = models.CharField(verbose_name='شماره کارت هش شده خریدار', max_length=127)
    Amount = models.BigIntegerField(verbose_name='هزینه خرید')
    DiscountedAmount = models.BigIntegerField(verbose_name='هزینه با احتساب تخفیف')
    STraceNo = models.CharField(max_length=127)

class PecConfirmation(models.Model):
    Status = models.IntegerField(verbose_name='کد وضعیت')
    CardNumberMasked = models.CharField(verbose_name='شماره کارت خریدار', max_length=127)
    Token = models.BigIntegerField(verbose_name='توکن')
    RRN = models.BigIntegerField(verbose_name='شماره یکتایی')
    OrderId = models.BigIntegerField(verbose_name='شماره تراکنش')

class PecReverse(models.Model):
    Status = models.IntegerField(verbose_name='کد وضعیت')
    Token = models.BigIntegerField(verbose_name='توکن')
    Message = models.CharField(verbose_name='پیام پارسیان', max_length=127, null=True, blank=True)
    OrderId = models.BigIntegerField(verbose_name='شماره تراکنش')
