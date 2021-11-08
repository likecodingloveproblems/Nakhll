from django.http.response import Http404
from rest_framework.exceptions import ValidationError
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import ugettext as _
from rest_framework import serializers, status, mixins, permissions, viewsets
from rest_framework.decorators import action, authentication_classes, permission_classes
from rest_framework.response import Response
from nakhll.authentications import CsrfExemptSessionAuthentication
from nakhll_market.models import Shop
from payoff.exceptions import NoAddressException, InvoiceExpiredException,\
            InvalidInvoiceStatusException, OutOfPostRangeProductsException
from .models import ShopFeature, ShopFeatureInvoice, ShopLanding, PinnedURL
from .serializers import (ShopFeatureDetailSerializer, ShopFeatureInvoice, ShopFeatureInvoiceSerializer,
                         ShopFeatureInvoiceWriteSerializer, ShopFeatureSerializer, ShopLandingDetailsSerializer, ShopLandingSerializer, UserPinnedURLSerializer, )
from .permissions import IsShopOwner, IsPinnedURLOwner


class ShopFeatureViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.ListModelMixin):
    queryset = ShopFeature.objects.published()
    serializer_class = ShopFeatureSerializer
    permission_classes = [permissions.AllowAny, ]
    authentication_classes = [CsrfExemptSessionAuthentication, ]

    def get_serializer_class(self):
        if self.action == 'list':
            return ShopFeatureSerializer
        else:
            return ShopFeatureDetailSerializer



class ShopFeatureInvoiceViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.DestroyModelMixin):
    permission_classes = [permissions.IsAuthenticated, IsShopOwner]
    authentication_classes = [CsrfExemptSessionAuthentication, ]
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
                                        bought_price_per_unit=0, bought_unit=feature.unit, unit_count=1, 
                                        start_datetime=timezone.now())
            invoice.save_expire_datetime()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


    def perform_create(self, serializer):
        feature = serializer.validated_data.get('feature')
        serializer.save(is_demo=False, status=ShopFeatureInvoice.ShopFeatureInvoiceStatuses.AWAIT_PAYMENT,
                            bought_price_per_unit=0, bought_unit=feature.unit, unit_count=1) 

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
            

class ShopLandingViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin,
                            mixins.ListModelMixin, mixins.CreateModelMixin,
                            mixins.DestroyModelMixin, mixins.UpdateModelMixin):
    queryset = ShopLanding.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsShopOwner]
    authentication_classes = [CsrfExemptSessionAuthentication, ]

    def get_serializer_class(self):
        if self.action == 'list':
            return ShopLandingSerializer
        else:
            return ShopLandingDetailsSerializer

    def get_queryset(self):
        return super().get_queryset().filter(shop__FK_ShopManager=self.request.user)

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(detail=True, methods=['get'])
    def activate_landing(self, request, pk=None):
        shop_landing = self.get_object()
        ShopLanding.objects.deactivate_all_landing_for_shop(shop_landing.shop)
        shop_landing.status = ShopLanding.Statuses.ACTIVE
        shop_landing.save()
        return Response(status=status.HTTP_200_OK)


class PinnedURLViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin,
                            mixins.ListModelMixin, mixins.CreateModelMixin,
                            mixins.DestroyModelMixin):
    queryset = PinnedURL.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsPinnedURLOwner]
    authentication_classes = [CsrfExemptSessionAuthentication, ]
    serializer_class = UserPinnedURLSerializer

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    

