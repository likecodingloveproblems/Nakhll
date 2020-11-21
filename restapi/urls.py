from django.urls import path, re_path ,include
from django.conf.urls import url
from . import views, web_views, analyzeview

from rest_framework_jwt.views import obtain_jwt_token, verify_jwt_token

app_name = 'restapi'

urlpatterns = [
    re_path(r'^rest/get_factor_products/$', views.get_factor_products , name='get_factor_products'),


    re_path(r'^get-login-user/$', views.get_login_user , name='get_login_user'),
    re_path(r'^get-version/$', views.get_version , name='get_version'),

    #login and dashboard
    url(r'^v1/check-phone$', views.logins , name='loginapp'),
    re_path(r'^v1/get-user-detail/$', views.get_user_detail , name='get_user_detail'),
    re_path(r'^v1/get-user-wallet/$', views.get_user_wallet , name='get_user_wallet'),
    re_path(r'^v1/get-user-bank/$', views.get_user_bank , name='get_user_bank'),

    re_path(r'^v1/get-user-shop/$', views.get_user_shop , name='get_user_shop'),
    re_path(r'^v1/get-user-product/$', views.get_user_product , name='get_user_product'),

    re_path(r'^v1/get-submarket-list/$', views.get_submarket_list , name='get_submarket_list'),
    re_path(r'^v1/get-attribute-list/$', views.get_attribute_list , name='get_attribute_list'),
    re_path(r'^v1/get-category-list/$', views.get_category_list , name='get_category_list'),
    re_path(r'^v1/get-post-range-list/$', views.get_post_range_list , name='get_post_range_list'),


    re_path(r'^v1/get-user-message-is-true/$', views.get_user_message_status_is_true , name='get_user_message_status_is_true'),
    re_path(r'^v1/get-user-message-is-false/$', views.get_user_message_status_is_false , name='get_user_message_status_is_false'),

    re_path(r'^v1/change-message-status/$', views.change_message_status, name='change_message_status'),
    
    


    re_path(r'^v1/check-slug-shop$', views.check_slug_shop , name='check_slug_shop'),
    re_path(r'^v1/check-slug-product$', views.check_slug_product , name='check_slug_product'),


    # update profile
    url(r'^v1/update-user-profile$', views.update_user_profile , name='update_user_profile'),

    # factors for seller
    re_path(r'^v1/get-send-factor/$', views.get_send_factor , name='get_send_factor'),
    re_path(r'^v1/get-cancel-factor/$', views.get_cancel_factor , name='get_cancel_factor'),
    re_path(r'^v1/get-inpreparation-factor/$', views.get_inpreparation_factor , name='get_inpreparation_factor'),
    re_path(r'^v1/get-waiting-factor/$', views.get_waiting_factor , name='get_waiting_factor'),
    url(r'^v1/get-factor-detail$', views.get_factor_detail , name='get_factor_detail'),
    # new
    url(r'^v1/get-factor-detail-new$', views.get_factor_details , name='get_factor_detail'),


    #factors change status
    url(r'^v1/accept-factor-product$', views.accept_factor_product , name='accept_factor_product'),  
    url(r'^v1/cancel-factor-product$', views.cancel_factor_product , name='cancel_factor_product'),   
    url(r'^v1/barcodepost-for-factor$', views.barcodepost_for_factor , name='barcodepost_for_factor'),


    #Transactions for seller
    re_path(r'^v1/get-transactions/$', views.get_transactions , name='get_transactions'),

    # detail shop and product
    url(r'^v1/get-product-detail$', views.get_product_detail , name='get_product_detail'),
    url(r'^v1/get-product-all-banner$', views.get_product_all_banner , name='get_product_all_banner'),
    url(r'^v1/get-product-attribute$', views.get_product_attribute , name='get_product_attribute'),
    url(r'^v1/get-product-price-attribute$', views.get_product_price_attribute , name='get_product_price_attribute'),
    url(r'^v1/change-product-price-attribute$', views.change_product_price_attribute_status , name='change_product_price_attribute_status'),
    url(r'^v1/get-all-attribute$', views.get_all_attribute , name='get_all_attribute'),
    
    url(r'^v1/get-shop-detail$', views.get_shop_detail , name='get_shop_detail'),
    url(r'^v1/get-shop-banner$', views.get_shop_banner , name='get_shop_banner'),
    
    
    

    # create shop and product
    url(r'^v1/create-new-shop$', views.create_new_shop , name='create_new_shop'),
    url(r'^v1/add-shop-banner$', views.add_shop_banner , name='add_shop_banner'),



    url(r'^v1/create-new-product$', views.create_new_product , name='create_new_product'),
    url(r'^v1/add-product-banner$', views.add_product_banner , name='add_product_banner'),
    url(r'^v1/add-product-attribute$', views.add_product_attribute , name='add_product_attribute'),
    url(r'^v1/add-product-price-attribute$', views.add_product_price_attribute , name='add_product_price_attribute'),
    url(r'^v1/add-new-attrprice$', views.add_new_attribute , name='add_new_attribute'),




    # edit and delete for shop and product
    path('v1/edit-user-shop', views.edit_user_shop, name='edit_user_shop'),

    path('v1/edit-shop-banner', views.edit_shop_banner, name='edit_shop_banner'),
    path('v1/edit-shop-banner-status', views.edit_shop_banner_status, name='edit_shop_banner_status'),
    path('v1/delete-shop-banner', views.delete_shop_banner, name='delete_shop_banner'),


    path('v1/edit-user-product', views.edit_user_product, name='edit_user_product'),

    path('v1/edit-product-banner-status', views.change_product_banner_status, name='change_product_banner_status'),
    path('v1/delete-product-banner', views.delete_product_banner, name='delete_product_banner'),
    path('v1/delete-product-attribute', views.delete_product_attribute, name='delete_product_attribute'),
    path('v1/delete-product-price-attribute', views.delete_product_price_attribute, name='delete_product_price_attribute'),

    # Get First User Shop View Chart
    url(r'^v1/get-chart/$', views.get_chart , name='get_chart'),
    # Get User Message Count
    url(r'^v1/get-user-message-count/$', views.get_user_message_count , name='get-user-message-count'),
    # Get All User Shops Orders
    url(r'^v1/get-user-sale-statistics/$', views.get_user_sale_statistics , name='get-user-sale-statistics'),
    # Set Check Out
    url(r'^v1/set-check-out$', views.add_check_out , name='add_check_out'),
    # Get User Home Page Statistics
    url('v1/get-user-home-page-statistics/', views.get_user_home_page_statistics , name='get_user_home_page_statistics'),

    # Web Api---------------------------------------------------------------------------------------------------
    # check add poin for last user order
    path('check/factor/add-point/', web_views.check_status_of_score, name='web_check_status_of_score'),
    # Shop Api <--------->
    # create new shop
    path('create/shop', web_views.create_new_shop, name='web_create_new_shop'),
    # edit shop
    path('edit/shop', web_views.edit_shop, name='web_edit_shop'),
    # shop`s products filter
    path('filter/shop-products', web_views.filter_shop_products, name='filter_shop_products'),
    # search in shop`s products
    path('search/shop-products', web_views.search_in_shop_products, name='search_in_shop_products'),
    # add shop gallery
    path('add/shop/gallery-image', web_views.add_shop_gallery, name='web_shop_add_imagetogallery'),
    # change shop gallery status
    path('change/status/shop/gallery-image', web_views.change_shop_gallery_status, name='web_shop_change_status_imagetogallery'),
    # delete shop gallery
    path('delete/shop/gallery-image', web_views.delete_shop_gallery, name='web_shop_delete_imagetogallery'),
    # Product Api <--------->
    # Create New Product
    path('create/product', web_views.create_new_product, name='web_create_new_product'),
    # Edit Product
    path('edit/product', web_views.edit_product, name='web_edit_product'),
    # add product post range
    path('get-or-create/product/post-range', web_views.add_product_postrange, name='web_getorcreate_postrange'),
    # add product post range
    path('delete/product/post-range', web_views.delete_product_postrange, name='web_delete_postrange'),
    # add product attribute
    path('add/product/attribute', web_views.add_product_attribute, name='web_product_add_attribute'),
    # delete product attribute
    path('delete/product/attribute', web_views.delete_product_attribute, name='web_product_delete_attribute'),
    # add product gallery
    path('add/product/gallery-image', web_views.add_product_gallery, name='web_product_add_imagetogallery'),
    # delete product gallery
    path('delete/product/gallery-image', web_views.delete_product_gallery, name='web_product_delete_imagetogallery'),
    # change product gallery status
    path('change/status/product/gallery-image', web_views.change_product_gallery_status, name='web_product_change_status_imagetogallery'),
    # add new attribute
    path('add/attribute', web_views.add_attribute, name='web_add_new_attribute'),
    # add product optional attribute
    path('add/product/optional-attribute', web_views.add_optional_attribute, name='web_product_add_optional_attribute'),
    # add product optional attribute detail
    path('add/product/optional-attribute/detail', web_views.add_optional_attribute_detail, name='web_optional_attribute_add_detail'),
    # delete product optional attribute detail
    path('delete/product/optional-attribute/detail', web_views.delete_optional_attribute_detail, name='web_optional_attribute_delete_detail'),
    # delete product optional attribute
    path('delete/product/optional-attribute', web_views.delete_optional_attribute, name='web_product_optional_attribute'),
    # edit product optional attribute detail
    path('edit/product/optional-attribute/detail', web_views.edit_optional_attribute_detail, name='web_product_optional_attribute_edit_detail'),
    # edit product optional attribute
    path('edit/product/optional-attribute', web_views.edit_optional_attribute, name='web_product_edit_optional_attribute'),
    # IranCountryDivisions Api---------------------------------------------------------------------------------------------
    # Get States
    path('get-all-state/', web_views.get_all_state, name='get_all_state'),
    # Get State`s Bigcity
    path('get-state-bigcity', web_views.get_state_bigcity, name='get_state_bigcity'),
    # Get Bigcity`s City
    path('get-bigcity-city', web_views.get_bigcity_city, name='get_bigcity_city'),
    # Get Shop`s Submarkets Api <--------->
    path('get/shop/submarkets/', web_views.get_shop_submarkets, name='get_shop_submarkets'),
    # Analyze Api------------------------------------------------------------------------------------------------------------
    # # check the seller interaction Api <--------->
    # path('get/check-the-seller-interaction/', analyzeview.check_the_seller_interaction, name = 'check_the_seller_interaction'),
    # # get factor analyze Api <--------->
    # path('get/factor-analyze/', analyzeview.get_factor_analyze, name = 'get_factor_analyze'),
    # # get top product Api <--------->
    # path('get/top-products/', analyzeview.get_top_products, name = 'get_top_products'),
]