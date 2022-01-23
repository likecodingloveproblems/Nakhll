from django.shortcuts import get_object_or_404, redirect
from nakhll_market.models import Product


def ProductsDetailWithSlug(request, product_slug, status = None, msg = None):
    ###################################
    ###### REDIRECT TO NEXT JS ########
    product = get_object_or_404(Product, Slug = product_slug)
    if not product.FK_Shop:
        return redirect('/')
    return redirect('/shop/' + product.FK_Shop.Slug + '/product/' + product_slug, permanent = True)

# Get Products
def ProductsDetail(request, shop_slug, product_slug, status = None, msg = None):
    ###################################
    ###### REDIRECT TO NEXT JS ########
    return redirect('/shop/' + shop_slug + '/product/' + product_slug, permanent = True)
    
