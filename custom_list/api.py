from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from rest_framework import status, viewsets, mixins, authentication, permissions
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from nakhll_market.models import Product
from custom_list.models import Favorite
from custom_list.serializers import UserFavoriteProductSerializer

class UserFavoriteProductsViewset(viewsets.GenericViewSet):
    '''
    Products that a registered user added to his/her favorites list
    
    Each user has a single favorites list called `Favorite` which contains
    many products.
    '''
    serializer_class = UserFavoriteProductSerializer
    permission_classes = [permissions.IsAuthenticated, ]
    queryset = Product.objects.all()

    def get_object(self):
        '''Get the user's favorite list or create if it does not exists '''
        user = self.request.user
        user_fav_list, _ = Favorite.objects.get_or_create(user=user)
        return user_fav_list

    def get_product(self, pk):
        ''' Get the product object from primary key'''
        try:
            return get_object_or_404(Product, ID=pk)
        except Exception as ex:
            raise ValidationError(ex)


    @action(detail=False, methods=['GET'], url_path='all')
    def user_fav_list(self, request):
        '''Return all products in the current user's favorite list'''
        user_fav_list = self.get_object()
        serializer = UserFavoriteProductSerializer(user_fav_list)
        return Response(serializer.data)

    @action(detail=False, methods=['POST'], url_path='add') 
    def add_product_to_fav_list(self, request):
        '''Add a product to the current user's favorite list'''
        user_fav_list = self.get_object()
        serializer = UserFavoriteProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(fav_list=user_fav_list)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['DELETE'])
    def remove(self, request, pk):
        '''Remove a product from the current user's favorite list'''
        user_fav_list = self.get_object()
        product = self.get_product(pk)
        user_fav_list.products.remove(product)
        return Response(status=status.HTTP_204_NO_CONTENT)



    


