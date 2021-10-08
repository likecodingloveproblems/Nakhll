from cart.api import UserCartItemViewSet
from datetime import datetime, timedelta
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.sessions.models import Session
from nakhll_market.models import Product
from cart.models import Cart, CartItem

# Create your views here.


def add_to_cart(request, product_ID):
    ''' Get product and add it to cart with cart apis
   
        This method is only exists until frontend implement landing page
        and product details page, then they should handle adding product 
        to cart and this method can be deleted
    '''
    cartviewset = UserCartItemViewSet()
    request.query_params = {}
    cartviewset.request = request
    cartviewset.add(request, product_ID)
    return redirect('/cart/')


def show_cart(request):
    ''' Show cart to user 

        also check each cart item to be valid and available 
        for not logged in users, convert session['cart'] to cart object
    '''

    # TODO: What is campaign all about?
    #  if factor.FK_FactorPost.all().count() == 0:
    #     factor.FK_Coupon = None
    #     factor.FK_Campaign = None
    #     factor.save()

    # TODO: Check factor coupon validity
    # if factor.FK_Coupon != None:
    #     if not management_coupon_views.CheckCouponWhenShowCart(request, factor.ID):
    #         factor.FK_Coupon = None
    #     factor.save()

    # Get or Create cart base on user login status
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session._get_or_create_session_key()
        session, created = Session.objects.get_or_create(
            session_key=request.session.session_key, defaults={'expire_date': datetime.now() + timedelta(days=5)})
        cart, created = Cart.objects.get_or_create(session=session)

    # Check if item is valid or not
    for item in cart.items.all():
        if item.product.Status == '4' or \
                not item.product.Available or \
                not item.product.Publish:
            item.delete()

    context = {
        'cart': cart,
    }
    return render(request, 'payment/cart/pages/cart2.html', context)

    
    
