from django.urls import path, re_path 
from django.conf.urls import url  
from . import views, profileviews, cartviews, alertviews, ajaxviwes
from nakhll_market import management_coupon_views, management_content_views
from django.contrib.sitemaps.views import sitemap
from .sitemaps import ShopSitemap , ProductSitemap ,StaticViewSitemap
from django.views.generic import TemplateView

sitemaps = {
    'static': StaticViewSitemap,
    'Shops': ShopSitemap,
    'Products' : ProductSitemap,
    
}

app_name = 'nakhll_market'
urlpatterns = [
    url(r'^sitemap\.xml/$', sitemap, {'sitemaps' : sitemaps } , name='sitemap'),
    url(r'^robots\.txt/$', TemplateView.as_view(template_name="robots.txt", content_type='text/plain')),
    #----------------------------------------------- Login Path ----------------------------------------------
    # Session Path <----->
    path('set-session', views.set_session, name = 'set_session'),
    # Login Page Path
    re_path(r'^login/$', views.accountlogin, name='AccountLogin'),
    # Login To Account Path
    path('login-to-account/', views.login_to_account, name = 'login_to_account'), 
    # Logout Path
    re_path(r'^account/logout/$', views.logout, name='AccountLogout'),
    # Register Path
    re_path(r'^registering/$', views.Register, name='AccountRegister'),
    # Show Change Password Path
    re_path(r'^change_password/$', views.ShowChangePassword, name='ShowChangePasswordPage'),
    # Show Change Password Offline Page
    re_path(r'^change_password/off/$', views.ShowChangePasswordOff, name='ShowChangePasswordOff'),
    # Change Password Offline Path
    re_path(r'^change_password/offline/$', views.ChangePasswordOffline, name='ChangePasswordOffline'),
    # Change Password Path
    re_path(r'^change_password/changing$', views.ChangePassword, name='ChangePassword'),
    # Show Get Phone Number Page
    re_path(r'^forgetpassword/$', views.ShowGetPhoneNumber, name='ShowGetPhoneNumber'),
    
    re_path(r'^forgetpassword/codesetvalid/$', views.codesetvalid, name='codesetvalid'),
    # Get Registeri Code
    re_path(r'^account/register/$', views.GetRegisteriCode, name='GetRegisteriCode'),
    # Get Code Path
    re_path(r'^get_phonenumber/get_user_code/$', views.GetCode, name='GetCode'),
    # Get Code Path
    # re_path(r'^get_phonenumber/get_user_code/<str:code>$', views.GetUserCode, name='GetUserCode'),
    # ------------------------------------------------------ End ---------------------------------------------------






    # ------------------------------------------------- Coupun Section ----------------------------------------------
    # Shop Coupon--------------------------------------
    # Add Shop Copun Page
    path('profile/shop-manager/add/shop-copun', profileviews.AddShopCopun, name='Shop_Manager_ShopCopun'),
    # Shop Copun List Path
    path('profile/shop-manager/shop-copun-list/', profileviews.ShopCopunList, name='Shop_Manager_ShopCopunList'),
    # Delete Shop Copun Path
    path('profile/shops/shop_copun_delete/<int:id>', profileviews.DeleteShopCopun, name='DeleteShopCopun'),
    # Management Coupon------------------------------------
    # Management Copun List Path
    path('management/coupun/list/', management_coupon_views.ManagementCopunList, name='ManagementCoupunList'),
    # Add Management Copun Path
    path('management/coupun/add', management_coupon_views.AddManagementCopun, name='AddManagementCoupun'),
    # Add Filter In Management Coupon Path
    path('management/coupun/add/<int:id>', management_coupon_views.AddFilterManagementCoupon, name='AddFilterManagementCoupon'),
    # Filter Management Coupon Path
    path('management/coupun/add-filter/<int:id>', management_coupon_views.FilterManagementCoupon, name='FilterManagementCoupon'),
    # Delete Management Copun Path
    path('management/coupun/delete/<int:id>', management_coupon_views.DeleteManagementCoupon, name='DeleteManagementCoupon'),
    # Edite Management Copun Path
    path('management/coupun/edit/<int:id>', management_coupon_views.EditManagementCoupon, name='EditManagementCoupon'),
    # Save Edite Management Copun Path
    path('management/coupun/edit/<int:id>/save', management_coupon_views.SaveEditManagementCoupon, name='SaveEditManagementCoupon'),  
    # Check Coupon When Show Cart Path
    path('management/coupun/check-coupon-show-cart/<uuid:ID>/', management_coupon_views.CheckCouponWhenShowCart, name='CheckCouponWhenShowCart'),

    # Check Copun Path
    path('profile/check/copun_code/', profileviews.CheckCopun, name='CheckCopun'),
    # ------------------------------------------------------ End ---------------------------------------------------






    # ------------------------------------------------- Content Section ----------------------------------------------
    # Add New Full Shop Path
    path('management/content/add-new-full-shop/<str:msg>', management_content_views.Add_New_Full_Shop, name='Add_New_Full_Shop'),
    # Edit Full Shop Path
    path('management/content/edit-full-shop/<uuid:id>/<str:msg>', management_content_views.Edit_Full_Shop, name='Edit_Full_Shop'),
    # Add New Shop Banner Path
    path('management/content/add-new-shop-banner/<uuid:id>/<str:msg>', management_content_views.Add_New_Shop_Banner, name='Add_New_Shop_Banner'),
    # Add New Shop`s Product Path
    path('management/content/add-new-shop-product/<uuid:id>/<str:msg>', management_content_views.Add_New_Shop_Product, name='Add_New_Shop_Product'),
    # Add Edit Shop`s Product Path
    path('management/content/edit-full-product/<uuid:id>/<str:msg>', management_content_views.Edit_Full_Product, name='Edit_Full_Product'),
    # Add New Product Banner Path
    path('management/content/add-new-product-banner/<uuid:id>/<str:msg>', management_content_views.Add_New_Product_Banner, name='Add_New_Product_Banner'),
    # Add New Product Attribute Path
    path('management/content/add-new-product-attrbuit/<uuid:id>/<str:msg>', management_content_views.Add_New_Product_Attribute, name='Add_New_Product_Attribute'),
    # Add New Product AttrPrice Path
    path('management/content/add-new-product-attrprice/<uuid:id>/<str:msg>', management_content_views.Add_New_Product_AttrPrice, name='Add_New_Product_AttrPrice'),
    # Add New User Path
    path('management/content/add-new-user', management_content_views.Add_New_User, name='Add_New_User'),
    # Add New User`s Shop Path
    path('management/content/add-new-shop/<int:id>', management_content_views.Add_New_Shop, name='Add_New_Shop'),
    # Add New Product In User`s Shop Path
    path('management/content/add-new-product/<uuid:shop>', management_content_views.Add_New_Product, name='Add_New_Product'),
    # Add User`s Bank Account Info Path
    path('management/content/add-user-bank-account/<int:id>', management_content_views.Add_Bank_Account, name='Add_Bank_Account'),
    # Show All User Info Path
    path('management/content/show-all-user/', management_content_views.Show_All_User_Info, name='Show_All_User_Info'),
    # Show All Shoper User Info Path
    path('management/content/show-all-shoper-user/', management_content_views.Show_All_Shoper_User_Info, name='Show_All_Shoper_User_Info'),
    # Change User Status Path
    path('management/content/change-user-status/<int:User_ID>', management_content_views.Change_User_Status, name='Change_User_Status'),
    # Show User Info Path
    path('management/content/show-user-info/<int:id>/', management_content_views.Management_Show_User_Info, name = 'Show_User_Info'),
    # Edit User Info Path
    path('management/content/edit-user-info/<int:id>/<str:msg>', management_content_views.Management_Edit_User_Info, name = 'Edit_User_Info'),
    # Show All Content Path
    path('management/content/show-all-content/', management_content_views.Show_All_Content, name='Show_All_Content'),
    # Change Shop Seen Status Path
    path('management/content/change-shop-seen-status/<slug:id>/', management_content_views.Change_Shop_Seen_Status, name='Change_Shop_Seen_Status'),
    # Change Shop Publish Status Path
    path('management/content/change-shop-publish-status/<slug:id>/', management_content_views.Change_Shop_Publish_Status, name='Change_Shop_Publish_Status'),
    # Show Shop Info Path
    path('management/content/show-shop-info/<slug:Shop_Slug>/', management_content_views.Show_Shop_Info, name='Show_Shop_Info'),
    # Change Product Seen Status Path
    path('management/content/change-product-seen-status/<uuid:id>/', management_content_views.Change_Product_Seen_Status, name='Change_Shop_Seen_Status'),
    # Change Product Publish Status Path
    path('management/content/change-product-publish-status/<uuid:id>/', management_content_views.Change_Product_Publish_Status, name='Change_Shop_Publish_Status'),
    # Change Shop Banner Seen Status Path
    path('management/content/change-shop-banner-seen-status/<int:id>/', management_content_views.Change_Shop_Banner_Seen_Status, name='Change_Shop_Banner_Seen_Status'),
    # Change Shop Banner Publish Status Path
    path('management/content/change-shop-banner-publish-status/<int:id>/', management_content_views.Change_Shop_Banner_Publish_Status, name='Change_Shop_Banner_Publish_Status'),
    # Show Product Info Path
    path('management/content/show-product-info/<slug:Product_Slug>/', management_content_views.Show_Product_Info, name='Show_Product_Info'),
    # Change Product Banner Seen Status Path
    path('management/content/change-product-banner-seen-status/<int:id>/', management_content_views.Change_Product_Banner_Seen_Status, name='Change_Product_Banner_Seen_Status'),
    # Change Product Banner Publish Status Path
    path('management/content/change-product-banner-publish-status/<int:id>/', management_content_views.Change_Product_Banner_Publish_Status, name='Change_Product_Banner_Publish_Status'),
    # Change Product Attribute Status Path
    path('management/content/change-attribute-status/<int:id>/', management_content_views.Change_Product_Attribute_Status, name='Change_Product_Attribute_Status'),
    # Change Product Attribute Price Status Path
    path('management/content/change-attrprice-status/<int:id>/', management_content_views.Change_Product_AttrPrice_Status, name='Change_Product_AttrPrice_Status'),
    # ------------------------------------------------------ End ----------------------------------------------------






    # ------------------------------------------------- Ajax Section ----------------------------------------------
    # Check New Username With Ajax Path
    path('ajax/check/new/username/', ajaxviwes.check_new_username, name = 'Check_New_UserName'),
    # Check New NationalCode With Ajax Path
    path('ajax/check/new/nationalcode/', ajaxviwes.check_new_nationalcode, name = 'Check_New_NationalCode'),
    # Check New PhoneNumber With Ajax Path
    path('ajax/check/new/phonenumber/', ajaxviwes.check_new_phonenumber, name = 'Check_New_PhoneNumber'),
    # Check New Shop Slug With Ajax
    path('ajax/check/new/shopslug/', ajaxviwes.check_new_shop_slug, name='Check_New_Shop_Slug'),
    # Check New Product Slug With Ajax
    path('ajax/check/new/productslug/', ajaxviwes.check_new_product_slug, name='Check_New_Product_Slug'),
    # Check Order Send Zoon With Ajax
    path('ajax/check/orde-send-zoon/', ajaxviwes.check_zoon, name='Check_Order_Send_Zoon'),
    # Check Factor Send Info With Ajax
    path('ajax/check/factor-send-info/<uuid:id>/', ajaxviwes.check_factor_send_info, name='check_factor_send_info'),
    # Check Factor Send Info With Ajax
    path('ajax/check/user-profile-info/', ajaxviwes.check_user_profile_info, name='check_user_profile_info'),
    # Check Factor Inventory With Ajax
    path('ajax/check/check-factor-inventory/', ajaxviwes.Check_Factor_Inventory, name='Check_Factor_Inventory'),
    # Check Product Inventory With Ajax
    path('ajax/check/check-product-inventory/', ajaxviwes.Check_Product_Inventory, name='Check_Product_Inventory'),
    # Add Singel Product From Cart With Ajax
    path('ajax/check/check-add-singel-item-inventory/', ajaxviwes.Add_Single_Item_From_Cart, name='Add_Single_Item_From_Cart'),
    # Remove Singel Product From Cart With Ajax
    path('ajax/check/check-remove-singel-item-inventory/', ajaxviwes.Remove_Single_Item_From_Cart, name='Remove_Single_Item_From_Cart'),
    # Check Factor Inventory With Ajax
    path('ajax/check/pay-factor-by-wallet/', ajaxviwes.Pay_Factor_by_wallet, name='Pay_Factor_by_wallet'),
    # Add New Email With Ajax
    path('ajax/add/new-email/', ajaxviwes.Add_New_Email, name='Add_New_Email'),
    # Check User Back Account Info With Ajax
    path('ajax/check/back-account-info/', ajaxviwes.check_user_bank_account_info, name='check_user_bank_account_info'),
    # Add To Cart WithOut Price Attribute With Ajax
    path('ajax/add-to-cart/without-price-attribute/', ajaxviwes.add_to_cart_without_price_attribute, name='add_to_cart_without_price_attribute'),
    # Add To Cart With Price Attribute With Ajax
    path('ajax/add-to-cart/with-price-attribute/', ajaxviwes.add_to_cart_with_price_attribute, name='add_to_cart_with_price_attribute'),
    # Add User Location Info With Ajax
    path('ajax/add-to-profile/user-location-info/', ajaxviwes.add_user_location_info, name='add_user_location_info'),
    # Add User Location Info With Ajax
    path('ajax/get-excel-file/factor/<uuid:id>/', ajaxviwes.get_factor_excel_file, name='get_factor_excel_file'),
    # ----------------------------------------------------- End ---------------------------------------------------







    # ---------------------------------------------- Add Comment Section --------------------------------------------
    # Add New Comment In Product Path
    path('comment/product/add-new/<slug:this_product>', views.AddNewCommentInProduct, name='AddNewProductComment'),
    # Add Replay Comment In Product Path
    path('comment/product/add-replay/<int:id>', views.AddReplayCommentInProduct, name='AddReplayProductComment'),
    # Add New Comment In Shop Path
    path('comment/shop/add-new/<slug:this_shop>', views.AddNewCommentInShop, name='AddNewShopComment'),
    # Add Replay Comment In Shop Path
    path('comment/shop/add-replay/<int:id>', views.AddReplayCommentInShop, name='AddReplayShopComment'),
    # ------------------------------------------------------ End -----------------------------------------------------




    
    # ---------------------------------------------- Add Review Section ----------------------------------------------
    # Add New Review In Product Path
    path('review/product/add-new/<slug:this_product>', views.AddNewReviewInProduct, name='AddNewProductReview'),
    # ------------------------------------------------------ End -----------------------------------------------------






    #------------------------------------------------ Add Path ------------------------------------------------
    # # Add User Email To Data Base
    # url(r'^addemail/$', views.AddEmail, name='AddEmail'),
    # Add Ticket
    path('profile/ticketing/addticket/', profileviews.AddNewTicket, name='AddNewTicket'),

    #-------------------------------------------- Nakhll Market Path ------------------------------------------
    # index path
    path('', views.index, name='index'),
    # Show Market and SubMarket path
    path('markets/', views.market, name='Markets'),
    # Submarket Path
    path('markets/submarkets/<slug:submarket_slug>/', views.submarket, name='SubMarkets'),
    # Category Path
    path('category/<str:slug>/<str:status>/<str:delta_price>/', views.category, name='show_category_page'),
    # Shop Detail
    path('<slug:shop_slug>/', views.ShopsDetail, name='ShopsDetail'),
    path('<slug:shop_slug>/redirect/<str:msg>/', views.ShopsDetail, name='Re_ShopsDetail'),
    # Product Path
    path('product/<slug:shop_slug>/<slug:product_slug>/', views.ProductsDetail, name='ProductsDetail'),
    path('product/<slug:shop_slug>/<slug:product_slug>/<str:status>/<str:msg>/', views.ProductsDetail, name='Re_ProductsDetail'),
    # Product Comment Like
    path('product/like/<int:id>/<int:type>/', views.ContentLike, name='ProductLike'),
    # Shop Comment Like
    path('shop/like/<int:id>', views.ShopCommentLike, name='ShopCommentLike'),
    # Tag Path
    path('search/tag/<slug:tag_slug>/', views.TagDetail, name='TagDetail'),
    # Add New Comment Path
    re_path(r'^product/(?P<shop_slug>[-\w]+)/(?P<product_slug>[-\w]+)/add/comment/$', views.TagDetail, name='AddNewPRoductComment'),
    # Show All Shops
    path('shops/all/', views.AllShop, name='ShowAllShops'),
    # Show All Peoduct
    path('product/all/', views.FilterSearch, name='ShowAllProducts'),
    # Cart View To User Path
    path('profile/check/cart_view/', profileviews.CartView, name='CartView'),
    # Advanced Search Path
    path('pages/new-search/', views.Advanced_Search, name='Advanced_Search'),
    # -------------------------------------------------------- Nakhll Ajax Path ---------------------------------------------------------
    # Check User Massage Path
    path('profile/message/check/', profileviews.CheckUserMessage, name='CheckUserMessage'),
    # ------------------------------------------------------ Profile Path ---------------------------------------------------------------

    # Dashbord Path
    path('profile/dashboard/', profileviews.ProfileDashbord, name='Dashbord'),
    # Wallet Path
    path('profile/wallet/', profileviews.ProfileWallet, name='Wallet'),
    # Message Path
    path('profile/message/', profileviews.ProfileMessage, name='Message'),
    # Factor Path
    path('profile/factor/', profileviews.ProfileFactor, name='Factor'),
    # Tarnsaction Path
    path('profile/transaction/', profileviews.ProfileTransactione, name='Transaction'),
    # Review Path
    path('profile/shops/', profileviews.ProfileShops, name='UserShops'),
    # Shops Path
    path('profile/review/', profileviews.ProfileReview, name='Review'),
    # Alerts Path
    path('profile/alert/', profileviews.ProfileAlert, name='Alert'),
    # -------------------------------------------------------------------------------------
    # Message Filter
    path('profile/message/filter/', profileviews.MessageFilter, name='Message_Filter'),
    # Show All Alert Path
    path('profile/all-alert/', profileviews.ProfileShowAllAlert, name='ShowAllAlert'),
    # Alert Filter Path
    path('profile/alert/filter/', profileviews.AlertFilter, name='AlertFilter'),
    # Show All Factor Path
    path('profile/factor/all/', profileviews.ShowAllFactorList, name='ShowAllFactorList'),
    # Manage Factor Filter Path
    path('profile/factor/all/filter/', profileviews.ManageFactorFilter, name='ManageFactorFilter'),
    # Show Factor Item Path
    path('profile/factor/all/show_item/<uuid:ID>/', profileviews.ShowFactorItem, name='ShowFactorItem'),
    # Show Factor Item For Shop Path
    path('profile/factor/all/show_item_shop/<uuid:ID>/<int:status>/', profileviews.ShowFactorItemForShop, name='ShowFactorItemForShop'),
    # Change Factor Checkout Status Path
    path('profile/factor/show_all/change_checkout_status/<uuid:id>/', profileviews.ChangeFactorCheckoutStatus, name='ChangeFactorCheckoutStatus'),
    # Add User Bank Account Info Path
    path('profile/shop-manager/add/bank-account-info/', profileviews.add_user_bank_account_info, name='Shop_Manager_AddBankAccount'),
    # Add New Message Path
    path('profile/message/new/', profileviews.AddNewMessage, name='AddNewMessage'),
    # Add New Message And Show Message Path
    path('profile/message/new/<str:msg>/', profileviews.AddNewMessage, name='Re_AddNewMessage'),
    # Change Message Status Path
    path('profile/message/change_status/', profileviews.ChengeMessageStatus, name='ChengeMessageStatus'),
    # Show Invate Path
    path('profile/manage-coupon/invitation/', profileviews.ShowInvatePage, name='ShowInvatePage'),
    # ------------------------------------------------------------ End ------------------------------------------------------------------

    # ----------- Ticketing Section -------------
    # Ticketing Path
    path('profile/ticketing/', profileviews.ProfileTicketing, name='Ticketing'),
    # Ticketing Detail Path
    path('profile/ticketing/detail/<uuid:ticket_id>', profileviews.ProfileTicketingDetail, name='TicketinDetail'),
    # Ticketing Replay Path
    path('profile/ticketing/detail/replay/<uuid:ticket_id>', profileviews.RepalyTicketing, name='ReplayTicketin'),
    # ----------- End Ticketing Section ---------




    # -----Product Section-------
    # Add New Product
    path('profile/shop-manager/add/product', profileviews.add_new_product, name='Shop_Manager_AddNewProduct'),
    # Edit Product Page
    path('profile/shop-manager/edit/product/<slug:product_slug>/', profileviews.edit_product, name='Shop_Manager_EditProduct'),
    # Edit Product Info In Shop Managment
    # path('profile/shop-manager/edit/product/<slug:product_slug>', profileviews.EditeProduct, name='EditProduct'),
    # Show Product Details Page
    # path('profile/shops/productdetail/<slug:product_slug>/', profileviews.EditeProduct, name='ShowProductPage'),
    # Re_Edit Product
    # path('profile/shops/product/edite/<slug:product_slug>/<str:msg>', profileviews.EditeProduct, name='Re_EditProduct'),
    # -----End Product Section----------

    # -----Product Banner Section-------
    # Add New Product Banner
    path('profile/product/banner/add/<slug:product_slug>', profileviews.add_to_product_gallery, name='Shop_Manager_AddProductBanner'),
    # Delete Product Banner
    path('profile/product/banner/delete/<int:banner_id>', profileviews.delete_product_banner, name='DeleteProductBanner'),
    # Edit Product Banner
    path('profile/product/banner/edite/<int:banner_id>', profileviews.edit_product_banner, name='EditeProductBanner'),
    # Product Galery
    path('profile/shop-manager/product-banner-list/<slug:product_slug>/', profileviews.show_product_gallery, name='Shop_Manager_ProductBannerList'),
    # Change Status Shop Banner
    path('profile/shops/change_banner_status/<int:banner_id>', profileviews.change_product_banner_status, name='ChangeProductBannerStatus'),
    # -----End Product Banner Section-------

    # --------- Product Attribute -----------
    # Add Product Attribute Page
    path('profile/shop-manager/add/product-attribute/<slug:product_slug>', profileviews.add_product_attribute, name='Shop_Manager_AddProductAttribute'),
    # Product Attribute List
    path('profile/shop-manager/product-attribute-list/<slug:product_slug>/', profileviews.product_attribute_list, name='Shop_Manager_ProductAttributeList'),
    # Add New Attribute
    path('profile/shop-manager/add-new-attribute/<slug:product_slug>', profileviews.add_new_attribute, name='AddAttribute'),
    # Delete Attribute
    path('profile/shop-manager/delete-attribute/<int:attr_id>', profileviews.delete_product_attribute, name='Shop_Manager_DeleteAttribute'),
    # ------End Product Attribute------


    # ---------- Product Attribute Price ---------
    # Add Attribute Price Page
    path('profile/shop-manager/add-product-price-attribute/<slug:product_slug>', profileviews.add_product_attribute_price, name='Shop_Manager_ProductPriceAttribute'),
    # Attribute Price List
    path('profile/shop-manager/product-price-attribute-list/<slug:product_slug>/', profileviews.product_attribute_price_list, name='Shop_Manager_ProductPriceAttributeList'),
    # Delete Attribute Price
    path('profile/shops/delete-price-attribute/<int:id>', profileviews.delete_product_attribute_price, name='DeleteAttributePrice'),
    # Change Attribute Price Status
    path('profile/shops/change-price-attributr-status/<int:id>', profileviews.change_product_attribute_price_status, name='Change_Product_Attribute_Price_Status'),
    # ------------- End ----------------


    # ----------------- Shop ----------------
    # Add New Shop
    path('profile/shop-manager/add/shop', profileviews.add_new_shop, name='Shop_Manager_AddNewShop'),
    # Edit Shop Info In Shop Managment
    path('profile/shop-manager/edit/shop/<slug:shop_slug>', profileviews.edit_shop_info, name='Shop_Manager_EditShop'),
    # --------------- End --------------------

   
   # ---------------- Shop Banner -----------------
    # Add Shop Banner Page
    path('profile/shop-manager/add/shop-banner/<slug:shop_slug>', profileviews.add_shop_banner, name='Shop_Manager_AddShopBanner'),
    # Shop Banner List
    path('profile/shop-manager/shop-banner-list/<slug:shop_slug>/', profileviews.shop_banner_list, name='Shop_Manager_ShopBannerList'),
    # Edit Shop Banner Info
    path('profile/shop-manager/edit/shop-banner/<int:banner_id>', profileviews.edit_shop_banner, name='Shop_Manager_EditShopBanner'),
    # Delete Shop Banner
    path('profile/shop-manager/delete/shop-banner/<int:banner_id>', profileviews.delete_shop_banner, name='Shop_Manager_DeleteShopBanner'),
    # Change Status Shop Banner
    path('profile/shop-manager/change-status/shop-banner/<int:banner_id>', profileviews.change_shop_banner_status, name='Shop_Manager_ChangeShopBannerStatus'),
   # ---------End Shop Banner ----------------


    #---------------------------------------- Update Profile Values Path -------------------------------------
    # Send Push Path
    path('profile/send-push/', profileviews.SendPush, name='SendPush'),
    # Update Dashbord (User Info) Values Path
    path('profile/dashboard/update', profileviews.UpdateUserDashbord, name='UpdateUserInfo'),
    # # Update Dashbord (Profile Info) Values Path
    # re_path(r'^profile/dashboard/update/profileinfo/(?P<profile>[-\w\d]+)/$', profileviews.UpdateProfileDashbord, name='UpdateProfileInfo'),

    #------------------------------------------------ Pages Path ---------------------------------------------


    # Pages Path
    path('pages/static/<str:name>/', views.StaticPage, name='StaticPage'),
    # Pages connect us Path
    path('pages/connectus/', views.connectus, name='connectau'),
    # Pages Search
    path('pages/search/', views.search, name='search'),
    # Pages Complaint Path
    path('pages/complaint/', views.Complaint, name='complaint'),
    # Add Complaint
    path('pages/complaint/add', profileviews.AddNewComplaint, name='AddNewComplaint'),
    # Add Connect Us
    path('pages/connectus/add', profileviews.AddNewConnect, name='AddNewConnect'),


    # Show Campaing
    path('camp/dokhtar/', views.ShowCampaing, name='ShowCampaing'),
    path('camp/dokhtar/products', views.ShowCampProducts, name='ShowCampProduct'),


    #------------------------------------------------- Cart Path ----------------------------------------------

    # Cart Path
    path('markets/cart/', cartviews.ShopCart, name='Shop_CartPage'),\
    # Checking And Shipping Method Path
    path('markets/check_shipping_method/', cartviews.ShopCheckingShippingMethod, name='Shop_CheckingPage'),
    # Send Info Path
    path('markets/infosend/', cartviews.ShopSendInfo, name='Shop_SendInfoPage'),
    # Pay Path
    path('markets/paymethod/', cartviews.ShopPay, name='Shop_PayPage'),
    # Add BarCode Path
    path('markets/paymethod/add_barcode', cartviews.AddBarCode, name='AddBarCode'),
    # Add Nazar Sanji Path
    path('markets/paymethod/add_nazarsanji', cartviews.AddNazarSanji, name='AddNazarSanji'),

    #------------------------------------------------- Campaign Path ----------------------------------------------
    # Manage Campaign List Path
    path('profile/shops/manage_campaign_list/', profileviews.ManageCampaignList, name='ManageCampaignList'),

    #------------------------------------------------- Alert Path ----------------------------------------------

    # Comment Alert
    path('profile/alert/comment/<int:id>', alertviews.CommentAlert, name='CommentAlert'),
    # Review Alert
    path('profile/alert/review/<int:id>', alertviews.ReviewAlert, name='ReviewAlert'),
    # Shop Alert
    path('profile/alert/shop/<uuid:id>', alertviews.ShopAlert, name='ShopAlert'),
    # Shop Banner Alert
    path('profile/alert/shopbanner/<int:id>', alertviews.ShopBannerAlert, name='ShopBannerAlert'),
    # Product Alert
    path('profile/alert/product/<uuid:id>', alertviews.ProductAlert, name='ProductAlert'),
    # Product Banner Alert
    path('profile/alert/productbanner/<int:id>', alertviews.ProductBannerAlert, name='ProductBannerAlert'),
    # Attribute Alert
    path('profile/alert/attribute/<int:id>', alertviews.AttributeAlert, name='AttributeAlert'),
    # Attribute Product Alert
    path('profile/alert/attributeproduct/<int:id>', alertviews.ProductAttributeAlert, name='ProductAttributeAlert'),
    # Edite Shop Banner Alert
    path('profile/alert/editeshopbanner/<int:id>', alertviews.EditeShopBannerAlert, name='EditeShopBannerAlert'),
    # Edite Product Banner Alert
    path('profile/alert/editeproductbanner/<int:id>', alertviews.EditeProductBannerAlert, name='EditeProductBannerAlert'),
    # Edite Shop Alert
    path('profile/alert/editeshop/<uuid:id>', alertviews.EditeShopAlert, name='EditeShopAlert'),
    # Edite Product Alert
    path('profile/alert/editeproduct/<uuid:id>', alertviews.EditeProductAlert, name='EditeProductAlert'),
    # Ticlet Alert
    path('profile/alert/ticket/<uuid:id>', alertviews.TicketAlert, name='TicketAlert'),
    # Attribute Price Alert
    path('profile/alert/attrprice/<int:id>', alertviews.AttributePriceAlert, name='AttributePriceAlert'),
    # Connect Us Alert
    path('profile/alert/connectus/<int:id>', alertviews.ConnectUsAlert, name='ConnectUsAlert'),
    # Factor Alert
    path('profile/alert/factor/<uuid:id>', alertviews.FactorAlert, name='FactorAlert'),
    # Delete Shop Banner Alert
    path('profile/alert/deleteshopbanner/<int:id>', alertviews.DeleteShopBannerAlert, name='DeleteShopBannerAlert'),
    # Delete Product Banner Alert
    path('profile/alert/deleteproductbanner/<int:id>', alertviews.DeleteProductBannerAlert, name='DeleteProductBannerAlert'),
    # Delete Attribute Product Alert
    path('profile/alert/deleteattrproduct/<int:id>', alertviews.DeleteAttributeProductAlert, name='DeleteAttributeProductAlert'),
    # Delete Attribute Price Alert
    path('profile/alert/deleteattrprice/<int:id>', alertviews.DeleteAttributePriceAlert, name='DeleteAttributePriceAlert'),
    # Order Alert
    path('profile/alert/order/<int:id>', alertviews.OrderAlert, name='OrderAlert'),
    # Send Info Alert
    path('profile/alert/sendinfo/<int:id>', alertviews.SendInfoAlert, name='SendInfoAlert'),
    # Cansel Order Alert
    path('profile/alert/canselorder/<int:id>', alertviews.CanselOrderAlert, name='CanselOrderAlert'),
    # Delete Coupon Alert
    path('profile/alert/deletecoupon/<int:id>', alertviews.DeleteCouponAlert, name='DeleteCouponAlert'),
    # Add Coupon Alert
    path('profile/alert/addcoupon/<int:id>', alertviews.AddCouponAlert, name='AddCouponAlert'),
    # Add New Post Comment Alert
    path('profile/alert/postcomment/<int:id>', alertviews.AddPostCommentAlert, name='AddPostCommentAlert'),
    # Add New Story Comment Alert
    path('profile/alert/storycomment/<int:id>', alertviews.RecordStoryCommentAlert, name='RecordStoryCommentAlert'),
    # Add New Shop Comment Alert
    path('profile/alert/shopcomment/<int:id>', alertviews.RecordShopCommentAlert, name='RecordShopCommentAlert'),
    # Set Check Out Alert
    path('profile/alert/check-out/<int:id>', alertviews.Checkout_By_User_Alert, name='Checkout_By_User_Alert'),
    # Add New Optional Attribute
    path('profile/alert/optional-attribute/<int:id>', alertviews.Add_New_Optional_Attribute, name='Add_New_Optional_Attribute'),
    # Delete Optional Attribute
    path('profile/alert/delete-optional-attribute/<int:id>', alertviews.Delete_Optional_Attribute, name='Delete_Optional_Attribute'),











    # Show Product
    path('profile/alert/record/product/<uuid:id>', alertviews.RecordProductAlert, name='RecordProductAlert'),
    # Show Product Banner
    path('profile/alert/record/productbanner/<int:id>', alertviews.RecordProducBannertAlert, name='RecordProductBannerAlert'),
    # Show Attribute
    path('profile/alert/record/attribute/<int:id>', alertviews.RecordAttributeAlert, name='RecordAttributeAlert'),
    # Show Product Attribute
    path('profile/alert/record/productattribute/<int:id>', alertviews.RecordProductAttributeAlert, name='RecordProductAttributeAlert'),
    # Show Edite Shop Banner
    path('profile/alert/record/editeshopbanner/<int:id>', alertviews.RecordEditeShopBannerAlert, name='RecordEditeShopBannerAlert'),
    # Show Edite Product Banner
    path('profile/alert/record/editeproductbanner/<int:id>', alertviews.RecordEditeProductBannerAlert, name='RecordEditeProductBannerAlert'),
    # Show Edite Comment
    path('profile/alert/record/comment/<int:id>', alertviews.RecordCommentAlert, name='RecordCommentAlert'),
    # Show Edite Review
    path('profile/alert/record/review/<int:id>', alertviews.RecordReviewAlert, name='RecordReviewAlert'),
    # Show Shop Review
    path('profile/alert/record/shop/<uuid:id>', alertviews.RecordShopAlert, name='RecordShopAlert'),
    # Show Shop Banner Review
    path('profile/alert/record/shopbanner/<int:id>', alertviews.RecordShopBannerAlert, name='RecordShopBannerAlert'),
    # Show Edite Shop Review
    path('profile/alert/record/editeshop/<uuid:id>', alertviews.RecorShopAlert, name='RecordEditeShopAlert'),
    # Show Edite Product Review
    path('profile/alert/record/editeproduct/<uuid:id>', alertviews.RecorProductAlert, name='RecordProductAlert'),
    # Show Edite Product Review
    path('profile/alert/record/ticketreplay/<uuid:id>', alertviews.RecorTicketReplayAlert, name='RecordTicketReplayAlert'),
    # Show Attribute Price
    path('profile/alert/record/attrprice/<int:id>', alertviews.RecorAttributePriceAlert, name='RecordAttributePriceAlert'),
    # Show Connect Us
    path('profile/alert/record/connectus/<int:id>', alertviews.RecorConnectUsAlert, name='RecordConnectUsAlert'),
    # Show Factor
    path('profile/alert/record/factor/<uuid:id>', alertviews.RecorFactorAlert, name='RecordFactorAlert'),
    # Delete Shop Banner
    path('profile/alert/record/deleteshopbanner/<int:id>', alertviews.RecordDeleteShopBanner, name='RecordDeleteShopBanner'),
    # Delete Product Banner
    path('profile/alert/record/deleteproductbanner/<int:id>', alertviews.RecordDeleteProductBanner, name='RecordDeleteProductBanner'),
    # Delete Attribute Product
    path('profile/alert/record/deleteattrproduct/<int:id>', alertviews.RecordDeleteAttributeProduct, name='RecordDeleteAttributeProduct'),
    # Delete Attribute Price
    path('profile/alert/record/deleteattrprice/<int:id>', alertviews.RecordDeleteAttributePrice, name='RecordDeleteAttributePrice'),
    # Order
    path('profile/alert/record/order/<uuid:id>', alertviews.RecordOrderAlert, name='RecordOrderAlert'),
    # Send Info
    path('profile/alert/record/sendinfo/<int:id>', alertviews.RecordSendInfoAlert, name='RecordSendInfoAlert'),
    # Cansel Order
    path('profile/alert/record/canselorder/<int:id>', alertviews.RecordCanselOrderAlert, name='RecordCanselOrderAlert'),
    # Delete Coupon
    path('profile/alert/record/deletecoupon/<int:id>', alertviews.RecordDeleteCouponAlert, name='RecordDeleteCouponAlert'),
    # Add Coupon
    path('profile/alert/record/addcoupon/<int:id>', alertviews.RecordAddCouponAlert, name='RecordAddCouponAlert'),
    #------------------------------------------------------------ Error Path -----------------------------------------------------------
    # Add Coupon
    path('error-500/<str:error_text>/', profileviews.error_500, name='error_500'),
]