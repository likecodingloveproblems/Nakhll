from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from nakhll_market.models import BigCity, City, Product, Shop, Alert, State, DashboardBanner
from nakhll_market.permissions import IsInvoiceProvider
from nakhll_market.serializers import ProductOwnerListSerializer
from invoice.models import Invoice, InvoiceItem
from invoice.serializers import BarcodeSerializer, InvoiceRetrieveSerializer, InvoiceProviderRetrieveSerializer
from restapi.permissions import IsShopOwner
from restapi.serializers import BigCitySerializer, CitySerializer, ProfileSerializer, StateSerializer
from sms.services import Kavenegar
from restapi.validators import get_params_are_numeric


class UncompeletedFactors(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = InvoiceProviderRetrieveSerializer

    def get_queryset(self):
        user = self.request.user
        return Invoice.objects.uncompleted_user_invoices(user)


class CompeletedFactors(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = InvoiceProviderRetrieveSerializer

    def get_queryset(self):
        user = self.request.user
        return Invoice.objects.completed_user_invoices(user)


class ShopCompeletedFactors(ListAPIView):
    permission_classes = [IsAuthenticated, IsShopOwner]
    serializer_class = InvoiceProviderRetrieveSerializer

    def get_queryset(self):
        user = self.request.user
        shop_slug = self.kwargs.get('shop_slug')
        shop = get_object_or_404(Shop, Slug=shop_slug)
        self.check_object_permissions(self.request, shop)
        return Invoice.objects.completed_user_shop_invoices(user, shop_slug)


class ShopUncompeletedFactors(ListAPIView):
    permission_classes = [IsAuthenticated, IsShopOwner]
    serializer_class = InvoiceProviderRetrieveSerializer

    def get_queryset(self):
        user = self.request.user
        shop_slug = self.kwargs.get('shop_slug')
        shop = get_object_or_404(Shop, Slug=shop_slug)
        self.check_object_permissions(self.request, shop)
        return Invoice.objects.uncompleted_user_shop_invoices(
            user, shop_slug).distinct()


class ShopProductList(ListAPIView):
    serializer_class = ProductOwnerListSerializer
    permission_classes = [permissions.IsAuthenticated, IsShopOwner]
    lookup_field = 'shop_slug'
    # filter_backends = [OrderingFilter]
    # ordering_fields = ['inventory', 'price', 'total_sell']

    def get_queryset(self):
        slug = self.kwargs.get('shop_slug')
        shop = get_object_or_404(Shop, Slug=slug)
        user = self.request.user
        # user = User.objects.get(id=72)
        self.check_object_permissions(self.request, shop)

        # Get query Parameters to do filtring and ordering
        product_status = self.request.query_params.get('product_status')
        price_from = self.request.query_params.get('price_from')
        price_to = self.request.query_params.get('price_to')
        inventory_from = self.request.query_params.get('inventory_from')
        inventory_to = self.request.query_params.get('inventory_to')
        order_by = self.request.query_params.get('order_by', None)

        # Filtering
        shop_products = Product.objects.get_user_shop_products(
            user, shop, order_by)
        shop_products = shop_products.filter(
            Status=product_status) if product_status else shop_products
        shop_products = shop_products.filter(
            Price__gt=price_from) if price_from else shop_products
        shop_products = shop_products.filter(
            Price__lt=price_to) if price_to else shop_products
        shop_products = shop_products.filter(
            Inventory__gt=inventory_from) if inventory_from else shop_products
        shop_products = shop_products.filter(
            Inventory__lt=inventory_to) if inventory_to else shop_products

        return shop_products


class UserInfo(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        user = request.user
        serializer = ProfileSerializer(user.User_Profile)
        return Response(serializer.data)


class UserDashboardInfo(APIView):
    permission_classes = [IsAuthenticated, IsShopOwner]

    def get(self, request, shop_slug, format=None):
        user = request.user
        shop_slug = self.kwargs.get('shop_slug')
        shop = get_object_or_404(Shop, Slug=shop_slug)
        self.check_object_permissions(request, shop)

        completed_fators = Invoice.objects.completed_user_shop_invoices(
            user, shop_slug).count()
        uncompleted_fators = Invoice.objects.uncompleted_user_shop_invoices(
            user, shop_slug).count()
        uncomfirmed_factors = Invoice.objects.unconfirmed_user_shop_invoices(
            user, shop_slug).count()
        banners = DashboardBanner.objects.get_banners(
            banner_status=DashboardBanner.PublishStatuses.PUBLISH)
        unread_comments_count = 0

        balance = 0  # TODO We don't have any wallet anymore

        current_week_total_sell = InvoiceItem.objects.current_week_user_total_sell(
            user, shop_slug)

        # Total sell in last week
        last_week_total_sell = InvoiceItem.objects.last_week_user_total_sell(
            user,
            shop_slug)

        # Total sell in last month
        last_month_total_sell = InvoiceItem.objects.last_month_user_total_sell(
            user,
            shop_slug)

        # Active Products
        active_products = Product.objects.user_shop_active_products(
            user, shop_slug).count()

        # InActive Products
        inactive_products = Product.objects.user_shop_inactive_products(
            user, shop_slug).count()

        # Nearly Out-Of-Stock Products
        nearly_outofstock_products = Product.objects.nearly_outofstock_products(
            user, shop_slug).count()

        # Out-Of-Stock Products
        outofstock_products = Product.objects.outofstock_products(
            user, shop_slug).count()

        # Panel Images and Sell History in Days for later
        return Response({
            'completed_fators': completed_fators,
            'uncompleted_fators': uncompleted_fators,
            'uncomfirmed_factors': uncomfirmed_factors,
            'unread_comments_count': unread_comments_count,
            'balance': balance,
            'current_week_total_sell': current_week_total_sell,
            'last_week_total_sell': last_week_total_sell,
            'last_month_total_sell': last_month_total_sell,
            'active_products': active_products,
            'inactive_products': inactive_products,
            'nearly_outofstock_products': nearly_outofstock_products,
            'outofstock_products': outofstock_products,
            'banners': banners,
        }, status=status.HTTP_200_OK)


class StateList(ListAPIView):
    serializer_class = StateSerializer
    queryset = State.objects.all().order_by('name')


class BigCityList(ListAPIView):
    serializer_class = BigCitySerializer

    @get_params_are_numeric(params=['state_id'])
    def get_queryset(self):
        state_id = self.request.GET.get('state_id')
        state = get_object_or_404(State, id=state_id)
        return BigCity.objects.filter(state=state).order_by('name')


class CityList(ListAPIView):
    serializer_class = CitySerializer

    @get_params_are_numeric(params=['bigcity_id'])
    def get_queryset(self):
        # we have unique big_city.name
        bigcity_id = self.request.GET.get('bigcity_id')
        bigcity = get_object_or_404(BigCity, id=bigcity_id)
        return City.objects.filter(big_city=bigcity).order_by('name')


class FactorDetails(APIView):
    permission_classes = [IsAuthenticated, IsInvoiceProvider]

    def get(self, request, format=None):
        invoice_id = request.GET.get('factor_id', 0)
        invoice = get_object_or_404(Invoice, id=invoice_id)
        self.check_object_permissions(request, invoice)
        serializer = InvoiceRetrieveSerializer(
            invoice, context={'request': request})
        return Response(serializer.data)


class ChangeFactorToConfirmed(APIView):
    ''' In each confirmation of factorpost, check for other factor posts of the factor
        if all factorposts are confirmed, factor state should be changed to confirmed
        and also an alert should be generated for staff to notified about factor comfirmation
    '''
    permission_classes = [IsAuthenticated, IsInvoiceProvider]

    def get_object(self, factor_id):
        return get_object_or_404(Invoice, id=factor_id)

    def put(self, request, factor_id):
        invoice = self.get_object(factor_id)
        self.check_object_permissions(request, invoice)
        # factor_posts = factor.FK_FactorPost.filter(FK_Product__FK_Shop__FK_ShopManager=request.user)
        invoice_items = invoice.items.filter(
            product__FK_Shop__FK_ShopManager=request.user)
        invoice_item_bulk = []
        for item in invoice_items:
            item.status = InvoiceItem.ItemStatuses.PREPATING_PRODUCT
            invoice_item_bulk.append(item)
        InvoiceItem.objects.bulk_update(invoice_item_bulk, ['status'])

        # Check for any invoice_item that not confirmed yet
        if all(
                item.status == InvoiceItem.ItemStatuses.PREPATING_PRODUCT
                for item in invoice_items):
            invoice.status = Invoice.Statuses.PREPATING_PRODUCT
            invoice.save()
            response_msg = 'Done'
        else:
            response_msg = 'Wait for other shops to confirm'

        # Set Alert
        Alert.objects.get_or_create(
            Part='20', FK_User=request.user, Slug=invoice.id)
        return Response({'details': response_msg}, status=status.HTTP_200_OK)


class ChangeFactorToSent(APIView):
    permission_classes = [IsAuthenticated, IsInvoiceProvider]

    def get_object(self, factor_id):
        invoice = get_object_or_404(Invoice, id=factor_id)
        self.check_object_permissions(self.request, invoice)
        return invoice

    def post(self, request, factor_id):
        # TODO: to replace with new logistic module
        serializer = BarcodeSerializer(data=request.data)
        if serializer.is_valid():
            barcode = serializer.validated_data.get('barcode')
            invoice = self.get_object(factor_id)
            invoice_items = invoice.items.filter(
                product__FK_Shop__FK_ShopManager=request.user)

            # Change factor_posts status and add post barcode to them
            invoice_item_list = []
            for item in invoice_items:
                item.status = InvoiceItem.ItemStatuses.AWAIT_CUSTOMER_APPROVAL
                item.barcode = barcode
                # PostTrackingCode.objects.create(factor_post=factor_post, barcode=barcode, post_type=post_type)
                invoice_item_list.append(item)
            InvoiceItem.objects.bulk_update(
                invoice_item_list, ['status', 'barcode'])

            # Check for any factor post that not sent yet
            if all(
                    item.status == InvoiceItem.ItemStatuses.AWAIT_CUSTOMER_APPROVAL
                    for item in invoice_items):
                invoice.status = Invoice.Statuses.AWAIT_CUSTOMER_APPROVAL
                invoice.save()
                response_msg = 'Done'
            else:
                response_msg = 'Wait for other shops to send'
            Kavenegar.invoice_has_been_sent(invoice)

            # Set Alert
            #! TODO: There is no part with code 34. Code 34 should be created later and it should be for
            #! TODO: PostTrackingCode model. The reason that I cannot use code 21 (which is SendOrder), is
            #! TODO: because it related to PostBarCode and will throw an error. An alertview should be created
            #! TODO: specefically for PostTrackingCode model. For now I just create Alert and save the rest
            #! TODO: for later
            #! TODO: Another problem is what should be saved to Slug field?
            Alert.objects.get_or_create(
                Part='34', FK_User=request.user, Slug=factor_id)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {'details': response_msg, 'data': serializer.data},
            status=status.HTTP_200_OK)
