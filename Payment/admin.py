from django.contrib import admin
from .models import  Wallet, Transaction, Installment, Invitation, Campaign, Coupon, FactorPost, Factor, PostBarCode, ManegerFactor

#Wallet admin panel
@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display=('FK_User','Inverntory','CreditCard','CreditCardStatus')
    list_filter=('CreditCardStatus','CreditCard')
    ordering=['ID','FK_User','Inverntory','CreditCardStatus','CreditCard']
#-------------------------------------------------
#Factor admin panel
@admin.register(Factor)
class FactorAdmin(admin.ModelAdmin):
    list_display=('FactorNumber','FK_User','MobileNumber','FactorType','PostPrice','TotalPrice','PaymentStatus','OrderDate','DeliveryDate','DeliveryDate','DeliveryDate')
    list_filter=('OrderDate','DeliveryDate','PaymentStatus','OrderStatus','Checkout')
    readonly_fields = ('FactorNumber',)
    ordering=['OrderDate','DeliveryDate','Checkout','TotalPrice','FactorNumber']
#-------------------------------------------------
#Installment admin panel
@admin.register(Installment)
class InstallmentAdmin(admin.ModelAdmin):
    list_display=('Title','Description','StartDate','EndDate','Publish','Available','FK_User')
    list_filter=('Available','Publish')
    ordering=['id','Available','Publish','StartDate','EndDate','Title']
#-------------------------------------------------
#Transaction admin panel
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display=('ID','FK_Wallet','FK_User','Price','Description','Date','Type')
    list_filter=('Date','Type')
    ordering=['ID','Type','Price','Date']
#-------------------------------------------------
#Invitation admin panel
@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display=('id','FK_Shop','Status')
    list_filter=('Status',)
    ordering=['id','Status']
#-------------------------------------------------
#ManegerFactor admin panel
@admin.register(ManegerFactor)
class ManegerFactorAdmin(admin.ModelAdmin):
    list_display=('ID','ManegerFactorNumber','FK_Sender','FK_Receiver','Description','Date','Price')
    list_filter=('Date',)
    readonly_fields = ('ManegerFactorNumber',)
    ordering=['Date','Price']
#-------------------------------------------------
#PostBarCode admin panel
@admin.register(PostBarCode)
class PostBarCodeAdmin(admin.ModelAdmin):
    list_display=('id','FK_Factor','User_Sender','PostPrice','BarCode')
    ordering=['id']
#-------------------------------------------------
#Campaign admin panel
@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display=('Title','Description','FK_Creator','CampaignType','StartDate','EndDate','Publish')
    list_filter=('CampaignType','DiscountType','StartDate','Publish')
    ordering=['id','Title','StartDate','EndDate']
#-------------------------------------------------
#Coupon admin panel
@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    readonly_fields = ('SerialNumber',)
    list_display=('Title','SerialNumber','StartDate','EndDate','DiscountType','Publish')
    list_filter=('DiscountType','DiscountType','StartDate','Publish')
    ordering=['id','Title','StartDate','EndDate']
    readonly_fields = ('Log',)