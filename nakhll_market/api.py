from django.contrib.auth.models import User
from django.db.models.expressions import Case, When
from django.db.models import Value, IntegerField
from django.http import response
from django.http.response import Http404
from django.shortcuts import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.exceptions import ValidationError, PermissionDenied, AuthenticationFailed
from nakhll_market.models import (
    Alert, AmazingProduct, Comment, Product, ProductBanner, Shop, Slider, Category, Market, State, BigCity, City, SubMarket
    )
from nakhll_market.serializers import (
    AmazingProductSerializer, Base64ImageSerializer, ProductCommentSerializer, ProductDetailSerializer, ProductImagesSerializer,
    ProductSerializer, ProductUpdateSerializer, ShopProductSerializer, ShopSerializer,SliderSerializer, ProductPriceWriteSerializer,
    CategorySerializer, FullMarketSerializer, CreateShopSerializer, ProductInventoryWriteSerializer,
    ProductListSerializer, ProductWriteSerializer, ShopAllSettingsSerializer, ProductBannerSerializer,
    ShopBankAccountSettingsSerializer, SocialMediaAccountSettingsSerializer, ProductSubMarketSerializer, StateFullSeraializer, SubMarketSerializer
    )
from rest_framework import generics, routers, status, views, viewsets
from rest_framework import permissions, filters, mixins
from django.db.models import Q, F, Count
import random
from nakhll.authentications import CsrfExemptSessionAuthentication
from rest_framework.response import Response
from django.utils.text import slugify
from restapi.permissions import IsFactorOwner, IsProductOwner, IsShopOwner, IsProductBannerOwner
from nakhll_market.paginators import StandardPagination
from nakhll_market.filters import ProductFilter
from django_filters import rest_framework as restframework_filters


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

class ShopProductsViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.ListModelMixin):
    serializer_class = ShopProductSerializer
    permission_classes = [permissions.AllowAny, ]
    product_slug = None
    lookup_field = 'FK_Shop__Slug'

    def get_queryset(self):
        filter_query = {self.lookup_field: self.product_slug, 'Publish': True, 'Available': True}
        return Product.objects.filter(**filter_query)

    def retrieve(self, request, *args, **kwargs):
        self.product_slug = self.kwargs.get(self.lookup_field)
        return self.list(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        if not self.product_slug:
            raise Http404
        return super().list(request, *args, **kwargs)
     



class UserProductViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.CreateModelMixin,
                         mixins.ListModelMixin, mixins.UpdateModelMixin):
    permission_classes = [permissions.IsAuthenticated, IsProductOwner]
    authentication_classes = [CsrfExemptSessionAuthentication, ]
    queryset = Product.objects.all().order_by('-DateCreate')
    lookup_field = 'ID'

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return ProductUpdateSerializer
        elif self.action in ['list', 'retrieve']:
            return ProductListSerializer
        else:
            return ProductWriteSerializer


    def generate_unique_slug(self, title):
        ''' Generate new unique slug for Product Model 
            NOTE: This fucntion should move to utils
        '''
        slug = slugify(title, allow_unicode=True)
        counter = 1
        new_slug = slug
        while(Product.objects.filter(Slug=new_slug).exists()):
            new_slug = f'{slug}_{counter}'
            counter += 1
        return new_slug

    def perform_create(self, serializer):
        data = serializer.validated_data
        shop = data.get('FK_Shop')
        title = data.get('Title')

        # Check if target shop is owned by user or not
        if shop.FK_ShopManager != self.request.user:
            raise ValidationError({'details': 'Shop is not own by user'})

        slug = self.generate_unique_slug(title)
        product_extra_fileds = {'Publish': True, 'Slug': slug}
        # TODO: This behavior should be inhanced later
        #! Check if price have dicount or not
        #! Swap Price and OldPrice value if discount exists
        #! Note that, request should use OldPrice as price with discount
        # Convert price and old price from Toman to Rial to store in DB
        old_price = data.get('OldPrice', 0) * 10
        price = data.get('Price', 0) * 10
        if old_price:
            product = serializer.save(OldPrice=price, Price=old_price, **product_extra_fileds)
        else:
            product = serializer.save(OldPrice=old_price, Price=price, **product_extra_fileds)
        # TODO: Check if product created successfully and published and alerts created as well
        Alert.objects.create(Part='6', FK_User=self.request.user, Slug=product.ID)

    def perform_update(self, serializer):
        data = serializer.validated_data
        ID = self.kwargs.get('ID')

        # TODO: This behavior should be inhanced later
        #! Check if price have dicount or not
        #! Swap Price and OldPrice value if discount exists
        #! Note that, request should use OldPrice as price with discount
        # Convert price and old price from Toman to Rial to store in DB
        old_price = data.get('OldPrice', 0) * 10
        price = data.get('Price', 0) * 10
        if old_price:
            product = serializer.save(OldPrice=price, Price=old_price)
        else:
            product = serializer.save(OldPrice=old_price, Price=price)

        # TODO: Check if product created successfully and published and alerts created as well
        Alert.objects.create(Part='7', FK_User=self.request.user, Slug=ID)


class ProductsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    pagination_class = StandardPagination
    filter_class = ProductFilter
    filter_backends = (restframework_filters.DjangoFilterBackend, filters.OrderingFilter)
    serializer_class = ProductListSerializer
    permission_classes = [permissions.AllowAny, ]
    ordering_fields = ('Title', 'Price', 'DiscountPrecentage', 'DateCreate', )

    def get_queryset(self):
        queryset = Product.objects.select_related('FK_SubMarket', 'FK_Shop')
        queryset = queryset.annotate(DiscountPrecentage=Case(
            When(OldPrice__gt=0, then=(
                (F('OldPrice') - F('Price')) * 100 / F('OldPrice'))
            ),
            default=0)
        )
        return queryset


class ProductDetailsViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = ProductDetailSerializer
    permission_classes = [permissions.AllowAny, ]
    lookup_field = 'Slug'
    queryset = Product.objects.select_related('FK_SubMarket', 'FK_Shop')

class ProductCommentsViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = ProductCommentSerializer
    permission_classes = [permissions.AllowAny, ]
    lookup_field = 'FK_Product__Slug'
    product_slug = None
    def get_queryset(self):
        filter_query = {self.lookup_field: self.product_slug, 'FK_Pater': None}
        return Comment.objects.filter(**filter_query).select_related('FK_Product')

    def retrieve(self, request, *args, **kwargs):
        self.product_slug = self.kwargs.get(self.lookup_field)
        return self.list(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        if not self.product_slug:
            raise Http404
        return super().list(request, *args, **kwargs)
        

class ProductRelatedItemsViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    pagination_class = StandardPagination
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny, ]
    lookup_field = 'Slug'
    product = None

    def get_queryset(self):
        return Product.objects.filter(
                    Available = True, Publish = True, Status__in = ['1', '2', '3'],
                    FK_Category__in = self.product.FK_Category.all())

    def retrieve(self, request, *args, **kwargs):
        self.product = Product.objects.get(Slug=self.kwargs.get(self.lookup_field))
        return self.list(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        if not self.product:
            raise Http404
        return super().list(request, *args, **kwargs)


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

    def generate_unique_slug(self, title):
        ''' Generate new unique slug for Shop Model 
            NOTE: This fucntion should move to utils
        '''
        slug = slugify(title, allow_unicode=True)
        counter = 1
        new_slug = slug
        while(Shop.objects.filter(Slug=new_slug).exists()):
            new_slug = f'{slug}_{counter}'
            counter += 1
        return new_slug

    def perform_create(self, serializer):
        # super().perform_create(serializer)
        # TODO: REFACTOR: Replace state, bigcity and city id to string in front side,
        # TODO: REFACTOR: and this gets do not need anymore
        state_id = serializer.validated_data.get('State')
        bigcity_id = serializer.validated_data.get('BigCity')
        city_id = serializer.validated_data.get('City')
        title = serializer.validated_data.get('Title')
        slug = serializer.validated_data.get('Slug')
        if not slug:
            slug = self.generate_unique_slug(title)
        elif Shop.objects.filter(Slug=slug).exists():
            raise ValidationError({'details': 'شناسه حجره از قبل موجود است'})

        state = get_object_or_404(State, id=state_id)
        bigcity = get_object_or_404(BigCity, id=bigcity_id)
        city = get_object_or_404(City, id=city_id)

        new_shop = serializer.save(FK_ShopManager=self.request.user, Publish=True, 
                                State=state.name, BigCity=bigcity.name, City=city.name, Slug=slug)
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
            serializer = ProductSubMarketSerializer(data=request.data)
            if serializer.is_valid():
                product_id = serializer.data.get('product')
                submarket_ids = serializer.data.get('submarkets', [])
                product = Product.objects.get(ID=product_id)
                self.check_object_permissions(request, product)
                for submarket_id in submarket_ids:
                    submarket = SubMarket.objects.get(ID=submarket_id)
                    submarket.Product_SubMarket.add(product)

                # TODO: Check if created product alert display images and submarkets
                # TODO: or I should create an alert for submarkets and images

                return Response({'details': 'done'}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'details': 'Bad Request'}, status=status.HTTP_400_BAD_REQUEST)

class AddImagesToProduct(views.APIView):
    # parser_classes = (MultiPartParser, FormParser)
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [CsrfExemptSessionAuthentication, ]
    def post(self, request, format=None):
        try:
            serializer = ProductImagesSerializer(data=request.data)
            # if serializer.is_valid() and 'images' in request.FILES:
            if serializer.is_valid():
                product_id = serializer.validated_data.get('product')
                images = serializer.validated_data.get('images')
                product = Product.objects.get(ID=product_id)
                self.check_object_permissions(request, product)
                
                # Save first image in product.NewImage
                product_main_image = images[0]
                product.Image = product_main_image
                product.save()

                # Save all images in product.Product_Banner
                # Set Alert for each image
                for image in images:
                    product_banner = ProductBanner.objects.create(FK_Product=product, Image=image, Publish=True)
                    Alert.objects.create(Part='8', FK_User=request.user, Slug=product_banner.id)


                return Response({'details': 'done'}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'details': 'Bad Request'}, status=status.HTTP_400_BAD_REQUEST)

class ProductBannerViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin, 
                        mixins.DestroyModelMixin):
    permission_classes = [permissions.IsAuthenticated, IsProductBannerOwner]
    authentication_classes = [CsrfExemptSessionAuthentication, ]
    lookup_field = 'id'
    queryset = ProductBanner.objects.all()
    serializer_class = ProductBannerSerializer

    def perform_create(self, serializer):
        product_banner = serializer.save(Publish=True)
        Alert.objects.create(Part='8', FK_User=self.request.user,
                             Slug=product_banner.id)


class ShopMultipleUpdatePrice(views.APIView):
    #TODO: Swap OldPrice and Price
    permission_classes = [permissions.IsAuthenticated,]
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
                        # TODO: This behavior should be inhanced later
                        #! Check if price have dicount or not
                        #! Swap Price and OldPrice value if discount exists
                        #! Note that, request should use OldPrice as price with discount
                        if old_price:
                            product.OldPrice = price
                            product.Price = old_price
                        else:
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


class ImageShopSettings(views.APIView):
    permission_classes = [permissions.IsAuthenticated, ]
    authentication_classes = [CsrfExemptSessionAuthentication,]
    def get_object(self, shop_slug):
        return get_object_or_404(Shop, Slug=shop_slug)
    def put(self, request, shop_slug, format=None):
        shop = self.get_object(shop_slug)
        self.check_object_permissions(request, shop)
        serializer = Base64ImageSerializer(data=request.data)
        if serializer.is_valid():
            image = serializer.validated_data.get('image')
            shop.Image = image
            shop.save()
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data)


class StateFullViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    permission_classes = [permissions.AllowAny, ]
    queryset = State.objects.all()
    serializer_class = StateFullSeraializer