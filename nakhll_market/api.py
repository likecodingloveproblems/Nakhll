import random
from django.contrib.postgres.aggregates.general import ArrayAgg
import pandas as pd
from django.shortcuts import get_object_or_404
from django.http import response
from django.http.response import Http404
from django.db.models import Q, F, Count, Value, BooleanField
from django.db.models.aggregates import Sum, Max, Min
from django.db.models.expressions import Case, When
from django.db.models.functions import Cast
from django.contrib.auth.models import User
from django.utils.text import slugify
from rest_framework import generics, routers, status, views, viewsets
from rest_framework import permissions, filters, mixins, serializers
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, PermissionDenied, AuthenticationFailed
from rest_framework.decorators import action
from django_filters import rest_framework as restframework_filters
from logistic.models import ShopLogisticUnit
from nakhll.utils import excel_response, get_dict
from nakhll_market.exceptions import UnPublishedProductException, UnPublishedShopException
from nakhll_market.interface import DiscordAlertInterface, ProductChangeTypes
from nakhll_market.models import (
    Alert,
    Comment,
    Category,
    Product,
    ProductBanner,
    Shop,
    Slider,
    State,
    BigCity,
    City,
    LandingPageSchema,
    ShopPageSchema,
    UserImage, Tag, ProductTag,
)
from nakhll_market.resources import ShopStatisticResource
from nakhll_market.serializers import (
    Base64ImageSerializer,
    CategoryProductCountSerializer,
    NewProfileSerializer,
    ProductBannerWithProductSerializer,
    ProductCommentSerializer,
    ProductDetailSerializer,
    ProductImagesSerializer,
    ProductOwnerListSerializer,
    ProductOwnerReadSerializer,
    ProductOwnerWriteSerializer,
    ProductPriceWriteSerializer,
    ProductSerializer,
    ShopSerializer,
    ShopSimpleSerializer,
    ShopSlugSerializer,
    CreateShopSerializer,
    ProductInventoryWriteSerializer,
    ProductListSerializer,
    ShopAllSettingsReadSerializer,
    ShopAllSettingsWriteSerializer,
    SliderSerializer,
    UserOrderSerializer,
    StateFullSeraializer,
    ShopPageSchemaSerializer,
    UserImageSerializer,
    LandingPageSchemaSerializer,
    CategoryChildSerializer,
    CategoryParentSerializer, TagOwnerListSerializer)
from restapi.permissions import IsProductOwner, IsShopOwner, IsProductBannerOwner, IsTagOwner
from restapi.serializers import ProfileSerializer
from invoice.models import Invoice
from nakhll_market.filters import ProductFilter
from nakhll_market.permissions import IsInvoiceOwner
from nakhll_market.paginators import StandardPagination
from nakhll_market.product_bulk_operations import BulkException, BulkProductHandler
from shop.mixins import MultipleFieldLookupMixin
from shop.serializers import ShopLandingDetailsSerializer, ShopLandingSerializer


class LastCreatedProductsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Return Prodocts that are created recently"""
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny, ]

    def get_queryset(self):
        return Product.objects.get_last_created_products()


class LastCreatedDiscountedProductsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Return discounted Prodocts that are created recently"""
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny, ]

    def get_queryset(self):
        return Product.objects.get_last_created_discounted_products()


class RandomShopsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Return random shops"""
    serializer_class = ShopSerializer
    permission_classes = [permissions.AllowAny, ]

    def get_queryset(self):
        return Shop.objects.get_random_shops()


class RandomProductsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Return random products"""
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny, ]

    def get_queryset(self):
        return Product.objects.get_random_products()


class MostDiscountPrecentageProductsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Return products that have highest discount precentage"""
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny, ]

    def get_queryset(self):
        return Product.objects.get_most_discount_precentage_products()


class MostSoldShopsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Return most sold shops"""
    serializer_class = ShopSerializer
    permission_classes = [permissions.AllowAny, ]

    def get_queryset(self):
        return Shop.objects.most_last_week_sale_shops()


class SliderViewSet(viewsets.ReadOnlyModelViewSet):
    """Model viewset for all sliders that are published"""
    serializer_class = SliderSerializer
    permission_classes = [permissions.AllowAny, ]
    search_fields = ('Location',)
    filter_backends = (filters.SearchFilter,)
    queryset = Slider.objects.filter(Publish=True)


class ShopProductsViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.ListModelMixin):
    """Return one or all products of a shop that are published"""
    serializer_class = ProductListSerializer
    permission_classes = [permissions.AllowAny, ]
    product_slug = None
    lookup_field = 'FK_Shop__Slug'

    def get_queryset(self):
        filter_query = {
            self.lookup_field: self.product_slug,
            'Publish': True,
            'Available': True}
        return Product.objects.filter(**filter_query).order_by('?')[:20]

    def retrieve(self, request, *args, **kwargs):
        self.product_slug = self.kwargs.get(self.lookup_field)
        return self.list(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        if not self.product_slug:
            raise Http404
        return super().list(request, *args, **kwargs)


class ShopOwnerProductViewSet(viewsets.GenericViewSet,
                              mixins.RetrieveModelMixin,
                              mixins.CreateModelMixin,
                              mixins.ListModelMixin,
                              mixins.UpdateModelMixin):
    """ModelViewset for products that are owned by a shop"""
    permission_classes = [permissions.IsAuthenticated, IsProductOwner]
    pagination_class = StandardPagination
    filter_class = ProductFilter
    filter_backends = (
        restframework_filters.DjangoFilterBackend,
        filters.OrderingFilter)
    lookup_field = 'ID'

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductOwnerListSerializer
        elif self.action == 'retrieve':
            return ProductOwnerReadSerializer
        else:
            return ProductOwnerWriteSerializer

    def get_queryset(self):
        shop = self.get_shop()
        return Product.objects.filter(FK_Shop=shop).order_by('-DateCreate')

    def get_shop(self):
        shop = get_object_or_404(Shop, Slug=self.kwargs.get('shop_slug'))
        self.__check_shop_owner(shop)
        return shop

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())

        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        obj = get_object_or_404(queryset, **filter_kwargs)

        self.check_object_permissions(self.request, obj)
        return obj

    def perform_create(self, serializer):
        """Create a new product

        Check if price have dicount or not. Swap Price and OldPrice value if discount exists.
        Note that, the requester should use OldPrice as price_with_discount, if discount exists. Then we convert price
        and old price from Toman to Rial to store in DB. We also create an alert for staff to check the product.
        """
        shop = self.get_shop()
        data = serializer.validated_data
        title = data.get('Title')

        slug = self.__generate_unique_slug(title)
        product_extra_fileds = {'Publish': True, 'Slug': slug, 'FK_Shop': shop}
        old_price = data.get('OldPrice', 0) * 10
        price = data.get('Price', 0) * 10
        if old_price:
            product = serializer.save(
                OldPrice=price,
                Price=old_price,
                **product_extra_fileds)
        else:
            product = serializer.save(
                OldPrice=old_price,
                Price=price,
                **product_extra_fileds)

        Alert.objects.create(
            Part='6',
            FK_User=self.request.user,
            Slug=product.ID)
        try:
            DiscordAlertInterface.product_alert(
                product, change_type=ProductChangeTypes.CREATE)
        except BaseException:
            DiscordAlertInterface.product_alert(
                product, change_type=ProductChangeTypes.CREATE,
                without_image=True)

    def perform_update(self, serializer):
        """Update a product

        Check if price have dicount or not. Swap Price and OldPrice value if discount exists.
        Note that, the requester should use OldPrice as price_with_discount, if discount exists. Then we convert price
        and old price from Toman to Rial to store in DB. We also create an alert for staff to check the product.
        """
        shop = self.get_shop()
        data = serializer.validated_data
        ID = self.kwargs.get('ID')
        old_price = data.get('OldPrice', 0) * 10
        price = data.get('Price', 0) * 10
        if old_price:
            product = serializer.save(
                OldPrice=price, Price=old_price, FK_Shop=shop)
        else:
            product = serializer.save(
                OldPrice=old_price, Price=price, FK_Shop=shop)

        Alert.objects.create(Part='7', FK_User=self.request.user, Slug=ID)
        try:
            DiscordAlertInterface.product_alert(
                product, change_type=ProductChangeTypes.UPDATE)
        except BaseException:
            DiscordAlertInterface.product_alert(
                product, change_type=ProductChangeTypes.UPDATE,
                without_image=True)

    def __check_shop_owner(self, shop):
        if shop.FK_ShopManager != self.request.user:
            raise serializers.ValidationError(
                {'FK_Shop': f'شما به فروشگاه {shop.Title} دسترسی ندارید'},
                code=status.HTTP_403_FORBIDDEN
            )

    def __generate_unique_slug(self, title):
        """Generate new unique slug for Product Model"""
        slug = slugify(title, allow_unicode=True)
        counter = 1
        new_slug = slug
        while (Product.objects.filter(Slug=new_slug).exists()):
            new_slug = f'{slug}_{counter}'
            counter += 1
        return new_slug


class TagsOwnerViewSet(viewsets.GenericViewSet,
                       mixins.RetrieveModelMixin, mixins.ListModelMixin, ):
    permission_classes = [permissions.IsAuthenticated, IsTagOwner]
    serializer_class = TagOwnerListSerializer

    def get_queryset(self):
        shop = self.get_shop()
        return Tag.objects.filter(shop=shop)

    def get_shop(self):
        shop = get_object_or_404(Shop, Slug=self.kwargs.get('shop_slug'))
        self.__check_shop_owner(shop)
        return shop

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())

        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        obj = get_object_or_404(queryset, **filter_kwargs)

        self.check_object_permissions(self.request, obj)
        return obj

    def __check_shop_owner(self, shop):
        if shop.FK_ShopManager != self.request.user:
            raise serializers.ValidationError(
                {'FK_Shop': f'شما به فروشگاه {shop.Title} دسترسی ندارید'},
                code=status.HTTP_403_FORBIDDEN
            )


class ProductsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Product viewset for end user with filter and search capabilities."""
    pagination_class = StandardPagination
    filter_class = ProductFilter
    filter_backends = (
        restframework_filters.DjangoFilterBackend,
        filters.OrderingFilter)
    serializer_class = ProductListSerializer
    permission_classes = [permissions.AllowAny, ]
    ordering_fields = ('Title', 'Price', 'DiscountPrecentage', 'DateCreate',)

    def get_queryset(self):
        res = Product.objects.filter(Publish=True, FK_Shop__Publish=True).\
            select_related('FK_Shop').annotate(
            is_available=Cast(
                Case(
                    When(
                        Q(Status__in=(1, 2, 3)) &
                        Q(Inventory__gt=0),
                        then=Value(True)),
                    default=Value(False)),
                output_field=BooleanField())).annotate(
            DiscountPrecentage=Case(
                When(
                    OldPrice__gt=0,
                    then=((F('OldPrice') - F('Price')) * 100 / F('OldPrice'))),
                default=0)).order_by(
            '-is_available', '-category_id')
        search_query = self.request.query_params.get('search', None)
        q_query = self.request.query_params.get('q', None)
        if search_query:
            query = res.filter(Title__icontains=search_query)
        elif q_query:
            query = res.filter(Title__icontains=q_query)
        else:
            query = res
        self.max_price = query.aggregate(Max('Price'))['Price__max']
        self.min_price = query.aggregate(Min('Price'))['Price__min']
        return res

    def get_paginated_response(self, data):
        res = super().get_paginated_response(data)
        res.data['max_price'] = self.max_price
        res.data['min_price'] = self.min_price
        return res


class ProductDetailsViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """Product details viewset for end user."""
    serializer_class = ProductDetailSerializer
    permission_classes = [permissions.AllowAny, ]
    lookup_field = 'Slug'
    queryset = Product.objects.select_related('FK_Shop')

    def get_object(self):
        product = super().get_object()
        if not product.FK_Shop.Publish or not product.Publish:
            raise UnPublishedProductException()
        return product


class ProductCommentsViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """List of comments for product for end user."""
    serializer_class = ProductCommentSerializer
    permission_classes = [permissions.AllowAny, ]
    lookup_field = 'FK_Product__Slug'
    product_slug = None

    def get_queryset(self):
        filter_query = {self.lookup_field: self.product_slug, 'FK_Pater': None}
        return Comment.objects.filter(
            **filter_query).select_related('FK_Product')

    def retrieve(self, request, *args, **kwargs):
        self.product_slug = self.kwargs.get(self.lookup_field)
        return self.list(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        if not self.product_slug:
            raise Http404
        return super().list(request, *args, **kwargs)


class ProductRelatedItemsViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """List of related products which are available for a product for end user. We get related products by category."""
    pagination_class = StandardPagination
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny, ]
    lookup_field = 'Slug'
    product = None

    def get_queryset(self):
        queryset = Product.objects.filter(Available=True, Publish=True,
                                          Status__in=['1', '2', '3'])
        if self.product and self.product.category:
            queryset = queryset.filter(category=self.product.category)
        return queryset.order_by('?')

    def retrieve(self, request, *args, **kwargs):
        self.product = get_object_or_404(
            Product, Slug=self.kwargs.get(
                self.lookup_field))
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


class GetShopWithSlug(views.APIView):
    """Return shop details with slug"""
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, ]

    def get(self, request, format=None):
        shop_slug = request.GET.get('slug')
        shop = get_object_or_404(Shop, Slug=shop_slug)
        serializer = ShopSerializer(shop)
        return Response(serializer.data)


class GetShop(viewsets.GenericViewSet, mixins.RetrieveModelMixin):
    """Return shop details with slug"""
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, ]
    serializer_class = ShopSerializer
    queryset = Shop.objects.all()
    lookup_field = 'Slug'

    def get_object(self):
        shop = super().get_object()
        if not shop.Publish:
            raise UnPublishedShopException()
        return shop


class GetShopList(viewsets.GenericViewSet, mixins.ListModelMixin):
    """Return list of shops with their details"""
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, ]
    serializer_class = ShopSimpleSerializer
    queryset = Shop.objects.filter(
        Available=True, Publish=True).select_related(
        'FK_ShopManager', 'FK_ShopManager__User_Profile', )


class CreateShop(generics.CreateAPIView):
    """Create shop api

    Slugs for a shop are automatically generated from the name of the shop.
    """
    serializer_class = CreateShopSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    def get_queryset(self):
        return Shop.objects.filter(FK_ShopManager=self.request.user)

    def generate_unique_slug(self, title):
        """Generate new unique slug for Shop Model based on title and using a counter."""
        slug = slugify(title, allow_unicode=True)
        counter = 1
        new_slug = slug
        while (Shop.objects.filter(Slug=new_slug).exists()):
            new_slug = f'{slug}_{counter}'
            counter += 1
        return new_slug

    def perform_create(self, serializer):
        # super().perform_create(serializer)
        # TODO: REFACTOR: Replace state, bigcity and city id to string in front side,
        # TODO: REFACTOR: and this gets do not need anymore
        shop_manager = serializer.validated_data.pop('FK_ShopManager')
        fname = shop_manager.get('first_name')
        lname = shop_manager.get('last_name')
        self.request.user.first_name = fname
        self.request.user.last_name = lname
        self.request.user.save()
        state = serializer.validated_data.get('State')
        bigcity = serializer.validated_data.get('BigCity')
        city = serializer.validated_data.get('City')
        title = serializer.validated_data.get('Title')
        slug = serializer.validated_data.get('Slug')
        if not slug:
            slug = self.generate_unique_slug(title)
        elif Shop.objects.filter(Slug=slug).exists():
            raise ValidationError({'details': 'شناسه حجره از قبل موجود است'})

        new_shop = serializer.save(
            FK_ShopManager=self.request.user,
            Publish=True,
            State=state,
            BigCity=bigcity,
            City=city,
            Slug=slug)
        ShopLogisticUnit.objects.generate_shop_logistic_units(new_shop)
        Alert.objects.create(
            Part='2',
            FK_User=self.request.user,
            Slug=new_shop.ID)


class CheckShopSlug(views.APIView):
    """Check if shop slug is available or not. We used to use this api before, but now we automatically generate slug for a shop."""
    permission_classes = [permissions.IsAuthenticated, ]

    def get(self, request, format=None):
        shop_slug = request.GET.get('slug')
        try:
            shop = Shop.objects.get(Slug=shop_slug)
            return Response({'shop_slug': shop.ID})
        except Shop.DoesNotExist:
            return Response({'shop_slug': None})


class CheckProductSlug(views.APIView):
    """Check if product slug is available or not. We used to use this api before, but now we automatically generate slug for a product."""
    permission_classes = [permissions.IsAuthenticated, ]

    def get(self, request, format=None):
        product_slug = request.GET.get('slug')
        try:
            product = Product.objects.get(Slug=product_slug)
            return Response({'product_slug': product.ID})
        except Product.DoesNotExist:
            return Response({'product_slug': None})


class AddImagesToProduct(views.APIView):
    """Add images to product as secondary images"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format=None):
        try:
            serializer = ProductImagesSerializer(data=request.data)
            # if serializer.is_valid() and 'images' in request.FILES:
            if serializer.is_valid():
                product_id = serializer.validated_data.get('product')
                images = serializer.validated_data.get('images')
                product = Product.objects.get(ID=product_id)
                self.check_object_permissions(request, product)

                product_main_image = images[0]
                product.Image = product_main_image
                product.save()

                # Save all images in product.Product_Banner
                # Set Alert for each image
                for image in images:
                    product_banner = ProductBanner.objects.create(
                        FK_Product=product, Image=image, Publish=True)
                    Alert.objects.create(
                        Part='8', FK_User=request.user, Slug=product_banner.id)

                return Response({'details': 'done'}, status=status.HTTP_200_OK)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        except BaseException:
            return Response(
                {'details': 'Bad Request'},
                status=status.HTTP_400_BAD_REQUEST)


class ProductBannerViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin,
                           mixins.DestroyModelMixin):
    """Viewset for creating and deleting product images. We also generate an alert for creation of new product image."""
    permission_classes = [permissions.IsAuthenticated, IsProductBannerOwner]
    lookup_field = 'id'
    queryset = ProductBanner.objects.all()
    serializer_class = ProductBannerWithProductSerializer

    def perform_create(self, serializer):
        product_banner = serializer.save(Publish=True)
        Alert.objects.create(Part='8', FK_User=self.request.user,
                             Slug=product_banner.id)


class ShopMultipleUpdatePrice(views.APIView):
    """Allow shop owner to update price of multiple products at once.

    Shop owner can update Price and OldPrice of many products using product_slug property.
    We use OldPrice as price with discount in front side and swap them in this api.
    """
    permission_classes = [permissions.IsAuthenticated, ]

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
                        if old_price:
                            product.OldPrice = price
                            product.Price = old_price
                        else:
                            product.OldPrice = old_price
                            product.Price = price
                        ready_for_update_products.append(product)

                except BaseException:
                    pass
            Product.objects.bulk_update(
                ready_for_update_products, [
                    'Price', 'OldPrice'])
            return Response({'details': 'done'})
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


class ShopMultipleUpdateInventory(views.APIView):
    """Allow shop owner to update inventory of multiple products at once.

    Shop owner can update Inventory of many products using product_slug property.
    """
    permission_classes = [permissions.IsAuthenticated, ]

    def patch(self, request, format=None):
        serializer = ProductInventoryWriteSerializer(
            data=request.data, many=True)
        user = request.user
        if serializer.is_valid():
            price_list = serializer.data
            ready_for_update_products = []
            for inventory_item in price_list:
                try:
                    product = Product.objects.get(
                        Slug=inventory_item.get('Slug'))
                    inventory = inventory_item.get('Inventory')
                    if product.FK_Shop.FK_ShopManager == user:
                        product.Inventory = inventory
                        ready_for_update_products.append(product)
                except BaseException:
                    pass
            Product.objects.bulk_update(
                ready_for_update_products, ['Inventory'])
            return Response({'details': 'done'})
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


class AllShopSettings(views.APIView):
    """Allow shop owner to update all settings of shop at once."""
    serializer_class = ShopAllSettingsReadSerializer
    permission_classes = [permissions.IsAuthenticated, IsShopOwner]

    def get_object(self, shop_slug, user):
        return get_object_or_404(Shop, Slug=shop_slug)

    def get(self, request, shop_slug, format=None):
        user = request.user
        shop = self.get_object(shop_slug, user)
        self.check_object_permissions(request, shop)
        serializer = ShopAllSettingsReadSerializer(shop)
        return Response(serializer.data)

    def patch(self, request, shop_slug, format=None):
        user = request.user
        shop = self.get_object(shop_slug, user)
        self.check_object_permissions(request, shop)
        serializer = ShopAllSettingsWriteSerializer(
            data=request.data, instance=shop, context={'user': user})
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data)


class DeleteShopImage(views.APIView):
    """Allow shop owner to delete shop image."""
    permission_classes = [permissions.IsAuthenticated, IsShopOwner]

    def get_object(self, shop_slug, user):
        return get_object_or_404(Shop, Slug=shop_slug)

    def delete(self, request, shop_slug, format=None):
        user = request.user
        shop: Shop = self.get_object(shop_slug, user)
        self.check_object_permissions(request, shop)
        shop.delete_image()
        return Response({'status': 'عکس با موفقیت حذف شد'},
                        status=status.HTTP_204_NO_CONTENT)


class ImageShopSettings(views.APIView):
    """Allow shop owner to update shop image."""
    permission_classes = [permissions.IsAuthenticated, ]

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
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data)


class StateFullViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    """Return list of all states with big cities and cities."""
    permission_classes = [permissions.AllowAny, ]
    queryset = State.objects.all()
    serializer_class = StateFullSeraializer


class UserProfileViewSet(viewsets.GenericViewSet):
    """View and update user profile."""
    permission_classes = [permissions.IsAuthenticated, ]
    queryset = User.objects.all()
    serializer_class = ProfileSerializer

    @action(detail=False, methods=['get', 'patch'])
    def me(self, request):
        user = request.user
        serializer = NewProfileSerializer(user.User_Profile)
        return Response(serializer.data)

    @action(detail=False, methods=['patch'])
    def edit_me(self, request):
        user = request.user
        serializer = NewProfileSerializer(user.User_Profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['patch'])
    def extend_referral_link_expiration_date(self, request):
        profile = request.user.User_Profile
        profile.extend_referral_link()
        return Response('')


class UserOrderHistory(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    """Return list of all invoices of user."""
    permission_classes = [permissions.IsAuthenticated, IsInvoiceOwner]
    queryset = Invoice.objects.all()
    serializer_class = UserOrderSerializer

    def get_queryset(self):
        return Invoice.objects.filter(cart__user=self.request.user)


class UserImagesViewSet(viewsets.ModelViewSet):
    """Viewset for user profile image."""
    permission_classes = [permissions.IsAuthenticated]
    queryset = UserImage.objects.all()
    serializer_class = UserImageSerializer

    def get_queryset(self):
        return super().get_queryset().filter(profile__FK_User=self.request.user)

    def perform_create(self, serializer):
        serializer.save(profile=self.request.user.User_Profile)


class LandingPageSchemaViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    """Return all published landing page schemas for Nakhll."""
    permission_classes = [permissions.AllowAny, ]
    serializer_class = LandingPageSchemaSerializer

    def get_queryset(self):
        return LandingPageSchema.objects.get_published_schema(self.request)


class ShopPageSchemaViewSet(views.APIView):
    """Return all published landing page schemas for given shop."""
    permission_classes = [permissions.AllowAny, ]
    serializer_class = ShopPageSchemaSerializer

    def get_object(self, shop_id):
        return get_object_or_404(Shop, Slug=shop_id)

    def get(self, request, shop_id, format=None):
        shops = ShopPageSchema.objects.get_published_schema(
            self.request, shop_id)
        serializer = ShopPageSchemaSerializer(shops, many=True)
        return Response(serializer.data)


class GroupProductCreateExcel(views.APIView):
    """Create many products from excel file using :class:`BulkProductHandler` class"""
    permission_classes = [permissions.IsAuthenticated, IsShopOwner]
    bulk_type = BulkProductHandler.BULK_TYPE_CREATE

    def get_object(self, shop_slug):
        shop = get_object_or_404(Shop, Slug=shop_slug)
        self.check_object_permissions(self.request, shop)
        return shop

    def post(self, request, shop_slug, format=None):
        shop = self.get_object(shop_slug)
        csv_file = request.FILES.get('product-excel-upload')
        if not csv_file:
            raise ValidationError('هیچ فایلی جهت بارگذاری انتخاب نشده است')
        zip_file = request.FILES.get('product-zip-file')
        bulk_product_handler = BulkProductHandler(
            shop=shop, images_zip_file=zip_file, bulk_type=self.bulk_type)
        try:
            result = bulk_product_handler.parse_csv(csv_file)
        except BulkException as ex:
            return Response(str(ex), status=status.HTTP_400_BAD_REQUEST)
        return Response(result)


class GroupProductUpdateExcel(GroupProductCreateExcel, views.APIView):
    """Update many products from excel file using :class:`BulkProductHandler` class"""
    permission_classes = [permissions.IsAuthenticated, IsShopOwner]
    bulk_type = BulkProductHandler.BULK_TYPE_UPDATE


class GroupProductUndo(views.APIView):
    """Undo bulk product operation."""
    permission_classes = [permissions.IsAuthenticated, IsShopOwner]

    def get_object(self, shop_slug):
        shop = get_object_or_404(Shop, Slug=shop_slug)
        self.check_object_permissions(self.request, shop)
        return shop

    def get(self, request, shop_slug, format=None):
        shop = self.get_object(shop_slug)
        bulk_product_handler = BulkProductHandler(
            shop=shop, is_undo_operation=True)
        try:
            result = bulk_product_handler.undo_last_changes()
        except BulkException as ex:
            return Response(str(ex), status=status.HTTP_400_BAD_REQUEST)
        return Response(result)


class MostSoldProduct(views.APIView):
    """Return most sold products of shop."""
    permission_classes = [permissions.AllowAny, ]
    serializer_class = ProductSerializer

    def get_object(self):
        return Product.objects.get_most_sold_product()

    def get(self, request, format=None):
        product = self.get_object()
        serializer = ProductSerializer(product, many=True)
        return Response(serializer.data)


class CategoryViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    """Represents categories in Nakhll system

    You can specify how deep you want to get categories by defining max_depth query string parameter. No max_depth
    or max_depth=-1 means that you will get all categories.
    """
    permission_classes = [permissions.AllowAny, ]
    queryset = Category.objects.all_ordered()
    serializer_class = CategoryParentSerializer
    lookup_field = 'slug'

    def get_queryset(self):
        if self.action == 'list':
            self.serializer_class = CategoryChildSerializer
            return Category.objects.get_root_categories()
        return Category.objects.all_ordered()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        try:
            max_depth = int(self.request.query_params.get('max_depth', -1))
        except ValueError:
            max_depth = -1
        context['max_depth'] = max_depth
        return context

    @action(methods=['GET'], detail=False)
    def category_product_count(self, request):
        """Without any query string, it gives you all categories with their product count. You can narrow down the
        categories by specifying a search parameter as q which search in product name, and/or a shop_slug parameter,
        which only gives you categories of a specific shop.
        """
        product_title_query = request.GET.get('q', None)
        shop = request.GET.get('shop', None)
        queryset = Category.objects.categories_with_product_count(
            product_title_query,
            shop)
        return Response(
            CategoryProductCountSerializer(
                queryset, many=True).data)


class PublicShopsViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    """Return all public shops."""
    permission_classes = [permissions.AllowAny, ]
    serializer_class = ProductSerializer

    def get_queryset(self):
        return Shop.objects.public_shops().annotate(
            products_slug=ArrayAgg('ShopProduct__Slug'))

    def list(self, request, *args, **kwargs):
        shops = self.get_queryset()
        serializer = ShopSlugSerializer(shops, many=True)
        return Response(serializer.data)


class ShopsStatisticView(views.APIView):
    """Return shops statistic."""
    permission_classes = [permissions.IsAdminUser, ]

    def get(self, request):
        return excel_response(ShopStatisticResource,
                              filename='shop-statistics')
