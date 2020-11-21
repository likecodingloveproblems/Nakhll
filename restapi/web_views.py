from django.shortcuts import get_object_or_404 
from django.http import HttpResponse, JsonResponse
from django.utils.datastructures import MultiValueDictKeyError
from django.views.decorators.http import require_POST 
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib.auth.models import User
from django.core import serializers
import json

from nakhll_market.models import Profile, Product, Shop, SubMarket, Category, BankAccount, ShopBanner, Attribute, AttrProduct, AttrPrice, ProductBanner, PostRange, Alert, Field, OptinalAttribute, Details

from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.generics import (
    ListAPIView, 
    RetrieveAPIView,
    DestroyAPIView,
    UpdateAPIView,
    CreateAPIView,
)
from .serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from oauth2_provider.views.generic import ProtectedResourceView
from django.http import HttpResponse
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_403_FORBIDDEN,
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_202_ACCEPTED,
    HTTP_500_INTERNAL_SERVER_ERROR
)
from rest_framework.response import Response



# create new shop //req : shop information // res: ({title : 'shop_title' }) OR err
@csrf_exempt
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_new_shop(request):
    # This Shop Object
    this_shop = None
    try:
        # Get Data   
        shop_title = request.POST.get('shop_title')
        shop_slug = request.POST.get('shop_slug')
        shop_subMarket = request.POST.get('shop_submarket')
        try:
            shop_description = request.POST.get('shop_des')
        except:
            shop_description = None
        shop_state = request.POST.get('shop_state')
        shop_bigcity = request.POST.get('shop_bigcity')
        shop_city = request.POST.get('shop_city')
        try:
            shop_bio = request.POST.get('shop_bio')
        except:
            shop_bio = None
        shop_holidays = request.POST.get('shop_holidays')
        try:
            shop_profile = request.FILES["shop_image"]
        except MultiValueDictKeyError:
            shop_profile = None
        # Set Data
        # Chech Shop Image
        if (shop_profile != '') and (shop_profile != None):
            this_shop = Shop.objects.create(FK_ShopManager = request.user, Title = shop_title, Slug = shop_slug, State = shop_state, BigCity = shop_bigcity, City = shop_city, Image = shop_profile)
        else:
            this_shop = Shop.objects.create(FK_ShopManager = request.user, Title = shop_title, Slug = shop_slug, State = shop_state, BigCity = shop_bigcity, City = shop_city)
        # Set Shop Bio
        if (shop_bio != '') and (shop_bio != None):
            this_shop.Bio = shop_bio
        # Set Shop Description
        if (shop_description != '') and (shop_description != None):
            this_shop.Description = shop_description
        # Set Shop Holidays
        if shop_holidays != 'null':
            this_shop.Holidays = shop_holidays
        # Set Shop Submarkets
        shop_subMarket = shop_subMarket.split('~')
        for item in shop_subMarket:
            this_shop.FK_SubMarket.add(SubMarket.objects.get(ID = item))
        this_shop.save()
        # Set Alert
        Alert.objects.create(Part = '2', FK_User = request.user, Slug = this_shop.ID)
        return JsonResponse({'title' : this_shop.Title, 'ID' : this_shop.ID}, status = HTTP_201_CREATED)
    except Exception as e:
        try:
            if this_shop is not None:
                for item in this_shop.FK_SubMarket.all():
                    this_shop.FK_SubMarket.remove(item)
                this_shop.delete()
                return JsonResponse({'res' : str(e)}, status = HTTP_400_BAD_REQUEST)
            else:
                return JsonResponse({'res' : str(e)}, status = HTTP_400_BAD_REQUEST)
        except Exception as e:
            return JsonResponse({'res' : str(e)}, status = HTTP_400_BAD_REQUEST)
        







# add shop gallery //req : shop information // res: ({status : (True, False), id : shop_image, image : url}) OR err
@csrf_exempt
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_shop_gallery(request):
    # this shop object
    this_shop = None
    try:
        # get data
        shop_id = request.POST["shop_id"]
        gallery_image = request.FILES["gallery_image"]
        # set data
        this_shop = Shop.objects.get(ID = shop_id)
        # check access level
        if this_shop.FK_ShopManager == request.user:
            # add new shop gallery 
            this_shop_gallery = ShopBanner.objects.create(FK_Shop = this_shop, Image = gallery_image)
            # set alert
            Alert.objects.create(FK_User = request.user, Part = '4', Slug = this_shop_gallery.id)

            return JsonResponse({'status' : True, 'id' : this_shop_gallery.id, 'image' : str(this_shop_gallery.Image.url)}, status = HTTP_200_OK)
        else:
            return JsonResponse({'status' : False, 'message' : 'You do not have access to do this'}, status = HTTP_403_FORBIDDEN)
    except Exception as e:
        return JsonResponse({'status' : False, 'message' : str(e)}, status = HTTP_500_INTERNAL_SERVER_ERROR)







# change shop gallery status //req : shop information // res: ({status : (True, False), message}) OR err
@csrf_exempt
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def change_shop_gallery_status(request):
    # this shop object
    this_shop = None
    try:
        # get data
        shop_id = request.POST["shop_id"]
        gallery_image = request.POST["gallery_id"]
        # set data
        this_shop = Shop.objects.get(ID = shop_id)
        this_shop_gallery = ShopBanner.objects.get(id = gallery_image)
        # check access level
        if (this_shop.FK_ShopManager == request.user) and (this_shop_gallery.FK_Shop == this_shop):
            # check shop publish
            if this_shop_gallery.Publish:
                # chnage shop gallery status
                if this_shop_gallery.Available:
                    this_shop_gallery.Available = False
                    this_shop_gallery.save()
                else:
                    this_shop_gallery.Available = True
                    this_shop_gallery.save()

                return JsonResponse({'status' : True}, status = HTTP_200_OK)
            else:
               return JsonResponse({'status' : False, 'message' : 'This gallery image is not publish'}, status = HTTP_400_BAD_REQUEST) 
        else:
            return JsonResponse({'status' : False, 'message' : 'You do not have access to do this'}, status = HTTP_403_FORBIDDEN)
    except Exception as e:
        return JsonResponse({'status' : False, 'message' : str(e)}, status = HTTP_500_INTERNAL_SERVER_ERROR)









# delete shop gallery //req : shop information // res: ({status : (True, False), message}) OR err
@csrf_exempt
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def delete_shop_gallery(request):
    # this shop object
    this_shop = None
    try:
        # get data
        shop_id = request.POST["shop_id"]
        gallery_image_id = request.POST["gallery_image_id"]
        # set data
        this_shop = Shop.objects.get(ID = shop_id)
        this_shop_gallery = ShopBanner.objects.get(id = gallery_image_id)
        # check access level
        if (this_shop.FK_ShopManager == request.user) and (this_shop_gallery.FK_Shop == this_shop):
            # delete shop attribute
            if Alert.objects.filter(FK_User = request.user, Part = '4', Slug = this_shop_gallery.id, Seen = True).exists():
                # change status
                this_shop_gallery.Publish = False
                this_shop_gallery.save()
                # set alert
                if not Alert.objects.filter(FK_User = request.user, Part = '22', Slug = this_shop_gallery.id).exists():
                    Alert.objects.create(FK_User = request.user, Part = '22', Slug = this_shop_gallery.id)
                
                return JsonResponse({'status' : True}, status = HTTP_200_OK)
            else:
                # delete alert
                this_alert = Alert.objects.get(FK_User = request.user, Part = '4', Slug = this_shop_gallery.id, Seen = False)
                this_alert.delete()
                # delete shop attribute
                this_shop_gallery.delete()

                return JsonResponse({'status' : True}, status = HTTP_200_OK)
        else:
            return JsonResponse({'status' : False, 'message' : 'You do not have access to do this'}, status = HTTP_403_FORBIDDEN)
    except Exception as e:
        return JsonResponse({'status' : False, 'message' : str(e)}, status = HTTP_500_INTERNAL_SERVER_ERROR)








# edit shop //req : shop informaton // res: ({title : 'shop_title' }) OR err
@csrf_exempt
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def edit_shop(request):
    try:
        # Get Data
        try:
            shop_title = request.POST.get('shop_title')
        except:
            shop_title = None
        try:
            shop_description = request.POST.get('shop_des')
        except:
            shop_description = None
        try:
            shop_state = request.POST.get('shop_state')
        except:
            shop_state = None
        try:
            shop_bigcity = request.POST.get('shop_bigcity')
        except:
            shop_bigcity = None
        try:
            shop_city = request.POST.get('shop_city')
        except:
            shop_city = None
        try:
            shop_subMarket = request.POST.get('shop_submarket')
        except:
            shop_subMarket = None
        try:
            shop_bio = request.POST.get('shop_bio')
        except:
            shop_bio = None
        try:
            shop_ID = request.POST.get('shop_id')
        except:
            shop_ID = None
        shop_holidays = request.POST.get('shop_holidays')
        try:
            shop_profile = request.FILES["shop_image"]
        except MultiValueDictKeyError:
            shop_profile = None
        # Get This Shop
        this_shop = Shop.objects.get(ID = shop_ID)
        # check access level
        if this_shop.FK_ShopManager == request.user:
            # Check Alert
            edit_shop_alert = None
            if not Alert.objects.filter(Part = '3', Slug = this_shop.ID, Seen = False).exists():
                edit_shop_alert = Alert.objects.create(FK_User = request.user, Part = '3', Slug = this_shop.ID)
            else:
                edit_shop_alert = Alert.objects.get(Part = '3', Slug = this_shop.ID, Seen = False)
                edit_shop_alert.FK_Field.all().delete()
            # Check Shop Title
            if (shop_title != '') and (shop_title != None) and (shop_title != this_shop.Title):
                shop_title_field = Field.objects.create(Title = 'Title', Value = shop_title)
                edit_shop_alert.FK_Field.add(shop_title_field)
            # Check Shop State
            if (shop_state != '') and (shop_state != None) and (shop_state != this_shop.State):
                shop_state_field = Field.objects.create(Title = 'State', Value = shop_state)
                edit_shop_alert.FK_Field.add(shop_state_field)
            # Check Shop BigCity
            if (shop_bigcity != '') and (shop_bigcity != None) and (shop_bigcity != this_shop.BigCity):
                shop_bigcity_field = Field.objects.create(Title = 'BigCity', Value = shop_bigcity)
                edit_shop_alert.FK_Field.add(shop_bigcity_field)
            # Check Shop City
            if (shop_city != '') and (shop_city != None) and (shop_city != this_shop.City):
                shop_city_field = Field.objects.create(Title = 'City', Value = shop_city)
                edit_shop_alert.FK_Field.add(shop_city_field)
            # Check Shop Bio
            if (shop_bio != '') and (shop_bio != None) and (shop_bio != this_shop.Bio):
                shop_bio_field = Field.objects.create(Title = 'Bio', Value = shop_bio)
                edit_shop_alert.FK_Field.add(shop_bio_field)
            # Check Shop Description
            if (shop_description != '') and (shop_description != None) and (shop_description != this_shop.Description):
                shop_description_field = Field.objects.create(Title = 'Description', Value = shop_description)
                edit_shop_alert.FK_Field.add(shop_description_field)
            # Check Shop Holidays
            if (shop_holidays != 'null') and (shop_holidays != this_shop.Holidays):
                shop_holidays_field = Field.objects.create(Title = 'Holidays', Value = shop_holidays)
                edit_shop_alert.FK_Field.add(shop_holidays_field)
            # Check Shop Image
            if (shop_profile != '') and (shop_profile != None):
                this_shop.NewImage = shop_profile
                this_shop.save()
                new_image_string = 'NewImage' + '#' + str(this_shop.NewImage)
                shop_image_field = Field.objects.create(Title = 'Image', Value = new_image_string)
                edit_shop_alert.FK_Field.add(shop_image_field)
            # Check Shop Submarkets
            if (shop_subMarket != '') and (shop_subMarket != None):
                shop_submarket_field = Field.objects.create(Title = 'SubMarket', Value = shop_subMarket)
                edit_shop_alert.FK_Field.add(shop_submarket_field)
            # Check Edit
            if edit_shop_alert.FK_Field.all().count() != 0:
                return JsonResponse({'title' : this_shop.Title, 'status' : True}, status = HTTP_200_OK)
            else:
                edit_shop_alert.delete()
                return JsonResponse({'title' : this_shop.Title, 'status' : False}, status = HTTP_200_OK)
        else:
            return JsonResponse({'res' : 'You do not have access to do this'}, status = HTTP_403_FORBIDDEN)
    except Exception as e:
        return JsonResponse({'res' : str(e)}, status = HTTP_500_INTERNAL_SERVER_ERROR)






# create new product //req : product information // res: ({title : 'product_title' }) OR err
@csrf_exempt
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_new_product(request):
    # this product object
    this_product = None
    try:
        # Get Data
        title = request.POST["product_title"]
        slug = request.POST["product_slug"]
        image = request.FILES["product_image"]
        shop_id = request.POST["product_shop"]
        categories = request.POST["product_category"]
        submarket_id = request.POST["product_submarket"]
        price = request.POST["product_price"]
        oldprice = request.POST["product_oldprice"]
        send_type = request.POST["product_sendtype"]
        status = request.POST["product_status"]
        net_weight = request.POST["product_netweight"]
        packing_weight = request.POST["product_packingweight"]
        length = request.POST["product_length"]
        width = request.POST["product_width"]
        height = request.POST["product_height"]
        try:
            description = request.POST["product_description"]
        except:
            description = None
        try:
            bio = request.POST["product_bio"]
        except:
            bio = None
        try:
            story = request.POST["product_story"]
        except:
            story = None
        try:
            inventory = request.POST["product_inventory"]
        except:
            inventory = None
        # Set Data
        this_shop = Shop.objects.get(ID = shop_id)
        this_submarket = SubMarket.objects.get(ID = submarket_id)
        # check access level
        if (this_shop.FK_ShopManager == request.user) and (Shop.objects.get(ID = shop_id).FK_ShopManager == request.user):
            # Check Product Image
            if (image != '') and (image != None):
                this_product = Product.objects.create(FK_Shop = this_shop, Image = image, Title = title, Slug = slug, FK_SubMarket = this_submarket, Price = price, OldPrice = oldprice, Net_Weight = net_weight, Weight_With_Packing = packing_weight, Length_With_Packaging = length, Width_With_Packaging = width, Height_With_Packaging = height, PostRangeType = send_type, Status = status)
            else:
                this_product = Product.objects.create(FK_Shop = this_shop, Title = title, Slug = slug, FK_SubMarket = this_submarket, Price = price, OldPrice = oldprice, Net_Weight = net_weight, Weight_With_Packing = packing_weight, Length_With_Packaging = length, Width_With_Packaging = width, Height_With_Packaging = height, PostRangeType = send_type, Status = status)
            # Set Product Bio
            if (bio != '') and (bio != None):
                this_product.Bio = bio
            # Set Product Description
            if (description != '') and (description != None):
                this_product.Description = description
            # Set Product Story
            if (story != '') and (story != None):
                this_product.Story = story
            # Set Shop Categories
            product_category = categories.split('~')
            for item in product_category:
                if (item != '') and (Category.objects.filter(id = item).exists()):
                    this_product.FK_Category.add(Category.objects.get(id = item))
            # Set Product Inventory
            if inventory != None:
                this_product.Inventory = inventory
            this_product.save()
            # Set Alert
            Alert.objects.create(Part = '6', FK_User = request.user, Slug = this_product.ID)
            return JsonResponse({'title' : this_product.Title, 'id' : this_product.ID}, status = HTTP_201_CREATED)
        else:
            return JsonResponse({'res' : 'You do not have access to do this'}, status = HTTP_403_FORBIDDEN)
    except Exception as e:
        try:
            if this_product is not None:
                for item in this_product.FK_Category.all():
                    this_product.FK_Category.remove(item)
                for item in this_product.FK_PostRange.all():
                    this_product.FK_PostRange.remove(item)
                for item in this_product.FK_ExceptionPostRange.all():
                    this_product.FK_ExceptionPostRange.remove(item)
                this_product.delete()
                return JsonResponse({'res' : str(e)}, status = HTTP_400_BAD_REQUEST)
            else:
                return JsonResponse({'res' : str(e)}, status = HTTP_400_BAD_REQUEST)
        except Exception as e:
            return JsonResponse({'res' : str(e)}, status = HTTP_500_INTERNAL_SERVER_ERROR)







# add product post range //req : product information // res: ({title : 'product_title' }) OR err
@csrf_exempt
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_product_postrange(request):
    # this product object
    this_product = None
    try:
        # get data
        product_id = request.POST["product_id"]
        state = request.POST["state_range"]
        bigcity = request.POST["bigcity_range"]
        city = request.POST["city_range"]
        status = request.POST["status_range"]
        # set data
        this_product = Product.objects.get(ID = product_id)
        # check access level
        if this_product.FK_Shop.FK_ShopManager == request.user:
            # get or add post range
            this_range = None
            if (bigcity == 'null') and (city == 'null'):
                this_range = PostRange.objects.get_or_create(State = state, BigCity = '', City = '')[0]
            elif (bigcity != 'null') and (city == 'null'):
                this_range = PostRange.objects.get_or_create(State = state, BigCity = bigcity, City = '')[0]
            elif (bigcity != 'null') and (city != 'null'):
                this_range = PostRange.objects.get_or_create(State = state, BigCity = bigcity, City = city)[0]
            # add post range to this product
            if bool(int(status)):
            #     # add to post range
                this_product.FK_PostRange.add(this_range)
            else:
            #     # add to exception post range
                this_product.FK_ExceptionPostRange.add(this_range)
            return JsonResponse({'status' : True, 'id' : this_range.id}, status = HTTP_200_OK)
        else:
            return JsonResponse({'status' : False, 'message' : 'You do not have access to do this'}, status = HTTP_403_FORBIDDEN)
    except Exception as e:
        return JsonResponse({'status' : False, 'message' : str(e)}, status = HTTP_500_INTERNAL_SERVER_ERROR)










# delete product post range //req : product information // res: ({title : 'product_title' }) OR err
@csrf_exempt
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def delete_product_postrange(request):
    # this product object
    this_product = None
    try:
        # get data
        product_id = request.POST["product_id"]
        postrange_id = request.POST["postrange_id"]
        status = request.POST["status_range"]
        # set data
        this_product = Product.objects.get(ID = product_id)
        this_postrange = PostRange.objects.get(id = postrange_id)
        # check access level
        if this_product.FK_Shop.FK_ShopManager == request.user:
            # delete data
            if bool(int(status)):
            # add to post range
                this_product.FK_PostRange.remove(this_postrange)
            else:
            # add to exception post range
                this_product.FK_ExceptionPostRange.remove(this_postrange)
            return JsonResponse({'status' : True}, status = HTTP_200_OK)
        else:
            return JsonResponse({'status' : False, 'message' : 'You do not have access to do this'}, status = HTTP_403_FORBIDDEN)
    except Exception as e:
        return JsonResponse({'status' : False, 'message' : str(e)}, status = HTTP_500_INTERNAL_SERVER_ERROR)







# add product attribute //req : product information // res: ({title : 'product_title' }) OR err
@csrf_exempt
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_product_attribute(request):
    # this product object
    this_product = None
    try:
        # get data
        product_id = request.POST["product_id"]
        attribute_id = request.POST["attribute_id"]
        value = request.POST["attribute_value"]
        # set data
        this_product = Product.objects.get(ID = product_id)
        this_attribute = Attribute.objects.get(id = attribute_id)
        # check access level
        if this_product.FK_Shop.FK_ShopManager == request.user:
            # add new product attribute
            if not AttrProduct.objects.filter(FK_Product = this_product, FK_Attribute = this_attribute).exists():
                this_product_attribute = AttrProduct.objects.create(FK_Product = this_product, FK_Attribute = this_attribute, Value = value)
                # set alert
                if not Alert.objects.filter(FK_User = request.user, Part = '11', Slug = this_product_attribute.id).exists():
                    Alert.objects.create(FK_User = request.user, Part = '11', Slug = this_product_attribute.id)

                return JsonResponse({'status' : True, 'id' : this_product_attribute.id}, status = HTTP_200_OK)
            else:
                return JsonResponse({'status' : False, 'message' : 'This product`s attribute is exists'}, status = HTTP_400_BAD_REQUEST)
        else:
            return JsonResponse({'status' : False, 'message' : 'You do not have access to do this'}, status = HTTP_403_FORBIDDEN)
    except Exception as e:
        return JsonResponse({'status' : False, 'message' : str(e)}, status = HTTP_500_INTERNAL_SERVER_ERROR)







# delete product attribute //req : product information // res: ({title : 'product_title' }) OR err
@csrf_exempt
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def delete_product_attribute(request):
    # this product object
    this_product = None
    try:
        # get data
        product_id = request.POST["product_id"]
        product_attribute_id = request.POST["product_attribute_id"]
        # set data
        this_product = Product.objects.get(ID = product_id)
        this_product_attribute = AttrProduct.objects.get(id = product_attribute_id)
        # check access level
        if this_product.FK_Shop.FK_ShopManager == request.user:
            # check product attribute
            if this_product_attribute.FK_Product == this_product:
                # delete product attribute
                if Alert.objects.filter(FK_User = request.user, Part = '11', Slug = this_product_attribute.id, Seen = True).exists():
                    # change status
                    this_product_attribute.Available = False
                    this_product_attribute.save()
                    # set alert
                    if not Alert.objects.filter(Part = '24', FK_User = request.user, Slug = this_product_attribute.id).exists():
                        Alert.objects.create(Part = '24', FK_User = request.user, Slug = this_product_attribute.id)
                    
                    return JsonResponse({'status' : True}, status = HTTP_200_OK)
                else:
                    # delete alert
                    this_alert = Alert.objects.get(FK_User = request.user, Part = '11', Slug = this_product_attribute.id, Seen = False)
                    this_alert.delete()
                    # delete product attribute
                    this_product_attribute.delete()

                    return JsonResponse({'status' : True}, status = HTTP_200_OK)
            else:
                return JsonResponse({'status' : False, 'message' : 'This attribute is not related to this product'}, status = HTTP_400_BAD_REQUEST)
        else:
            return JsonResponse({'status' : False, 'message' : 'You do not have access to do this'}, status = HTTP_403_FORBIDDEN)
    except Exception as e:
        return JsonResponse({'status' : False, 'message' : str(e)}, status = HTTP_500_INTERNAL_SERVER_ERROR)








# add attribute //req : product information // res: ({status : (True, False), massage : (system_message) }) OR err
@csrf_exempt
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_attribute(request):
    try:
        # get data
        this_title = request.POST["attribute_title"]
        this_unit = request.POST["attribute_unit"]
        # set data
        if not Attribute.objects.filter(Title = this_title, Unit = this_unit).exists():
            # create new attribute
            this_attribute = Attribute.objects.create(Title = this_title, Unit = this_unit, Publish = True)
            # set alert
            # Alert.objects.create(FK_User = request.user, Part = '10', Slug = this_attribute.id)
            # set serializer
            serializer = AttributeSerializer(this_attribute)

            return JsonResponse({'status' : True, 'data' : serializer.data}, status = HTTP_201_CREATED, safe = False)
        else:
            return JsonResponse({'status' : False, 'message' : 'The entered data is duplicate'}, status = HTTP_400_BAD_REQUEST)
    except Exception as e:
        return JsonResponse({'status' : False, 'message' : str(e)}, status = HTTP_500_INTERNAL_SERVER_ERROR)







# add product gallery //req : product information // res: ({status : (True, False), id : product_image, image : url' }) OR err
@csrf_exempt
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_product_gallery(request):
    # this product object
    this_product = None
    try:
        # get data
        product_id = request.POST["product_id"]
        gallery_image = request.FILES["gallery_image"]
        # set data
        this_product = Product.objects.get(ID = product_id)
        # check access level
        if this_product.FK_Shop.FK_ShopManager == request.user:
            # add new product gallery 
            this_product_gallery = ProductBanner.objects.create(FK_Product = this_product, Image = gallery_image)
            # set alert
            Alert.objects.create(FK_User = request.user, Part = '8', Slug = this_product_gallery.id)

            return JsonResponse({'status' : True, 'id' : this_product_gallery.id, 'image' : str(this_product_gallery.Image_thumbnail_url())}, status = HTTP_200_OK)
        else:
            return JsonResponse({'status' : False, 'message' : 'You do not have access to do this'}, status = HTTP_403_FORBIDDEN)
    except Exception as e:
        return JsonResponse({'status' : False, 'message' : str(e)}, status = HTTP_500_INTERNAL_SERVER_ERROR)







# change product gallery status //req : product information // res: ({status : (True, False)}) OR err
@csrf_exempt
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def change_product_gallery_status(request):
    # this product object
    this_product = None
    try:
        # get data
        product_id = request.POST["product_id"]
        product_gallery = request.POST["gallery_id"]
        # set data
        this_product = Product.objects.get(ID = product_id)
        this_product_gallery = ProductBanner.objects.get(id = product_gallery)
        # check access level
        if (this_product.FK_Shop.FK_ShopManager == request.user) and (this_product_gallery.FK_Product == this_product):
            # check product publish
            if this_product_gallery.Publish:
                # chnage product gallery status
                if this_product_gallery.Available:
                    this_product_gallery.Available = False
                    this_product_gallery.save()
                else:
                    this_product_gallery.Available = True
                    this_product_gallery.save()

                return JsonResponse({'status' : True}, status = HTTP_200_OK)
            else:
               return JsonResponse({'status' : False, 'message' : 'This gallery image is not publish'}, status = HTTP_400_BAD_REQUEST) 
        else:
            return JsonResponse({'status' : False, 'message' : 'You do not have access to do this'}, status = HTTP_403_FORBIDDEN)
    except Exception as e:
        return JsonResponse({'status' : False, 'message' : str(e)}, status = HTTP_500_INTERNAL_SERVER_ERROR)









# delete product gallery //req : product information // res: ({title : 'product_title' }) OR err
@csrf_exempt
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def delete_product_gallery(request):
    # this product object
    this_product = None
    try:
        # get data
        product_id = request.POST["product_id"]
        gallery_image_id = request.POST["gallery_image_id"]
        # set data
        this_product = Product.objects.get(ID = product_id)
        this_product_gallery = ProductBanner.objects.get(id = gallery_image_id)
        # check access level
        if (this_product.FK_Shop.FK_ShopManager == request.user) and (this_product_gallery.FK_Product == this_product):
            # delete product attribute
            if Alert.objects.filter(FK_User = request.user, Part = '8', Slug = this_product_gallery.id, Seen = True).exists():
                # change status
                this_product_gallery.Publish = False
                this_product_gallery.save()
                # set alert
                if not Alert.objects.filter(FK_User = request.user, Part = '23', Slug = this_product_gallery.id).exists():
                    Alert.objects.create(FK_User = request.user, Part = '23', Slug = this_product_gallery.id)
                
                return JsonResponse({'status' : True}, status = HTTP_200_OK)
            else:
                # delete alert
                this_alert = Alert.objects.get(FK_User = request.user, Part = '8', Slug = this_product_gallery.id, Seen = False)
                this_alert.delete()
                # delete product attribute
                this_product_gallery.delete()

                return JsonResponse({'status' : True}, status = HTTP_200_OK)
        else:
            return JsonResponse({'status' : False, 'message' : 'You do not have access to do this'}, status = HTTP_403_FORBIDDEN)
    except Exception as e:
        return JsonResponse({'status' : False, 'message' : str(e)}, status = HTTP_500_INTERNAL_SERVER_ERROR)







# add optional attribute //req : product id, optional attribute information // res: ({status : (True, False), optinal attribute object, massage : (system_message) }) OR err
@csrf_exempt
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_optional_attribute(request):
    try:
        # get data
        this_product_id = request.POST["product_id"]
        this_title = request.POST["this_title"]
        this_type = request.POST["this_type"]
        this_status = request.POST["this_status"]
        # set data
        this_product = Product.objects.get(ID = this_product_id)
        if this_status == '0':
            this_status_bool = False
        else:
            this_status_bool = True
        # check access level
        if this_product.FK_Shop.FK_ShopManager == request.user:
            # check data
            if not this_product.FK_OptinalAttribute.filter(Title = this_title).exists():
                # create new optional attribute
                this_optional_attribute = OptinalAttribute.objects.create(Title = this_title, Type  = this_type, Status = this_status_bool)
                # add this optional attribute to product
                this_product.FK_OptinalAttribute.add(this_optional_attribute)
                # set alert
                Alert.objects.create(Part = '32', FK_User = request.user, Slug = this_optional_attribute.id)
                # serializer data
                serializer = OptionalAttributeSerializer(this_optional_attribute)
                
                return JsonResponse({'status' : True, 'data' : serializer.data}, status = HTTP_201_CREATED)
            else:
               return JsonResponse({'status' : False, 'message' : 'The entered data is duplicate'}, status = HTTP_400_BAD_REQUEST) 
        else:
            return JsonResponse({'status' : False, 'message' : 'You do not have access to do this'}, status = HTTP_403_FORBIDDEN)
    except Exception as e:
        return JsonResponse({'status' : False, 'message' : str(e)}, status = HTTP_500_INTERNAL_SERVER_ERROR)






# add optional attribute detail //req : product id, optional attribute id, detail information // res: ({status : (True, False), detail file, massage : (system_message) }) OR err
@csrf_exempt
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_optional_attribute_detail(request):
    try:
        # get data
        this_product_id = request.POST["product_id"]
        this_optional_attribute_id = request.POST["optional_attribute_id"]
        this_value = request.POST["this_value"]
        this_price = request.POST["this_price"]
        this_weight = request.POST["this_weight"]
        this_length = request.POST["this_length"]
        this_width = request.POST["this_width"]
        this_height = request.POST["this_height"]
        this_inventory = request.POST["this_inventory"]
        this_status = request.POST["this_status"]
        # set data
        this_product = Product.objects.get(ID = this_product_id)
        this_optional_attribute = OptinalAttribute.objects.get(id = this_optional_attribute_id)
        # check access level
        if (this_product.FK_Shop.FK_ShopManager == request.user) and (this_product.FK_OptinalAttribute.filter(id = this_optional_attribute_id).exists()):
            # check optional attribute details
            if not this_product.FK_OptinalAttribute.get(id = this_optional_attribute_id).FK_Details.all().filter(Value = this_value, Price = this_price, Weight = this_weight, Length = this_length, Width = this_width, Height = this_height).exists():
                # create datails
                this_detail = Details.objects.create(Value = this_value, Price = this_price, Weight = this_weight, Length = this_length, Width = this_width, Height = this_height, Inventory = this_inventory, Status = this_status)
                # add file to optional attribute
                this_optional_attribute.FK_Details.add(this_detail)
                # serializer data
                serializer = OptionalAttributeSerializer(this_optional_attribute)
            
                return JsonResponse({'status' : True, 'data' : serializer.data}, status = HTTP_201_CREATED)
            else:
                return JsonResponse({'status' : False, 'message' : 'The entered data is duplicate'}, status = HTTP_400_BAD_REQUEST)
        else:
            return JsonResponse({'status' : False, 'message' : 'You do not have access to do this'}, status = HTTP_403_FORBIDDEN)
    except Exception as e:
        return JsonResponse({'status' : False, 'message' : str(e)}, status = HTTP_500_INTERNAL_SERVER_ERROR)







# delete optional attribute detail //req : product id, optional attribute id, detail id // res: ({status : (True, False), detail file, massage : (system_message) }) OR err
@csrf_exempt
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def delete_optional_attribute_detail(request):
    try:
        # get data
        this_product_id = request.POST["product_id"]
        this_optional_attribute_id = request.POST["optional_attribute_id"]
        this_detail_id = request.POST["detail_id"]
        # set data
        this_product = Product.objects.get(ID = this_product_id)
        this_optional_attribute = OptinalAttribute.objects.get(id = this_optional_attribute_id)
        this_detail = Details.objects.get(id = this_detail_id)
        # check access level
        if (this_product.FK_Shop.FK_ShopManager == request.user) and (this_product.FK_OptinalAttribute.filter(id = this_optional_attribute_id).exists()):
            if this_optional_attribute.FK_Details.filter(id = this_detail_id).exists():
                # delete datails
                this_optional_attribute.FK_Details.remove(this_detail)
                this_detail.delete()
                # serializer data
                serializer = OptionalAttributeSerializer(this_optional_attribute)

                return JsonResponse({'status' : True, 'data' : serializer.data}, status = HTTP_200_OK)
            else:
                return JsonResponse({'status' : False, 'message' : 'The object with this ID does not exist'}, status = HTTP_404_NOT_FOUND)
        else:
            return JsonResponse({'status' : False, 'message' : 'You do not have access to do this'}, status = HTTP_403_FORBIDDEN)
    except Exception as e:
        return JsonResponse({'status' : False, 'message' : str(e)}, status = HTTP_500_INTERNAL_SERVER_ERROR)






# delete optional attribute //req : product id, optional attribute id // res: ({status : (True, False), massage : (system_message) }) OR err
@csrf_exempt
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def delete_optional_attribute(request):
    try:
        # get data
        this_product_id = request.POST["product_id"]
        this_optional_attribute_id = request.POST["optional_attribute_id"]
        # set data
        this_product = Product.objects.get(ID = this_product_id)
        this_optional_attribute = OptinalAttribute.objects.get(id = this_optional_attribute_id)
        # check access level
        if (this_product.FK_Shop.FK_ShopManager == request.user) and (this_product.FK_OptinalAttribute.filter(id = this_optional_attribute_id).exists()):
            # delete product attribute
            if Alert.objects.filter(FK_User = request.user, Part = '32', Slug = this_optional_attribute.id, Seen = True).exists():
                # change status
                this_optional_attribute.Publish = False
                this_optional_attribute.save()
                # set alert
                if not Alert.objects.filter(Part = '33', FK_User = request.user, Slug = this_optional_attribute.id).exists():
                    Alert.objects.create(Part = '33', FK_User = request.user, Slug = this_optional_attribute.id)
                
                return JsonResponse({'status' : True}, status = HTTP_200_OK)
            else:
                # delete alert
                this_alert = Alert.objects.get(FK_User = request.user, Part = '32', Slug = this_optional_attribute.id, Seen = False)
                this_alert.delete()
                # delete optional attribute
                for item in this_optional_attribute.FK_Details.all():
                    this_optional_attribute.FK_Details.remove(item)
                    item.delete()
                this_product.FK_OptinalAttribute.remove(this_optional_attribute)
                this_optional_attribute.delete()
                
            return JsonResponse({'status' : True}, status = HTTP_200_OK)
        else:
            return JsonResponse({'status' : False, 'message' : 'You do not have access to do this'}, status = HTTP_403_FORBIDDEN)
    except Exception as e:
        return JsonResponse({'status' : False, 'message' : str(e)}, status = HTTP_500_INTERNAL_SERVER_ERROR)







# edit optional attribute detail //req : product id, optional attribute id, detail id, detail information // res: ({status : (True, False), detail file, massage : (system_message) }) OR err
@csrf_exempt
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def edit_optional_attribute_detail(request):
    try:
        # get data
        this_product_id = request.POST["product_id"]
        this_optional_attribute_id = request.POST["optional_attribute_id"]
        this_detail_id = request.POST["detail_id"]
        this_value = request.POST["this_value"]
        this_price = request.POST["this_price"]
        this_weight = request.POST["this_weight"]
        this_length = request.POST["this_length"]
        this_width = request.POST["this_width"]
        this_height = request.POST["this_height"]
        this_inventory = request.POST["this_inventory"]
        this_status = request.POST["this_status"]
        # set data
        this_product = Product.objects.get(ID = this_product_id)
        this_optional_attribute = OptinalAttribute.objects.get(id = this_optional_attribute_id)
        this_detail = Details.objects.get(id = this_detail_id)
        # check access level
        if (this_product.FK_Shop.FK_ShopManager == request.user) and (this_product.FK_OptinalAttribute.filter(id = this_optional_attribute_id).exists()) and (this_optional_attribute.FK_Details.filter(id = this_detail_id).exists()):
            # change data
            if this_value != 'null':
                this_detail.Value = this_value
            if this_price != 'null':
                this_detail.Price = this_price
            if this_weight != 'null':
                this_detail.Weight = this_weight
            if this_length != 'null':
                this_detail.Length = this_length
            if this_width != 'null':
                this_detail.Width = this_width
            if this_height != 'null':
                this_detail.Height = this_height
            if this_inventory != 'null':
                this_detail.Inventory = this_inventory
            if this_status != 'null':
                this_detail.Status = this_status
            # save data
            this_detail.save()
            # serializer data
            serializer = OptionalAttributeSerializer(this_optional_attribute)
            
            return JsonResponse({'status' : True, 'data' : serializer.data}, status = HTTP_200_OK)
        else:
            return JsonResponse({'status' : False, 'message' : 'You do not have access to do this'}, status = HTTP_403_FORBIDDEN)
    except Exception as e:
        return JsonResponse({'status' : False, 'message' : str(e)}, status = HTTP_500_INTERNAL_SERVER_ERROR)






# edit optional attribute //req : product id, optional attribute id, optional attribute information // res: ({status : (True, False), optional attribute, massage : (system_message) }) OR err
@csrf_exempt
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def edit_optional_attribute(request):
    try:
        # get data
        this_product_id = request.POST["product_id"]
        this_optional_attribute_id = request.POST["optional_attribute_id"]
        this_type = request.POST["this_type"]
        this_status = request.POST["this_status"]
        # set data
        this_product = Product.objects.get(ID = this_product_id)
        this_optional_attribute = OptinalAttribute.objects.get(id = this_optional_attribute_id)
        # check access level
        if (this_product.FK_Shop.FK_ShopManager == request.user) and (this_product.FK_OptinalAttribute.filter(id = this_optional_attribute_id).exists()):
            # change optional attribute data
            if this_type != 'null':
                this_optional_attribute.Type = this_type
            if this_status != 'null':
                if this_status == '0':
                    this_status_bool = False
                elif this_status == '1':
                    this_status_bool = True
                this_optional_attribute.Status = this_status_bool
            this_optional_attribute.save()
            # serializer data
            serializer = OptionalAttributeSerializer(this_optional_attribute)
            
            return JsonResponse({'status' : True, 'data' : serializer.data}, status = HTTP_200_OK)
        else:
            return JsonResponse({'status' : False, 'message' : 'You do not have access to do this'}, status = HTTP_403_FORBIDDEN)
    except Exception as e:
        return JsonResponse({'status' : False, 'message' : str(e)}, status = HTTP_500_INTERNAL_SERVER_ERROR)







# edit product //req : product id // res: ({title : 'product_title', status = True or False}) OR err
@csrf_exempt
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def edit_product(request):
    try:
        # Get Data
        title = request.POST["product_title"]
        shop_id = request.POST["product_shop"]
        categories = request.POST["product_category"]
        submarket_id = request.POST["product_submarket"]
        price = request.POST["product_price"]
        oldprice = request.POST["product_oldprice"]
        send_type = request.POST["product_sendtype"]
        status = request.POST["product_status"]
        net_weight = request.POST["product_netweight"]
        packing_weight = request.POST["product_packingweight"]
        length = request.POST["product_length"]
        width = request.POST["product_width"]
        height = request.POST["product_height"]
        try:
            image = request.FILES["product_image"]
        except MultiValueDictKeyError:
            image = None
        try:
            description = request.POST["product_description"]
        except:
            description = None
        try:
            bio = request.POST["product_bio"]
        except:
            bio = None
        try:
            story = request.POST["product_story"]
        except:
            story = None
        try:
            within_range = request.POST["product_withinrange"]
        except:
            within_range = None
        try:
            out_of_range = request.POST["product_outofrange"]
        except:
            out_of_range = None
        try:
            inventory = request.POST["product_inventory"]
        except:
            inventory = None
        # get this product
        this_product = Product.objects.get(ID = request.POST["product_id"])
        # check access level
        if (this_product.FK_Shop.FK_ShopManager == request.user) and (Shop.objects.get(ID = shop_id).FK_ShopManager == request.user):
            # check alert
            edit_product_alert = None
            if not Alert.objects.filter(Part = '7', Slug = this_product.ID, Seen = False).exists():
                edit_product_alert = Alert.objects.create(FK_User = request.user, Part = '7', Slug = this_product.ID)
            else:
                edit_product_alert = Alert.objects.get(Part = '7', Slug = this_product.ID, Seen = False)
                edit_product_alert.FK_Field.all().delete()
            # check product title
            if this_product.Title != title:
                product_title_field = Field.objects.create(Title = 'Title', Value = title)
                edit_product_alert.FK_Field.add(product_title_field)
            # check product price
            if this_product.Price != price:
                product_price_field = Field.objects.create(Title = 'Price', Value = price)
                edit_product_alert.FK_Field.add(product_price_field)
            # check product oldprice
            if this_product.OldPrice != oldprice:
                product_oldprice_field = Field.objects.create(Title = 'OldPrice', Value = oldprice)
                edit_product_alert.FK_Field.add(product_oldprice_field)
            # check product send_type
            if this_product.PostRangeType != send_type:
                product_sendtype_field = Field.objects.create(Title = 'ProdRange', Value = send_type)
                edit_product_alert.FK_Field.add(product_sendtype_field)
            # check product status
            if this_product.Status != status:
                product_status_field = Field.objects.create(Title = 'ProdPostType', Value = status)
                edit_product_alert.FK_Field.add(product_status_field)
            # check product inventory
            if status == '1':
                # check product inventory
                if (inventory != None) and (this_product.Inventory != int(inventory)):
                    product_inventory_field = Field.objects.create(Title = 'ProdInStore', Value = inventory)
                    edit_product_alert.FK_Field.add(product_inventory_field)
            elif (status == '4') or (status == '3') or (status == '2'):
                # check product inventory
                product_inventory_field = Field.objects.create(Title = 'ProdInStore', Value = 0)
                edit_product_alert.FK_Field.add(product_inventory_field)
            # check product net_weight
            if this_product.Net_Weight != net_weight:
                product_netweight_field = Field.objects.create(Title = 'ProdNetWeight', Value = net_weight)
                edit_product_alert.FK_Field.add(product_netweight_field)
            # check product packing_weight
            if this_product.Weight_With_Packing != packing_weight:
                product_packingweight_field = Field.objects.create(Title = 'ProdPackingWeight', Value = packing_weight)
                edit_product_alert.FK_Field.add(product_packingweight_field)
            # check product length
            if this_product.Length_With_Packaging != length:
                product_length_field = Field.objects.create(Title = 'ProdLengthWithPackaging', Value = length)
                edit_product_alert.FK_Field.add(product_length_field)
            # check product width
            if this_product.Width_With_Packaging != width:
                product_width_field = Field.objects.create(Title = 'ProdWidthWithPackaging', Value = width)
                edit_product_alert.FK_Field.add(product_width_field)
            # check product height
            if this_product.Height_With_Packaging != height:
                product_height_field = Field.objects.create(Title = 'ProdHeightWithPackaging', Value = height)
                edit_product_alert.FK_Field.add(product_height_field)
            # check product shop
            if this_product.FK_Shop != Shop.objects.get(ID = shop_id):
                product_shop_field = Field.objects.create(Title = 'Shop', Value = shop_id)
                edit_product_alert.FK_Field.add(product_shop_field)
            # check product submarket
            if this_product.FK_SubMarket != SubMarket.objects.get(ID = submarket_id):
                product_submarket_field = Field.objects.create(Title = 'SubMarket', Value = submarket_id)
                edit_product_alert.FK_Field.add(product_submarket_field)
            # check product image
            if (image != '') and (image != None):
                this_product.NewImage = image
                this_product.save()
                new_image_string = 'NewImage' + '#' + str(this_product.NewImage)
                product_image_field = Field.objects.create(Title = 'Image', Value = new_image_string)
                edit_product_alert.FK_Field.add(product_image_field)
            # check product bio
            if (bio != '') and (bio != None) and (this_product.Bio != bio):
                product_bio_field = Field.objects.create(Title = 'Bio', Value = bio)
                edit_product_alert.FK_Field.add(product_bio_field)
            # check product description
            if (description != None) and (this_product.Description != description):
                product_description_field = Field.objects.create(Title = 'Description', Value = description)
                edit_product_alert.FK_Field.add(product_description_field)
            # check product story
            if (story != '') and (story != None) and (this_product.Story != story):
                product_story_field = Field.objects.create(Title = 'Story', Value = story)
                edit_product_alert.FK_Field.add(product_story_field)
            # check product categories
            product_category = categories.split('~')
            category_list = ''
            for item in product_category:
                category_list += item + '-'
            product_category_field = Field.objects.create(Title = 'Category', Value = category_list)
            edit_product_alert.FK_Field.add(product_category_field)
            # check product within range
            product_within = within_range.split('~')
            in_range_list = ''
            for item in product_within:
                if len(item) >= 1:
                    in_range_list += item + '-'
            if in_range_list:
                product_withinrange_field = Field.objects.create(Title = 'PostRange', Value = in_range_list)
                edit_product_alert.FK_Field.add(product_withinrange_field)
            else:
                product_withinrange_field = Field.objects.create(Title = 'PostRange', Value = 'remove')
                edit_product_alert.FK_Field.add(product_withinrange_field)
            # check product out of range
            product_Out = out_of_range.split('~')
            out_range_list = ''
            for item in product_Out:
                out_range_list += item + '-'
            if out_range_list:
                product_outrange_field = Field.objects.create(Title = 'ExePostRange', Value = out_range_list)
                edit_product_alert.FK_Field.add(product_outrange_field)
            else:
                product_outrange_field = Field.objects.create(Title = 'ExePostRange', Value = 'remove')
                edit_product_alert.FK_Field.add(product_outrange_field)
            # check edit
            if edit_product_alert.FK_Field.all().count() != 0:
                return JsonResponse({'title' : this_product.Title, 'status' : True}, status = HTTP_200_OK)
            else:
                edit_product_alert.delete()
                return JsonResponse({'title' : this_product.Title, 'status' : False}, status = HTTP_200_OK)
        else:
            return JsonResponse({'res' : 'You do not have access to do this'}, status = HTTP_403_FORBIDDEN)
    except Exception as e:
        return JsonResponse({'res' : str(e)}, status = HTTP_500_INTERNAL_SERVER_ERROR)






# check status of score //req : request.user  // res: data OR err
@csrf_exempt
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def check_status_of_score(request):
    # Chack User Factor
    if Factor.objects.filter(FK_User = request.user, PaymentStatus = True, Publish = True, Checkout = True).exists():
        # Get User Last Factor
        factor = Factor.objects.filter(FK_User = request.user, PaymentStatus = True, Publish = True, Checkout = True)[0]
        # Get All Factor Item
        order_item = []
        for item in factor.FK_FactorPost.all():
            order_item.append(item.FK_Product)
        # Return Data
        serializer = PointSerializer(order_item, many = True)
        return JsonResponse(serializer.data, status = HTTP_200_OK, safe = False)
    else:
        return JsonResponse({'res' : 'فاکتوری برای ثبت امتیاز ندارد...'}, status = HTTP_404_NOT_FOUND)




# get shop`s submarkets //req : request.user and shop_id// res: data OR err
@csrf_exempt
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def get_shop_submarkets(request):
    this_shop = Shop.objects.get(ID = request.POST["shop_id"])
    # set shop`s submarket list
    result = this_shop.FK_SubMarket.all()
    serializer = ShopSubMarketsSerializer(result , many = True)
    return JsonResponse(serializer.data, status = HTTP_200_OK, safe = False)




# get iran state //req : request.user// res: data OR err
@csrf_exempt
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_all_state(request):
    global users
    with open('Iran.json', encoding = 'utf8') as f:
        users = json.load(f)
    # Build Class
    class Items:
        def __init__(self, id, name):
            self.id = id
            self.name = name
        def toJSON(self):
            return json.dumps(self, default = lambda o: o.__dict__)
    # Set List
    result = []
    for i in users:
        if i['divisionType'] == 1:
            new = Items(i['id'], i['name'])
            result.append(json.loads(new.toJSON()))
    return JsonResponse(result, status = HTTP_200_OK, safe = False)



# get state`s bigcity //req : request.user// res: data OR err
@csrf_exempt
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def get_state_bigcity(request):
        
    this_id = request.POST.get('id')
    global users
    with open('Iran.json', encoding = 'utf8') as f:
        users = json.load(f)
    # Build Class
    class Items:
        def __init__(self, id, name):
            self.id = id
            self.name = name
        def toJSON(self):
            return json.dumps(self, default = lambda o: o.__dict__)
    # Set List
    result = []
    for i in users:
        if (i['divisionType'] == 2) and (i['parentCountryDivisionId'] == int(this_id)):
            new = Items(i['id'], i['name'])
            result.append(json.loads(new.toJSON()))
    return JsonResponse(result, status = HTTP_200_OK, safe = False)



# get bigcity`s city //req : request.user// res: data OR err
@csrf_exempt
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def get_bigcity_city(request):

    this_id = request.POST.get('id')
    global users
    with open('Iran.json', encoding = 'utf8') as f:
        users = json.load(f)
    # Build Class
    class Items:
        def __init__(self, id, name):
            self.id = id
            self.name = name
        def toJSON(self):
            return json.dumps(self, default = lambda o: o.__dict__)
    # Set List
    result = []
    global name
    for i in users:
        if (i['divisionType'] == 2) and (i['id'] == int(this_id)):
            name = i['name']
        if (i['divisionType'] == 3) and (i['parentCountryDivisionId'] == int(this_id)):
            if i['name'] == 'مرکزی':
                new = Items(i['id'], name)
            else:
                new = Items(i['id'], i['name'])
            result.append(json.loads(new.toJSON()))
    return JsonResponse(result, status = HTTP_200_OK, safe = False)




# product filter in shop //req : request.user// res: list of product OR err
@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
def filter_shop_products(request):
    try:
        shop_id = request.POST.get('id')
        status_id = request.POST.get('status')
        categories = request.POST.get('categories')
        search_text = request.POST.get('search_text')
        # get status
        if status_id == '0':
            status = False
        elif status_id == '1':
            status = True
        # get this shop
        this_shop = Shop.objects.get(ID = shop_id)
        # get categories
        category_list = []
        if categories != 'null':
            for item in categories.split('~'):
                if (item != '') and (Category.objects.filter(id = item).exists()):
                    category_list.append(Category.objects.get(id = item))
        else:
            category_list = this_shop.get_products_category()
        # change search text
        if search_text != 'null':
            words = search_text.split(' ')
            words = list(filter(lambda i: i!='', words))
            search_words = []
            for word in words:
                search_word = list(map(lambda x: x + '\s*', word.replace(' ','')[:-1]))
                search_word = ''.join(search_word) + word[-1]
                search_words.append(search_word)
            search_word = r'.*'.join(search_words)
            # get product
            if status:
                if len(category_list) != 0:
                    product_list = this_shop.get_products().filter(Title__regex = search_text, FK_Category__in = category_list, Status__in = ['1', '2', '3'])
                else:
                    product_list = this_shop.get_products().filter(Title__regex = search_text, Status__in = ['1', '2', '3'])
            else:
                product_list = []
                if len(category_list) != 0:
                    product_list += list(this_shop.get_products().filter(Title__regex = search_text, FK_Category__in = category_list, Status__in = ['1', '2', '3']))
                    product_list += list(this_shop.get_products().filter(Title__regex = search_text, FK_Category__in = category_list, Status = '4'))
                else:
                    product_list += list(this_shop.get_products().filter(Title__regex = search_text, Status__in = ['1', '2', '3']))
                    product_list += list(this_shop.get_products().filter(Title__regex = search_text, Status = '4'))
        else:
            # get product
            if status:
                if len(category_list) != 0:
                    product_list = this_shop.get_products().filter(FK_Category__in = category_list, Status__in = ['1', '2', '3'])
                else:
                    product_list = this_shop.get_products().filter(Status__in = ['1', '2', '3'])
            else:
                product_list = []
                if len(category_list) != 0:
                    product_list += list(this_shop.get_products().filter(FK_Category__in = category_list, Status__in = ['1', '2', '3']))
                    product_list += list(this_shop.get_products().filter(FK_Category__in = category_list, Status = '4'))
                else:
                    product_list += list(this_shop.get_products().filter(Status__in = ['1', '2', '3']))
                    product_list += list(this_shop.get_products().filter(Status = '4'))

        product_list = list(dict.fromkeys(product_list))
        print(len(product_list))
        print(status)
        print(category_list)
        serializer = ProductSerializer(product_list, many = True)
        return JsonResponse(serializer.data, status = HTTP_200_OK, safe = False)
    except Exception as e:
        return JsonResponse({'res' : str(e)}, status = HTTP_400_BAD_REQUEST)






# search in shop product //req : request.user, shop ID// res: list of product OR err
@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
def search_in_shop_products(request):
    try:
        shop_id = request.POST.get('id')
        search_text = request.POST.get('search_text')
        # change search text
        words = search_text.split(' ')
        search_words = []
        for word in words:
            search_word = list(map(lambda x: x + '\s*', word.replace(' ','')[:-1]))
            search_word = ''.join(search_word) + word[-1]
            search_words.append(search_word)
        search_text = r'.*'.join(search_words)
        # get this shop
        this_shop = Shop.objects.get(ID = shop_id)
        # get product
        product_list = []
        for item in this_shop.get_products().filter(Title__regex = search_text, Status__in = ['1', '2', '3']):
            product_list.append(item)
        for item in this_shop.get_products().filter(Title__regex = search_text, Status = '4'):
            product_list.append(item)
        product_list = list(dict.fromkeys(product_list))
        serializer = ProductSerializer(product_list, many = True)
        return JsonResponse(serializer.data, status = HTTP_200_OK, safe = False)
    except Exception as e:
        return JsonResponse({'res' : str(e)}, status = HTTP_400_BAD_REQUEST)