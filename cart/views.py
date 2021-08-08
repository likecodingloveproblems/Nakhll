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
    ''' Get product and add to user cart 
        Check if user logged in or not add to session for guest users and add
        to db if user logged in
    '''
    # TODO: Check for Product attributes and AttrPrice
    # TODO: Check for Coupons
    # // TODO: Check prev cart items and check if shop has enough item in stock

    # Check product availability
    product = get_object_or_404(Product, ID=product_ID)
    if (product.Status == '4') or (product.Inventory == 0):
        return redirect('nakhll_market:Re_ProductsDetail',
                        shop_slug=product.get_shop_slug(),
                        product_slug=product.Slug,
                        status=True,
                        msg='محصول مدنظر شما در حال حاضر موجود نمی باشد!')

    # Check for user login status
    # Create cart base on User object or session id
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session._get_or_create_session_key()
        session, created = Session.objects.get_or_create(
            session_key=request.session.session_key, defaults={'expire_date': datetime.now() + timedelta(days=5)})
        cart, created = Cart.objects.get_or_create(session=session)

    # Create cart items
    cart_item, created = CartItem.objects.get_or_create(cart=cart,
                                                        product=product, defaults={'count': 1})
    if not created:
        # First, check if shop owner has enough items in stock
        prev_count = cart_item.count
        if prev_count + 1 > product.Inventory:
            return redirect('nakhll_market:Re_ProductsDetail',
                            shop_slug=product.get_shop_slug(),
                            product_slug=product.Slug,
                            status=True,
                            msg='.فروشنده بیش از این تعداد قادر به تامین  کالا نمی باشد')
        # and now, add one more to cart
        cart_item.count += 1
        cart_item.save()

    return redirect('nakhll_market:ProductsDetail',
                    shop_slug=product.get_shop_slug(),
                    product_slug=product.Slug)


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

    
    
