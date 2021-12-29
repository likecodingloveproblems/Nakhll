from django.db.models.expressions import F
from django.http.response import Http404
from excel_response import ExcelResponse
from rest_framework.exceptions import ValidationError
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import ugettext as _
from rest_framework import serializers, status, mixins, permissions, viewsets
from rest_framework.decorators import action, authentication_classes, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from nakhll_market.models import Shop
from payoff.exceptions import NoAddressException, InvoiceExpiredException,\
            InvalidInvoiceStatusException, OutOfPostRangeProductsException
from .models import ShopFeature, ShopFeatureInvoice, ShopLanding, PinnedURL
from .serializers import (ShopFeatureDetailSerializer, ShopFeatureInvoice, ShopFeatureInvoiceSerializer,
                         ShopFeatureInvoiceWriteSerializer, ShopFeatureSerializer, ShopLandingDetailsSerializer, ShopLandingSerializer, UserPinnedURLSerializer, )
from .permissions import IsShopOwner, IsPinnedURLOwner, ShopLandingPermission
from .mixins import MultipleFieldLookupMixin


class ShopFeatureViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.ListModelMixin):
    queryset = ShopFeature.objects.published()
    serializer_class = ShopFeatureSerializer
    permission_classes = [permissions.AllowAny, ]

    def get_serializer_class(self):
        if self.action == 'list':
            return ShopFeatureSerializer
        else:
            return ShopFeatureDetailSerializer



class ShopFeatureInvoiceViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.DestroyModelMixin):
    permission_classes = [permissions.IsAuthenticated, IsShopOwner]
    queryset = ShopFeatureInvoice.objects.all()
    lookup_field = 'id'
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ShopFeatureInvoiceWriteSerializer

    @action(detail=False, methods=['get'], url_path='(?P<shop_slug>[^/.]+)/history')
    def shop_feature_invoices_history(self, request, shop_slug):
        feature_id = request.query_params.get('feature')
        shop = self.get_shop(shop_slug)
        invoices = ShopFeatureInvoice.objects.filter(shop=shop)
        if feature_id:
            invoices = invoices.filter(feature__id=feature_id)
        serializer = ShopFeatureInvoiceSerializer(invoices, many=True)
        return Response(serializer.data)


    @action(detail=False, methods=['post'])
    def activate_demo(self, request):
        serializer = ShopFeatureInvoiceWriteSerializer(data=request.data)
        if serializer.is_valid(is_demo=True):
            feature = serializer.validated_data.get('feature')
            invoice = serializer.save(is_demo=True, status=ShopFeatureInvoice.ShopFeatureInvoiceStatuses.COMPLETED,
                                        bought_price_per_unit=feature.price_per_unit_with_discount,
                                        bought_unit=feature.unit, unit_count=1, 
                                        start_datetime=timezone.now())
            invoice.save_expire_datetime()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

    def perform_create(self, serializer):
        feature = serializer.validated_data.get('feature')
        serializer.save(is_demo=False, status=ShopFeatureInvoice.ShopFeatureInvoiceStatuses.AWAIT_PAYMENT,
                            bought_price_per_unit=feature.price_per_unit_with_discount,
                            bought_unit=feature.unit, unit_count=1) 

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status != ShopFeatureInvoice.ShopFeatureInvoiceStatuses.AWAIT_PAYMENT:
            return Response({'error': 'شما نمی‌توانید این فاکتور را پاک کنید'}, status=status.HTTP_400_BAD_REQUEST)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['get'])
    def pay(self, request, id=None):
        invoice = self.get_object()
        if invoice.status != ShopFeatureInvoice.ShopFeatureInvoiceStatuses.AWAIT_PAYMENT:
            return Response({'error': 'شما نمی‌توانید این فاکتور را پرداخت کنید'}, status=status.HTTP_400_BAD_REQUEST)
        return invoice.send_to_payment()

    def get_shop(self, shop_slug):
        try:
            shop = Shop.objects.get(Slug=shop_slug)
            self.check_object_permissions(self.request, shop)
            return shop
        except Shop.DoesNotExist as ex:
            raise Http404
            

class ShopLandingViewSet(MultipleFieldLookupMixin, mixins.RetrieveModelMixin,
                            mixins.ListModelMixin, mixins.CreateModelMixin,
                            mixins.DestroyModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = ShopLanding.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsShopOwner, ShopLandingPermission]
    lookup_fields = ['shop__Slug', 'pk']

    def get_serializer_class(self):
        if self.action == 'list':
            return ShopLandingSerializer
        else:
            return ShopLandingDetailsSerializer

    def get_shop(self):
        shop_slug = self.kwargs.get('shop__Slug')
        return get_object_or_404(Shop, Slug=shop_slug, FK_ShopManager=self.request.user)

    def get_queryset(self):
        return super().get_queryset().filter(shop__FK_ShopManager=self.request.user, **self.kwargs)

    @action(detail=True, methods=['get'], )
    def activate_landing(self, request, shop__Slug, pk=None):
        shop_landing = self.get_object()
        ShopLanding.objects.deactivate_all_landing_for_shop(shop_landing.shop)
        shop_landing.status = ShopLanding.Statuses.ACTIVE
        shop_landing.save()
        return Response(status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        shop = self.get_shop()
        serializer.save(shop=shop)

    def perform_update(self, serializer):
        shop = self.get_shop()
        serializer.save(shop=shop)


class PinnedURLViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin,
                            mixins.ListModelMixin, mixins.CreateModelMixin,
                            mixins.DestroyModelMixin):
    queryset = PinnedURL.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsPinnedURLOwner]
    serializer_class = UserPinnedURLSerializer

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    

class ShopViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated, IsShopOwner]
    queryset = Shop.objects.all()
    lookup_field = 'Slug'
    
    @action(detail=True, methods=['get'])
    def products_as_excel(self, request, Slug=None):
        shop = self.get_object()
        shop_products = shop.ShopProduct.annotate(
                عنوان=F('Title'),
                بارکد=F('barcode'),
                قیمت=F('Price'),
                قیمت_قبل=F('OldPrice'),
                موجودی=F('Inventory'),
                وزن=F('Net_Weight'),
                وزن_با_بسته_بندی=F('Weight_With_Packing'),
                دسته_بندی=F('new_category_id'),
                وضعیت_انتشار=F('Publish'),
            ).values(
                'عنوان',
                'بارکد',
                'قیمت',
                'قیمت_قبل',
                'وزن',
                'وزن_با_بسته_بندی',
                'موجودی',
                'دسته_بندی',
                'وضعیت_انتشار',
        )
        return ExcelResponse(data=shop_products)