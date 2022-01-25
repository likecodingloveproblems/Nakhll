from django.shortcuts import get_object_or_404, redirect
from nakhll_market.models import Product


def ProductsDetailWithSlug(request, product_slug, status = None, msg = None):
    ###################################
    ###### REDIRECT TO NEXT JS ########
    product = Product.objects.filter(Slug=product_slug).first()
    if not product:
        return redirect('https://nakhll.com/404/')
    if not product.FK_Shop:
        return redirect('/')
    return redirect('/shop/' + product.FK_Shop.Slug + '/product/' + product_slug, permanent = True)

# Get Products
def ProductsDetail(request, shop_slug, product_slug, status = None, msg = None):
    ###################################
    ###### REDIRECT TO NEXT JS ########
    return redirect('/shop/' + shop_slug + '/product/' + product_slug, permanent = True)
    
