from rest_framework import status, permissions, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from logistic.managers import AddressManager
from django.utils.translation import ugettext as _
from logistic.models import Address, ShopLogisticUnit, ShopLogisticUnitConstraint, LogisticUnit
from logistic.serializers import AddressSerializer, ShopLogisticUnitSerializer, ShopLogisticUnitConstraintSerializer
from logistic.permissions import IsAddressOwner
from nakhll_market.models import Shop

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



class ShopLogisticUnitViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.UpdateModelMixin):
    serializer_class = ShopLogisticUnitSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        queryset = ShopLogisticUnit.objects.filter(shop__FK_ShopManager=self.request.user,
                                                   logistic_unit__is_publish=True)
        if self.shop_slug:
            queryset = queryset.filter(shop__Slug=self.shop_slug)
        return queryset

    def list(self, request, *args, **kwargs):
        self.sync_shop_logistic_unit()
        return super().list(request, *args, **kwargs)

    def sync_shop_logistic_unit(self):
        self.shop_slug = self.request.GET.get('shop')
        self.shop = Shop.objects.filter(Slug=self.shop_slug).first()
        if not self.shop:
            return
        all_logistic_units_ids = LogisticUnit.objects.filter(is_publish=True).values_list('id', flat=True)
        shop_logistic_units_ids = self.get_queryset().values_list('logistic_unit__id', flat=True)
        for id in all_logistic_units_ids:
            if id not in shop_logistic_units_ids:
                self.create_shop_logistic_unit(id)

    def create_shop_logistic_unit(self, logistic_unit_id):
        shop_logistic_unit = ShopLogisticUnit(shop=self.shop, logistic_unit_id=logistic_unit_id)
        shop_logistic_unit.save()
        return Response({'message': _('Shop logistic unit is deactivated')}, status=status.HTTP_200_OK)
    
    
class ShopLogisticUnitConstraintViewSet(viewsets.ModelViewSet):
    serializer_class = ShopLogisticUnitConstraintSerializer
    permission_classes = [permissions.IsAuthenticated]
        
    def get_queryset(self):
        return ShopLogisticUnitConstraint.objects.filter(shop__FK_User=self.request.user)
        
        
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
