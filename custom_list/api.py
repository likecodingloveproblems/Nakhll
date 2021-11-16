from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from rest_framework import generics, viewsets, mixins, authentication, permissions
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from nakhll_market.models import Product
from custom_list.models import Favorite
from custom_list.serializers import SimpleFavoriteSerializer, UserFavoriteProductSerializer

class UserFavoriteProductsViewset(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    serializer_class = UserFavoriteProductSerializer
    permission_classes = [permissions.IsAuthenticated, ]
    queryset = Product.objects.all()

    def list(self, request, *args, **kwargs):
        return self.retrieve(request, args, kwargs)

    def get_object(self):
        user = self.request.user
        user_fav_list, _ = Favorite.objects.get_or_create(user=user)
        return user_fav_list

    def get_product(self, pk):
        try:
            return get_object_or_404(Product, ID=pk)
        except Exception as ex:
            raise ValidationError(ex)

    @action(detail=True, methods=['POST']) 
    def add(self, request, pk):
        user_fav_list = self.get_object()
        product = self.get_product(pk)
        user_fav_list.product.add(product)
        return Response({'status': 'success'})

    @action(detail=True, methods=['DELETE'])
    def remove(self, request, pk):
        user_fav_list = self.get_object()
        product = self.get_product(pk)
        user_fav_list.product.remove(product)
        return Response({'status': 'success'})



    


