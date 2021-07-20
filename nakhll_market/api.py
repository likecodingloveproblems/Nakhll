from django.contrib.auth.models import User
from django.http.response import Http404
from django.shortcuts import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.exceptions import ValidationError
from nakhll_market.models import (
    Alert, AmazingProduct, Product, ProductBanner, Shop, Slider, Category, Market, State, BigCity, City, SubMarket
    )
from nakhll_market.serializers import (
    AmazingProductSerializer, ProductDetailSerializer, ProductImagesSerializer,
    ProductSerializer, ShopSerializer,SliderSerializer, ProductPriceWriteSerializer,
    CategorySerializer, FullMarketSerializer, CreateShopSerializer, ProductInventoryWriteSerializer,
    ProductListSerializer, ProductWriteSerializer, ShopAllSettingsSerializer,
    ShopBankAccountSettingsSerializer, SocialMediaAccountSettingsSerializer, ProductSubMarketSerializer, SubMarketSerializer
    )
from rest_framework import generics, routers, status, views, viewsets
from rest_framework import permissions, filters, mixins
from django.db.models import Q, F, Count
import random
from nakhll.authentications import CsrfExemptSessionAuthentication
from rest_framework.response import Response
from restapi.permissions import IsFactorOwner, IsProductOwner, IsShopOwner


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
    def perform_create(self, serializer):
        data = serializer.validated_data
        shop = data.get('FK_Shop')
        if shop.FK_ShopManager != self.request.user:
            raise ValidationError({'details': 'Shop is not own by user'})
        product_extra_fileds = {'Publish': True}
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
        shop = get_object_or_404(Shop, Slug=shop_slug)
        serializer = ShopSerializer(shop)
        return Response(serializer.data)




class CreateShop(generics.CreateAPIView):
    serializer_class = CreateShopSerializer
    permission_classes = [permissions.IsAuthenticated, ]
    authentication_classes = [CsrfExemptSessionAuthentication, ]
    def get_queryset(self):
        return Shop.objects.filter(FK_ShopManager=self.request.user)
    def perform_create(self, serializer):
        super().perform_create(serializer)
        # TODO: REFACTOR: Replace state, bigcity and city id to string in front side,
        # TODO: REFACTOR: and this gets do not need anymore
        state_id = serializer.validated_data.get('State')
        bigcity_id = serializer.validated_data.get('BigCity')
        city_id = serializer.validated_data.get('City')

        state = get_object_or_404(State, id=state_id)
        bigcity = get_object_or_404(BigCity, id=bigcity_id)
        city = get_object_or_404(City, id=city_id)


        new_shop = serializer.save(FK_ShopManager=self.request.user, Publish=True, State=state.name, BigCity=bigcity.name, City=city.name)
        Alert.objects.create(Part='2', FK_User=self.request.user, Slug=new_shop.ID)







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
class AddSubMarketToProduct(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [CsrfExemptSessionAuthentication, ]
    def post(self, request, format=None):
        try:
            serializer = ProductSubMarketSerializer(request.data)
            product_id = serializer.data.get('product')
            submarket_ids = serializer.data.get('submarkets', [])
            product = Product.objects.get(ID=product_id)
            self.check_object_permissions(request, product)
            for submarket_id in submarket_ids:
                submarket = SubMarket.objects.get(id=submarket_id)
                submarket.Product_SubMarket.add(product)

            # TODO: Check if created product alert display images and submarkets
            # TODO: or I should create an alert for submarkets and images

            return Response({'details': 'done'}, status=status.HTTP_200_OK)
        except:
            return Response({'details': 'Bad Request'}, status=status.HTTP_400_BAD_REQUEST)

class AddImageToProduct(views.APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [CsrfExemptSessionAuthentication, ]
    def post(self, request, format=None):
        try:
            serializer = ProductImagesSerializer(data=request.data)
            if serializer.is_valid() and 'images' in request.FILES:
                product_id = serializer.validated_data.get('product')
                images = request.FILES.getlist('images')
                product = Shop.objects.get(ID=product_id)

                product = Product.objects.get(ID=product_id)
                self.check_object_permissions(request, product)
                
                # Save first image in product.NewImage
                product_main_image = images[0]
                product.NewImage = product_main_image
                product.save()

                # Save all images in product.Product_Banner
                # Set Alert for each image
                for image in images:
                    product_banner = ProductBanner.objects.create(FK_Product=product, Image=image)
                    Alert.objects.create(Part='8', FK_User=request.user, Slug=product_banner.id)


                return Response({'details': 'done'}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'details': 'Bad Request'}, status=status.HTTP_400_BAD_REQUEST)


class ShopMultipleUpdatePrice(views.APIView):
    #TODO: Swap OldPrice and Price
    permission_classes = [permissions.IsAuthenticated, ]
    authentication_classes = [CsrfExemptSessionAuthentication, ]
    def patch(self, request, format=None):
        serializer = ProductPriceWriteSerializer(data=request.data, many=True)
        user = request.user
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
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AllShopSettings(views.APIView):
    # TODO: Check this class entirely
    permission_classes = [permissions.IsAuthenticated, IsShopOwner]
    authentication_classes = [CsrfExemptSessionAuthentication,]
    def get_object(self, shop_slug, user):
        return get_object_or_404(Shop, Slug=shop_slug)
    def get(self, request, shop_slug, format=None):
        user = request.user
        shop = self.get_object(shop_slug, user)
        self.check_object_permissions(request, shop)
        serializer = ShopAllSettingsSerializer(shop)
        return Response(serializer.data)

    def put(self, request, shop_slug, format=None):
        user = request.user
        shop = self.get_object(shop_slug, user)
        self.check_object_permissions(request, shop)
        serializer = ShopAllSettingsSerializer(data=request.data, instance=shop)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data)

class BankAccountShopSettings(views.APIView):
    # TODO: Check this class entirely
    permission_classes = [permissions.IsAuthenticated, ]
    authentication_classes = [CsrfExemptSessionAuthentication,]
    def get_object(self, shop_slug, user):
        return get_object_or_404(Shop, Slug=shop_slug)
    def put(self, request, shop_slug, format=None):
        user = request.user
        shop = self.get_object(shop_slug, user)
        self.check_object_permissions(request, shop)
        serializer = ShopBankAccountSettingsSerializer(data=request.data, instance=shop)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data)

class SocialMediaShopSettings(views.APIView):
    # TODO: Check this class entirely
    permission_classes = [permissions.IsAuthenticated, ]
    authentication_classes = [CsrfExemptSessionAuthentication,]
    def get_object(self, shop_slug, user):
        return get_object_or_404(Shop, Slug=shop_slug)
    def put(self, request, shop_slug, format=None):
        user = request.user
        shop = self.get_object(shop_slug, user)
        self.check_object_permissions(request, shop)
        serializer = SocialMediaAccountSettingsSerializer(data=request.data, instance=shop)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data)
