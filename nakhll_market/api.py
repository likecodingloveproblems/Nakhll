from django.contrib.auth.models import User
from django.http.response import Http404
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.exceptions import ValidationError
from nakhll_market.models import (
    Alert, AmazingProduct, Product, ProductBanner, Shop, Slider, Category, Market
    )
from nakhll_market.serializers import (
    AmazingProductSerializer, ProductDetailSerializer, ProductImagesSerializer,
    ProductSerializer, ShopSerializer,SliderSerializer, ProductPriceWriteSerializer,
    CategorySerializer, FullMarketSerializer, CreateShopSerializer, ProductInventoryWriteSerializer,
    ProductListSerializer, ProductCategorySerializer, ProductWriteSerializer, ShopAllSettingsSerializer,
    ShopBankAccountSettingsSerializer, SocialMediaAccountSettingsSerializer,
    )
from rest_framework import generics, routers, status, views, viewsets
from rest_framework import permissions, filters, mixins
from django.db.models import Q, F, Count
import random
from nakhll.authentications import CsrfExemptSessionAuthentication
from rest_framework.response import Response
from django.utils.text import slugify


class SliderViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SliderSerializer
    permission_classes = [permissions.AllowAny, ]
    search_fields = ('Location', )
    filter_backends = (filters.SearchFilter,)
    queryset = Slider.objects.filter(Publish=True)
    

class CategoryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny, ]

    def get_queryset(self):
        return Category.objects.get_category_publush_avaliable()

class AmazingProductViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = AmazingProductSerializer
    permission_classes = [permissions.AllowAny, ]

    def get_queryset(self):
        return AmazingProduct.objects.get_amazing_products()

class LastCreatedProductsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny, ]

    def get_queryset(self):
        return Product.objects.get_last_created_products()

class LastCreatedDiscountedProductsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny, ]

    def get_queryset(self):
        return Product.objects.get_last_created_discounted_products()

class RandomShopsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = ShopSerializer
    permission_classes = [permissions.AllowAny, ]

    def get_queryset(self):
        return Shop.objects.get_random_shops()

class RandomProductsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny, ]

    def get_queryset(self):
        return Product.objects.get_random_products()

class MostDiscountPrecentageProductsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny, ]

    def get_queryset(self):
        return Product.objects.get_most_discount_precentage_products()

class MostSoldShopsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = ShopSerializer
    permission_classes = [permissions.AllowAny, ]

    def get_queryset(self):
        return Shop.objects.most_last_week_sale_shops()


class UserProductViewSet(mixins.RetrieveModelMixin, mixins.CreateModelMixin, mixins.ListModelMixin,
                            viewsets.GenericViewSet, mixins.UpdateModelMixin):
    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return ProductListSerializer
        else:
            return ProductWriteSerializer
    def get_queryset(self):
        queryset = Product.objects.filter(FK_Shop__FK_ShopManager=self.request.user).order_by('-DateCreate')
        return queryset

    def generate_unique_slug(title):
        ''' Generate new unique slug for Product Model 
            NOTE: This fucntion should move to utils
        '''
        slug = slugify(title, allow_unicode=True)
        counter = 1
        new_slug = slug
        while(Product.objects.get(Slug=new_slug)):
            new_slug = f'{slug}_{counter}'
            counter += 1
        return new_slug

    def perform_create(self, serializer):
        data = serializer.validated_data
        shop = data.get('FK_Shop')
        title = data.get('Title')
        if shop.FK_ShopManager != self.request.user:
            raise ValidationError({'details': 'Shop is not own by user'})
        slug = self.generate_unique_slug(title)
        product_extra_fileds = {'Publish': True, 'Slug': slug}
        # TODO: This behavior should be inhanced later
        #! Check if price have dicount or not
        #! Swap Price and OldPrice value if discount exists
        #! Note that, request should use OldPrice as price with discount
        old_price = data.get('OldPrice')
        if old_price:
            price = data.get('Price')
            product = serializer.save(OldPrice=price, Price=old_price, **product_extra_fileds)
        else:
            product = serializer.save(**product_extra_fileds)
        # TODO: Check if product created successfully and published and alerts created as well
        Alert.objects.create(Part='7', FK_User=self.request.user, Slug=product.ID)
    permission_classes = [permissions.IsAuthenticated, ]
    authentication_classes = [CsrfExemptSessionAuthentication, ]
    lookup_field = 'Slug'


class ProductFullDetailsViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = ProductDetailSerializer
    permission_classes = [permissions.AllowAny, ]
    lookup_field = 'Slug'
    queryset = Product.objects.select_related('FK_SubMarket', 'FK_Shop')



class ProductsInSameFactorViewSet(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny, ]

    def get_queryset(self):
        id = self.kwargs.get('ID')
        return Product.objects.get_products_in_same_factor(id)
 
 
class MarketList(generics.ListAPIView):
    serializer_class = FullMarketSerializer
    permission_classes = [permissions.AllowAny, ]
    queryset = Market.objects.filter(Available=True, Publish=True)


class GetShopWithSlug(views.APIView):
    permission_classes = [permissions.IsAuthenticated, ]
    authentication_classes = [CsrfExemptSessionAuthentication, ]

    def get(self, request, format=None):
        shop_slug = request.GET.get('slug')
        try:
            shop = Shop.objects.get(Slug=shop_slug)
        except Shop.DoesNotExist:
            raise Http404
        serializer = ShopSerializer(shop)
        return Response(serializer.data)

    def patch(self, request, instance, format=None):
        # TODO: Search for patch function in Internet
        pass





class CreateShop(generics.CreateAPIView):
    serializer_class = CreateShopSerializer
    permission_classes = [permissions.IsAuthenticated, ]
    authentication_classes = [CsrfExemptSessionAuthentication, ]
    def get_queryset(self):
        return Shop.objects.filter(FK_ShopManager=self.request.user)
    def perform_create(self, serializer):
        super().perform_create(serializer)
        serializer.save(FK_ShopManager=self.request.user)

                # TODO: Create Alerts
                #
                #
                #







class CheckShopSlug(views.APIView):
    permission_classes = [permissions.IsAuthenticated, ]
    def get(self, request, format=None):
        shop_slug = request.GET.get('slug')
        try:
            shop = Shop.objects.get(Slug=shop_slug)
            return Response({'shop_slug': shop.ID})
        except Shop.DoesNotExist:
            return Response({'shop_slug': None})
class CheckProductSlug(views.APIView):
    permission_classes = [permissions.IsAuthenticated, ]
    def get(self, request, format=None):
        product_slug = request.GET.get('slug')
        try:
            product = Product.objects.get(Slug=product_slug)
            return Response({'product_slug': product.ID})
        except Product.DoesNotExist:
            return Response({'product_slug': None})
class AddCategoryToProduct(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [CsrfExemptSessionAuthentication, ]
    def post(self, request, format=None):
        try:
            serializer = ProductCategorySerializer(request.data)
            product_slug = serializer.data.get('product')
            categories_id = serializer.data.get('categories', [])
            product = Product.objects.get(Slug=product_slug)
            product_owner = product.FK_Shop.FK_ShopManager
            if product_owner != request.user:
                return Response({'details': 'Access Denied'}, status=status.HTTP_401_UNAUTHORIZED)
            for category_id in categories_id:
                category = Category.objects.get(id=category_id)
                product.FK_Category.add(category)

                # TODO: Create Alerts
                #
                #
                #

            return Response({'details': 'done'}, status=status.HTTP_200_OK)
        except:
            return Response({'details': 'Bad Request'}, status=status.HTTP_400_BAD_REQUEST)
    def get(self, request, format=None):
        cats = Category.objects.all()
        ser = CategorySerializer(cats, many=True)
        return Response(ser.data)

class AddImageToProduct(views.APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [CsrfExemptSessionAuthentication, ]
    def post(self, request, format=None):
        try:
            serializer = ProductImagesSerializer(data=request.data)
            if serializer.is_valid() and 'images' in request.FILES:
                product_slug = serializer.validated_data.get('product')
                images = request.FILES.getlist('images')
                product = Shop.objects.get(Slug=product_slug)
                product_owner = product.FK_Shop.FK_ShopManager
                if product_owner != request.user:
                    return Response({'details': 'Access Denied'}, status=status.HTTP_401_UNAUTHORIZED)
                
                # Save first image in product.NewImage
                product_main_image = images[0]
                product.NewImage = product_main_image
                product.save()

                # Save all images in product.Product_Banner
                for image in images:
                    ProductBanner.objects.create(FK_Product=product, Image=image)

                # TODO: Create Alerts
                #
                #
                #

                return Response({'details': 'done'}, status=status.HTTP_200_OK)
            return Response(serializer.errors)
        except:
            return Response({'details': 'Bad Request'}, status=status.HTTP_400_BAD_REQUEST)


class ShopMultipleUpdatePrice(views.APIView):
    permission_classes = [permissions.IsAuthenticated, ]
    authentication_classes = [CsrfExemptSessionAuthentication, ]
    def patch(self, request, format=None):
        serializer = ProductPriceWriteSerializer(data=request.data, many=True)
        user = request.user
        # user = User.objects.get(id=72)
        if serializer.is_valid():
            price_list = serializer.data
            ready_for_update_products = []
            for price_item in price_list:
                try:
                    product = Product.objects.get(Slug=price_item.get('Slug'))
                    old_price = price_item.get('OldPrice')
                    price = price_item.get('Price')
                    if product.FK_Shop.FK_ShopManager == user:
                        product.OldPrice = old_price
                        product.Price = price
                        ready_for_update_products.append(product)
                except:
                    pass
            Product.objects.bulk_update(ready_for_update_products, ['Price', 'OldPrice'])
            return Response({'details': 'done'})
        else:
            return Response(serializer.errors)

class ShopMultipleUpdateInventory(views.APIView):
    permission_classes = [permissions.IsAuthenticated, ]
    authentication_classes = [CsrfExemptSessionAuthentication, ]
    def patch(self, request, format=None):
        serializer = ProductInventoryWriteSerializer(data=request.data, many=True)
        user = request.user
        # user = User.objects.get(id=72)
        if serializer.is_valid():
            price_list = serializer.data
            ready_for_update_products = []
            for inventory_item in price_list:
                try:
                    product = Product.objects.get(Slug=inventory_item.get('Slug'))
                    inventory = inventory_item.get('Inventory')
                    if product.FK_Shop.FK_ShopManager == user:
                        product.Inventory = inventory
                        ready_for_update_products.append(product)
                except:
                    pass
            Product.objects.bulk_update(ready_for_update_products, ['Inventory'])
            return Response({'details': 'done'})
        else:
            return Response(serializer.errors)

class AllShopSettings(views.APIView):
    permission_classes = [permissions.IsAuthenticated, ]
    authentication_classes = [CsrfExemptSessionAuthentication,]
    def get_object(self, shop_slug, user):
        try:
            return Shop.objects.get(Slug=shop_slug, FK_ShopManager=user)
        except:
            raise Http404
    def get(self, request, shop_slug, format=None):
        user = request.user
        # TODO: Remove This user
        user = User.objects.get(id=72)
        shop = self.get_object(shop_slug, user)
        serializer = ShopAllSettingsSerializer(shop)
        return Response(serializer.data)

    def put(self, request, shop_slug, format=None):
        user = request.user
        # TODO: Remove This user
        user = User.objects.get(id=72)
        shop = self.get_object(shop_slug, user)
        serializer = ShopAllSettingsSerializer(data=request.data, instance=shop)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(serializer.errors)
        return Response(serializer.data)

class BankAccountShopSettings(views.APIView):
    permission_classes = [permissions.IsAuthenticated, ]
    authentication_classes = [CsrfExemptSessionAuthentication,]
    def get_object(self, shop_slug, user):
        try:
            return Shop.objects.get(Slug=shop_slug, FK_ShopManager=user)
        except:
            raise Http404
    def put(self, request, shop_slug, format=None):
        user = request.user
        # TODO: Remove This user
        user = User.objects.get(id=72)
        shop = self.get_object(shop_slug, user)
        serializer = ShopBankAccountSettingsSerializer(data=request.data, instance=shop)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(serializer.errors)
        return Response(serializer.data)

class SocialMediaShopSettings(views.APIView):
    permission_classes = [permissions.IsAuthenticated, ]
    authentication_classes = [CsrfExemptSessionAuthentication,]
    def get_object(self, shop_slug, user):
        try:
            return Shop.objects.get(Slug=shop_slug, FK_ShopManager=user)
        except:
            raise Http404
    def put(self, request, shop_slug, format=None):
        user = request.user
        # TODO: Remove This user
        user = User.objects.get(id=72)
        shop = self.get_object(shop_slug, user)
        serializer = SocialMediaAccountSettingsSerializer(data=request.data, instance=shop)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(serializer.errors)
        return Response(serializer.data)
