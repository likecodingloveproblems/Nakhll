from django.db.models import constraints
from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework import serializers, status, permissions, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from logistic.managers import AddressManager
from django.utils.translation import ugettext as _
from logistic.models import Address, LogisticUnitGeneralSetting, ShopLogisticUnit, ShopLogisticUnitConstraint, ShopLogisticUnitCalculationMetric
from logistic.serializers import (AddressSerializer, ShopLogisticUnitCalculationMetricSerializer,
                                  ShopLogisticUnitConstraintReadSerializer, ShopLogisticUnitSerializer,
                                  ShopLogisticUnitConstraintWriteSerializer, ShopLogisticUnitFullSerializer)
from logistic.permissions import IsAddressOwner, IsShopOwner
from nakhll_market.models import Product, Shop

class AddressViewSet(viewsets.ModelViewSet):
    serializer_class = AddressSerializer
    permission_classes = [IsAddressOwner, permissions.IsAuthenticated ]
    lookup_field = 'id'

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    # def check_post_range(factor):
    #     src_address = factor.shop.address
    #     dst_address = factor.address


    # def calcaulate_post_price(factor):
    #     src_state = factor.shop.State
    #     src_big_city = factor.shop.BigCity
    #     src_city = factor.shop.City

    #     dst_address = factor.address
    #     dst_state = dst_address.state
    #     dst_big_city = dst_address.big_city
    #     dst_city = dst_address.city

    #     if src_state == dst_state and src_big_city == dst_big_city and src_city == dst_city:
    #         return 80000
    #     elif src_big_city == dst_big_city and src_city == dst_city:
    #         return 80000
    #     elif src_state == dst_state:
    #         return 150000
    #     else:
    #         return 200000



# class ShopLogisticUnitViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.UpdateModelMixin):
#     serializer_class = ShopLogisticUnitSerializer
#     permission_classes = [permissions.IsAuthenticated, IsShopOwner]
#     lookup_field = 'id'

#     def get_queryset(self):
#         queryset = ShopLogisticUnit.objects.filter(shop__FK_ShopManager=self.request.user,
#                                                    logistic_unit__is_publish=True)
#         if hasattr(self, 'shop_slug') and self.shop_slug:
#             queryset = queryset.filter(shop__Slug=self.shop_slug)
#         return queryset

#     def list(self, request, *args, **kwargs):
#         self.sync_shop_logistic_unit()
#         return super().list(request, *args, **kwargs)

#     def sync_shop_logistic_unit(self):
#         self.shop_slug = self.request.GET.get('shop')
#         self.shop = Shop.objects.filter(Slug=self.shop_slug).first()
#         if not self.shop:
#             return
#         LogisticUnit.sync_shop(self.shop)
        
        
class ShopLogisticUnitViewSet(viewsets.ModelViewSet):
    serializer_class = ShopLogisticUnitFullSerializer
    permission_classes = [permissions.IsAuthenticated, IsShopOwner]
    lookup_field = 'id'

    def get_shop(self):
        shop_slug = self.request.GET.get('shop')
        try:
            return Shop.objects.get(Slug=shop_slug)
        except Shop.DoesNotExist:
            return None

    def get_queryset(self):
        queryset = ShopLogisticUnit.objects.filter(shop__FK_ShopManager=self.request.user)
        shop = self.get_shop()
        if shop:
            queryset = queryset.filter(shop=shop)
        return queryset.select_related('constraint', 'calculation_metric')

    def perform_create(self, serializer):
        slu = serializer.save()
        ShopLogisticUnitConstraint.objects.create(shop_logistic_unit=slu)
        ShopLogisticUnitCalculationMetric.objects.create(shop_logistic_unit=slu)
    

class ShopLogisticUnitConstraintViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.UpdateModelMixin):
    permission_classes = [permissions.IsAuthenticated, IsShopOwner]
    lookup_field = 'id'

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ShopLogisticUnitConstraintReadSerializer
        return ShopLogisticUnitConstraintWriteSerializer

    def get_queryset(self):
        shop_logistic_unit_id = self.request.GET.get('id')
        queryset = ShopLogisticUnitConstraint.objects.filter(shop_logistic_unit__shop__FK_ShopManager=self.request.user)
        if shop_logistic_unit_id:
            return queryset.filter(shop_logistic_unit__id=shop_logistic_unit_id)
        return queryset             
        


class ShopLogisticUnitCalculationMetricViewSet(viewsets.GenericViewSet,
                                             mixins.UpdateModelMixin,
                                             mixins.RetrieveModelMixin):
    serializer_class = ShopLogisticUnitCalculationMetricSerializer
    permission_classses = [permissions.IsAuthenticated, IsShopOwner]
    lookup_field = 'id'

    def get_queryset(self):
        return ShopLogisticUnitCalculationMetric.objects.filter(
            shop_logistic_unit__shop__FK_ShopManager=self.request.user
        )
  