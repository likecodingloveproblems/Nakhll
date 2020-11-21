from django.shortcuts import render_to_response
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator
from django.urls import reverse
from django.views import generic
from ipware import get_client_ip
from datetime import datetime
from django.contrib import messages

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
from .models import Comment
from .models import Profile
from .models import Review
from .models import Survey
from .models import Slider
from .models import Message
from .models import Option_Meta
from .models import Newsletters 

from Payment.models import Wallet

#--------------------------------------------------------------------------------------------------------------------------------

# Shop - Cart
def ShopCart(request):

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
        }

        return render(request, 'payment/cart/pages/cart.html', context)

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

# Shop - Checking And Shipping Method
def ShopCheckingShippingMethod(request):

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
        }

        return render(request, 'payment/cart/pages/checking_and_shipping_method.html', context)

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

# Shop - Send Info
def ShopSendInfo(request):

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
        }

        return render(request, 'payment/cart/pages/sendinfo.html', context)

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

# Shop - Pay
def ShopPay(request):

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
        }

        return render(request, 'payment/cart/pages/pay.html', context)
        
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

# Shop - Add BarCode
def AddBarCode(request):

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
        }

        return render(request, 'payment/cart/pages/barcode.html', context)
        
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

# Shop - Add Nazar Sanji
def AddNazarSanji(request):

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
        }

        return render(request, 'payment/cart/pages/nazarsanji.html', context)
        
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