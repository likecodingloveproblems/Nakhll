from django.urls import path, re_path 
from django.conf.urls import url
from .import views

app_name = 'Payment'

urlpatterns = [
    path('detail/', views.show_cart, name='cartdetail'),
    path('sendinfo', views.Set_Send_Info, name='sendinfo'),
    path('pay-detail/', views.Pay_Detail , name='Pay_Detail'),
    path('final-factor/', views.Final_Factor, name='final_factor'),

    path('add-to-cart/<uuid:ID>', views.add_to_cart, name='add-to-cart'),

    path('request/call/<uuid:factor_id>/<str:bank_port>', views.send_request_first, name='request_first'),

    url(r'^request/$', views.send_request, name='request'),
    url(r'^verify/$', views.verify , name='verify'),



    # path('add-to-cart-detail/<uuid:ID>', views.add_to_cart_detail, name='add-to-cart-detail'),

    path('unsuccessful/', views.unsuccessful, name='unsuccessful'),

    path('remove-from-cart/<uuid:ID>', views.remove_from_cart, name='remove-from-cart'),
    path('remove-item-from-cart/<ID>', views.remove_single_item_from_cart,
         name='remove-single-item-from-cart'),
    
    path('add-item-from-cart/<ID>', views.add_single_item_from_cart,
         name='add-single-item-from-cart'),

    path('delete-factor-coupon/<int:id>/', views.delete_coupon, name='delete-coupon-factor'),

    # path('request/<uuid:factor_id>', views.send_request, name='request'),
   

    # Add Product With Attribute Price
    path('add-product-to-cart/<uuid:ID>', views.AddProductToCartWithAttrPrice, name='AddProductToCartWithAttrPrice'),
    
    # Send Factor Product
    path('send_factor/<uuid:ID>', views.send_factor, name='send_factor'),
    path('send_factor/<uuid:ID>/<str:status>/<str:msg>/', views.send_factor, name='re_send_factor'),
    # Cansel Factor Product
    path('cansel_factor_product/<uuid:ID>', views.cansel_factor_product, name='cansel_factor_product'),
    # Accept Factor Product
    path('accept_factor_product/<uuid:ID>', views.accept_factor_product, name='accept_factor_product'),
    # Show Send Factor
    path('send_factor/<uuid:ID>', views.send_factor, name='send_factor_page'),
    # Charging User Wallet
     path('cherging-wallet/', views.send_request_wallet, name='send_request_wallet'),
    
    url(r'^request_wallet/$', views.send_request_wallet, name='request_wallet'),
    url(r'^verify_wallet/$', views.verify_wallet , name='verify_wallet'),
]