from django.db.models import F
from django.db.models.aggregates import Sum
from django.db.models.fields import FloatField
from django.db.models.functions import Cast
from django.db.models.query_utils import Q
from rest_framework.validators import ValidationError
from nakhll_market.models import Product, Shop
from . import models
from .exceptions import NoLogisticUnitAvailableException


class LogisticUnitInterface:
    """Interface for logistic unit calculation based on user cart

    Given a cart, logistic unit will calculate logistic details including
    price and optimal unit for each shop.

    Attributes:
        total_price: Zero by default. This will be the final price of the
            logistic unit for an invoice after calculation.
        cart (Cart): Cart object, which is going to convert to invoice
        logistic_units (list): Final details of the logistic unit after
            calculation. It will contains logistic unit names with all
            products that are going to be shipped in that logistic unit.
            Also, it will contains each logistic unit price.
            It also can contains errors if any.
        errors (list): List of all errors (if any) that occurred during
            calculation.
    """

    def __init__(self, cart) -> None:
        self.total_price = 0
        self.cart = cart
        self.logistic_units = []
        self.errors = []

    def generate_logistic_unit_list(self):
        """Loop through all shops and generate logistic unit list

        Each shop will have its own logistic unit, including errors, total
        price and logistic unit details (which itself contains products group
        and the optimal unit for each group).

        Returns:
            This function will not return anything. It will update the
            :attr:`logistic_units` attribute in self.
        """
        for shop in self.cart.shops:
            shop_obj = ShopLogisticUnitInterface(self.cart, shop)
            shop_obj.generate_shop_logistic_units()

            self.errors.extend(shop_obj.errors)
            self.total_price += shop_obj.total_price
            self.logistic_units.append(shop_obj.logistic_units)

        if self.errors:
            self.cart.items.filter(product__in=self.errors).delete()

        # TODO: after fixing purchase process
        # if no_item:
        #     raise ValidationError({
        #         'errors': [_('No Item to purchase')],
        #         'redirect': 'https://nakhll.com/cart/'
        #         })

    def as_dict(self):
        """Return logistic unit list as dict"""
        return {
            "errors": self.errors,
            "total_price": self.total_price,
            "logistic_units": self.logistic_units,
        }


class ShopLogisticUnitInterface:
    """Calculate optimal unit and price for a given shop in cart

    This class use :func:`generate_shop_logistic_units` as it's main method
    to generate logistic units for given shop.

    The __init__ method of this class, will calculate some basic things, as
    described here:
        - available_logistic_units
        - all_products
        - pad_products
        - free_products
        - total_weight

    Args:
        shop (Shop): Shop object for which logistic unit will be calculated
        cart (Cart): Cart object for which logistic unit will be calculated
        total_price: Total price of the logistic unit for given shop in this
            cart. This value is zero, but will be filled after calculation.
        logistic_units (list): List of logistic units for given shop in this
            cart. This value is private to this class. Final result can be
            accessed by :attr:`logistic_unit` property.
        available_logistic_units: list of all logistic units for given shop
            that is available for this cart. Two main parameters here that may
            affect this calculation are:
                - Cart address
                - Cart total_weight
        all_products: All products in this cart which is belogs to given shop
        pad_products: Products that can be sent to user's address, only with
            "Pay At Delivery" method. This products will pop out from all
            products in :attr:`all_products`.
        free_products: Products that can be send to user using a free service
            provided by shop owner. This products will pop out from all
            products in :attr:`all_products`.
        total_weight: Total weight of all products with their count in this
            cart for the given shop.

    Attributes:
        PAD_UNIT_TYPE: const value for pad (Pay At Delivery) serivces.
        FREE_UNIT_TYPE: const value for free serivces.
    """

    PAD_UNIT_TYPE = 'pad'
    FREE_UNIT_TYPE = 'free'

    def __init__(self, cart, shop):
        self.total_price = 0
        self.cart = cart
        self.shop = shop
        self.__logistic_units = []
        self.errors = []
        self.available_logistic_units = self.get_available_logistic_units(shop)
        self.all_products = self.cart.products.filter(FK_Shop=self.shop)
        self.pad_products = self.pop_only_pad_products()
        self.free_products = self.pop_free_products()
        self.total_weight = self.get_total_weight()

    def generate_shop_logistic_units(self):
        """Main method that calculates and generates all logistic unit details
            with their price for given shop

        This method devides logistic unit into 3 section:
            - products that only can be sent using pad system of shop.
              price for this service is always zero, because user should pay
              for that in their delivery location, not in website.
            - products that can be sent using a free system of shop.
              price for this service is zero too.
            - other products optimal unit will calculate using this system:
                For each remaining product, all available logistic units will
                be stored in a set.
                After that, intersection of those logistic units will sent to
                a method to get optimal unit among all units, with it's price.
                *Note*: If no intersection among logistic units was available,
                :attr:`logistic.exceptions.NoLogisticUnitAvailableException`
                will be raised.
        """
        products_available_units = []

        if self.pad_products:
            pad_lu_name = self._get_pad_lu_name()
            self.__logistic_units.append({
                'unit_name': pad_lu_name,
                'unit_type': self.PAD_UNIT_TYPE,
                'products': [
                    {
                        'slug': product.slug,
                        'title': product.Title,
                        'image': product.image_thumbnail_url
                    }
                    for product in self.pad_products
                ],
                'price': 0
            })

        if self.free_products:
            free_lu_name = self._get_free_lu_name()
            self.__logistic_units.append({
                'unit_name': free_lu_name,
                'unit_type': self.FREE_UNIT_TYPE,
                'products': [
                    {
                        'slug': product.slug,
                        'title': product.Title,
                        'image': product.image_thumbnail_url
                    }
                    for product in self.free_products
                ],
                'price': 0
            })

        if self.all_products:
            all_products_set = set()
            for product in self.all_products:
                product_available_lus = self.get_product_available_logistic_units(
                    product, exclude_pads=True)
                if not product_available_lus:
                    self.errors.append(product)
                    self.cart.items.filter(product=product).delete()
                else:
                    all_products_set.add(product)
                    products_available_units.append(set(product_available_lus))

            if not products_available_units or not set.intersection(
                    *products_available_units):
                raise NoLogisticUnitAvailableException()
            joint_units = set.intersection(*products_available_units)

            optimal_unit, self.total_price = self.get_optimal_unit_and_price(
                joint_units)
            products = [
                {'slug': product.slug, 'title': product.Title,
                 'image': product.image_thumbnail_url}
                for product in all_products_set]

            self.__logistic_units.append({
                'unit_name': optimal_unit.name,
                'unit_type': '',
                'products': products,
                'price': self.total_price
            })

    @property
    def logistic_units(self):
        """Create and return a detailed dict from
            :attr:`self.__logistic_units`
        """
        return {
            'price': self.total_price,
            'errors': self.errors,
            'shop_name': self.shop.Title,
            'shop_slug': self.shop.Slug,
            'logistic_units': self.__logistic_units
        }

    def get_total_weight(self):
        """Get total weight of all products in this cart for given shop."""
        return self.cart.items.filter(product__FK_Shop=self.shop).aggregate(
            total_weight=Sum(Cast(Cast(
                'product__Weight_With_Packing',
                output_field=FloatField()
            ) * F('count'), output_field=FloatField()))
        )['total_weight']

    def pop_only_pad_products(self):
        """Pop products that can be sent to user's address only with pad

        This function gets logistuc_units for all products in this cart for
        given shop and compare it with the shop's pad logistic unit. If product
        can be sent to user's address only with pad system, it removes that
        product from all products list in :attr:`all_products` and returns
        pad_only products.
        """
        only_pad_ids = []
        for product in self.all_products:
            all_lus = self.get_product_available_logistic_units(product)
            pad_lus = self.get_pad_lus()
            if set(all_lus) == set(pad_lus) and len(all_lus) != 0:
                only_pad_ids.append(product.ID)
        only_pad_products = Product.objects.filter(ID__in=only_pad_ids)
        self.all_products = self.all_products.difference(only_pad_products)
        return only_pad_products

    def pop_free_products(self):
        """Pop products that contains free logistic unit

        This function get all products that contains free logistic unit. They
        may contains other logistic units too, but having free logistic unit
        is enough to be considered as free. This product will be removed from
        all products list in :attr:`all_products` and returned.
        """
        free_products_qs = self.get_free_lus()
        free_products = Product.objects.filter(
            ID__in=free_products_qs.values_list(
                'constraint__products__ID', flat=True))
        self.all_products = self.all_products.difference(free_products)
        return free_products

    def _get_pad_lu_name(self):
        """Pop products that contains free logistic unit

        This function get all products that contains free logistic unit. They
        may contains other logistic units too, but having free logistic unit
        is enough to be considered as free. This product will be removed from
        all products list in :attr:`all_products` and returned.
        """
        lu = self.get_pad_lus().first()
        if lu:
            return lu.name
        return 'پسکرایه'

    def _get_free_lu_name(self):
        """Get any free logistic unit name for given shop

        If shop has any free logistic unit, this method will return it's name.
        if not, it will return default free logistic unit name.
        """
        lu = self.get_free_lus().first()
        if lu:
            return lu.name
        return 'ارسال رایگان'

    def shop_active_logistic_units(self, shop):
        return models.ShopLogisticUnit.filter(
            shop=shop, is_active=True)

    def get_available_logistic_units(self, shop):
        """
        available_logistic_units: list of all logistic units for given shop
            that is available for this cart. Two main parameters here that may
            affect this calculation are:
                - Cart address
                - Cart total_weight
        """
        queryset = self.shop_active_logistic_units(shop)
        sum_shop_cart_price = self.cart.products.filter(
            FK_Shop=shop).aggregate(total_price=Sum('Price'))['total_price']
        filter_queryset = Q(
            Q(constraint__cities=self.cart.address.city) |
            Q(constraint__cities=None)
        )
        filter_queryset &= Q(
            constraint__min_cart_price__lte=sum_shop_cart_price)
        return queryset.filter(filter_queryset)

    def get_product_available_logistic_units(
            self, product: Product, *, exclude_pads=False):
        """Get all available logistic units for given product and shop

        Args:
            product (Product): The product to get available logistic units for
            exclude_pads (bool, optional): If True, products that can be sent
                to user's address with pad will be removed from the result.
                Defaults to False.

        Returns:
            QuerySet of all available logistic units for given product
        """
        filter_queryset = Q()
        filter_queryset &= Q(
            Q(constraint__products=product) |
            Q(constraint__products=None)
        )
        # TODO: max weight should be calculated base on all products, not just
        # one
        weight = int(product.Weight_With_Packing) / 1000
        filter_queryset &= Q(
            Q(constraint__max_weight__gte=weight) |
            Q(constraint__max_weight=0)
        )
        queryset = self.available_logistic_units.filter(filter_queryset)
        if exclude_pads:
            pad_filter_queryset = Q(
                calculation_metric__pay_time=models.ShopLogisticUnitCalculationMetric.PayTimes.AT_DELIVERY)
            pad_filter_queryset &= Q(
                calculation_metric__payer=models.ShopLogisticUnitCalculationMetric.PayerTypes.CUSTOMER)
            queryset = queryset.exclude(pad_filter_queryset)

        return queryset

    def get_optimal_unit_and_price(self, units):
        """Get optimal logistic unit and price for given units

        This method will loop through all given logistic units. It will
        calculate price for each unit and return the unit with the lowest
        price.
        """
        minimum_price = None
        optimal_unit = None
        for unit in units:
            price = self.calculate_logistic_price(unit)
            if minimum_price is None or price < minimum_price:
                minimum_price = price
                optimal_unit = unit
        return optimal_unit, minimum_price

    def calculate_logistic_price(self, unit):
        """Calculate logistic price for given unit"""
        extra_weight = int((self.total_weight + 1) / 1000)
        price = unit.calculation_metric.price_per_kilogram
        price += unit.calculation_metric.price_per_extra_kilogram * extra_weight
        return price

    def get_pad_lus(self):
        """Get all pad logistic units for given shop"""
        filter_queryset = Q(
            calculation_metric__pay_time=models.ShopLogisticUnitCalculationMetric.PayTimes.AT_DELIVERY)
        filter_queryset &= Q(
            calculation_metric__payer=models.ShopLogisticUnitCalculationMetric.PayerTypes.CUSTOMER)
        return self.available_logistic_units.filter(filter_queryset)

    def get_free_lus(self):
        """Get all free logistic units for given shop"""
        filter_queryset = Q(
            calculation_metric__pay_time=models.ShopLogisticUnitCalculationMetric.PayTimes.WHEN_BUYING)
        filter_queryset &= Q(
            calculation_metric__payer=models.ShopLogisticUnitCalculationMetric.PayerTypes.SHOP)
        return self.available_logistic_units.filter(filter_queryset)


def generate_shop_logistic_units():
    SLU = models.ShopLogisticUnit
    for shop in Shop.objects.all():
        SLU.objects.generate_logistic_units(shop)
