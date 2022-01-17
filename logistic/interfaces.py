from django.db.models.aggregates import Sum
from django.db.models.functions import Cast
from django.db.models.fields import FloatField
from django.db.models.query import QuerySet
from django.db.models.query_utils import Q
from django.utils.translation import ugettext as _
from rest_framework.validators import ValidationError
from nakhll_market.models import City, NewCategory, Product, Shop


class PostPriceSettingInterface:
    ''' Create an interface for other apps to communicate with PostPriceSetting

        This class should be inharited by PostPriceSetting model.
        It provide some functionallities for other apps to use.
        After inharitance, self variable reference to a setting object
        which contains prices to calculate post_price.
    '''
    def get_out_of_range_products(self, invoice):
        ''' Check if all products in invoice can sent to user address'''
        if not all([hasattr(invoice, 'items') and hasattr(invoice, 'address')]):
            msg = 'factor should have attribute items and address'
            raise ValidationError(msg)

        user_address = invoice.address
        if not user_address:
            return []
        out_of_range_products = []
        for invoice_item in invoice.items.all():
            if not self._is_vaild_product_post_range(invoice_item, user_address):
                out_of_range_products.append(invoice_item.product.title) 
        return out_of_range_products

        
    def _is_vaild_product_post_range(self, invoice_item, user_address):
        ''' Check if user_address is in range of shop post range '''
        # dst_state = user_address.state
        # dst_big_city = user_address.big_city
        dst_city = user_address.city

        # if invoice_item.product.PostRangeType == '1': # This is a post inside coutry and is true
        #     return True
        # elif invoice_item.product.PostRangeType == '2': # This is a post in a state
        #     if dst_state == invoice_item.product.FK_Shop.State:
        #         return True
        #     return False
        # elif invoice_item.product.PostRangeType == '3' or invoice_item.product.PostRangeType == '4': # This is a post in a big city or city
        #     if invoice_item.product.FK_Shop.State == dst_state and invoice_item.product.FK_Shop.BigCity == dst_big_city and invoice_item.product.FK_Shop.City == dst_city:
        #         return True
        #     else:
        #         return False

        if invoice_item.product.post_range_cities.all() and dst_city not in invoice_item.product.post_range_cities.all():
            return False
        return True




    def get_post_price(self, invoice):
        ''' Calculate each shop post_price based on user address '''
        if not all([hasattr(invoice, 'items') and hasattr(invoice, 'address')]):
            msg = 'factor should have attribute items and address'
            raise ValidationError(msg)
        if self.get_out_of_range_products(invoice):
            msg = 'There is errors in post_range. Run .out_of_range_products(invoice) to see them'
            raise ValidationError(msg)
        post_range_price = self._get_factor_post_range_price(invoice) or 0
        post_wieght_price = self._get_factor_post_wieght_price(invoice) or 0
        return post_range_price + post_wieght_price

        
    def _get_factor_post_range_price(self, invoice):
        ''' Get post range price from factor '''
        user_address = invoice.address
        if not user_address:
            return None
        total_post_price = 0
        for shop in invoice.shops.all():
            total_post_price += self._get_shop_post_price(shop, user_address)
        return total_post_price

    def _get_shop_post_price(self, shop, user_address):
        ''' Get post price from a specific shop '''
        dst_state = user_address.state
        dst_big_city = user_address.big_city
        return self.inside_city_price if shop.BigCity == dst_big_city and shop.State == dst_state\
            else self.outside_city_price

    def _get_factor_post_wieght_price(self, invoice):
        ''' Get post wieght price from factor
            For each shop, weight of products multiply by its quantity should be checked
        '''
        total_post_price = 0
        for shop in invoice.shops.all():
            total_post_price += self.__get_shop_post_weight_price(invoice, shop)
        return total_post_price
        
    def __get_shop_post_weight_price(self, invoice, shop):
        extra_weight = 0
        total_item_weights = 0
        for item in invoice.items.filter(product__FK_Shop=shop):
            total_item_weights += int(item.product.weight or 0) * item.count
        weight_kilogram = total_item_weights / 1000
        if weight_kilogram > 1: # There is a fee for more than 1kg
            extra_weight = weight_kilogram - 1 # for example 2.5kg is 2.5kg - 1kg = 1.5kg
            extra_weight = int(extra_weight) + 1 # 1.5kg is 1kg when converted to int, so add 1kg 
        return self.extra_weight_fee * extra_weight
        

class LogisticUnitInterface:
    def __init__(self) -> None:
        self.total_post_price = 0

    def create_logistic_unit_list(self, invoice):
        logistic_units = []
        errors = []
        total_price = 0

        for shop in invoice.shops:
            shop_logistic_unit_dict = self._generate_shop_logistic_unit_dict(shop, invoice)
            price = shop_logistic_unit_dict['price']
            errors.extend(shop_logistic_unit_dict['errors'])
            total_price += price
            logistic_units.append(shop_logistic_unit_dict)

        if errors:
            invoice.items.filter(product__in=errors).delete()
            raise ValidationError(_('این محصولات هیچ روش ارسالی ندارند و از سبد خرید شما حذف خواهند شد<br>{}').format(
                '<br>'.join([product.Title for product in errors])
                ))

        self.total_post_price = total_price
        return {
            "logistic_units": logistic_units,
            "total_price": total_price,
            "errors": errors
        }

            

   
    def _generate_shop_logistic_unit_dict(self, shop, invoice):
        errors = []
        logistic_units = []
        products_available_units = []
        price = 0
        shop_logistic_units_queryset = self.get_acceptable_logistic_units(invoice, shop)
        all_products = invoice.products.filter(FK_Shop=shop)

        pad_products = self._get_only_pad_products(shop_logistic_units_queryset, all_products)
        if pad_products:
            all_products = all_products.difference(pad_products)

        free_products = self._get_free_products(shop_logistic_units_queryset, all_products)
        if free_products:
            all_products = all_products.difference(free_products)

        pad_lu_name = self._get_pad_lu_name(pad_products) # TODO
        free_lu_name = self._get_free_lu_name(free_products) # TODO

        if all_products:
            all_products_set = set()
            for product in all_products:
                product_available_lus = self.get_product_available_lus(shop_logistic_units_queryset, product, exclude_pads=True)
                if not product_available_lus:
                    errors.append(product)
                    invoice.items.filter(product=product).delete()
                else:
                    all_products_set.add(product)
                    products_available_units.append(set(product_available_lus))

            if not products_available_units or not set.intersection(*products_available_units):
                raise ValidationError(_('هیچ واحد ارسالی برای این مجموعه یافت نشد'))
            joint_units = set.intersection(*products_available_units)


            total_weight = invoice.items.filter(product__FK_Shop=shop).aggregate(
                total_weight=Sum(Cast('product__Weight_With_Packing', output_field=FloatField()))
            )['total_weight']
            optimal_unit, price = self.get_optimal_unit_and_price(joint_units, total_weight)
            products = [
                        {'slug': product.slug, 'title': product.Title, 'image': product.image_thumbnail_url}
                        for product in all_products_set
                        ]
            logistic_units.append({
                'unit_name': optimal_unit.name,
                'unit_type': '',
                'products': products,
                'price': price
            })

        if pad_products:
            logistic_units.append({
                'unit_name': pad_lu_name,
                'unit_type': 'pad',
                'products': [
                    {'slug': product.slug, 'title': product.Title, 'image': product.image_thumbnail_url}
                    for product in pad_products
                ],
                'price': 0
            })

        if free_products:
            logistic_units.append({
                'unit_name': free_lu_name,
                'unit_type': 'free',
                'products': [
                    {'slug': product.slug, 'title': product.Title, 'image': product.image_thumbnail_url}
                    for product in free_products
                ],
                'price': 0
            })

        return {
            'shop_name': shop.Title,
            'shop_slug': shop.Slug,
            'logistic_units': logistic_units,
            'price': price,
            'errors': errors
        }

    def _get_only_pad_products(self, queryset: QuerySet, all_products: QuerySet):
        only_pad_ids = []
        for product in all_products:
            all_lus = self.get_product_available_lus(queryset, product)
            pad_lus = self.get_pad_lus(queryset, product)
            if set(all_lus) == set(pad_lus):
                only_pad_ids.append(product.ID)
        only_pad_products = Product.objects.filter(ID__in=only_pad_ids)
        return only_pad_products

    def get_pad_lus(self, shop_all_lus: QuerySet, product: Product):
        filter_queryset = Q(calculation_metric__pay_time=models.ShopLogisticUnitCalculationMetric.PayTimes.AT_DELIVERY)
        filter_queryset &= Q(calculation_metric__payer=models.ShopLogisticUnitCalculationMetric.PayerTypes.CUSTOMER)
        return shop_all_lus.filter(filter_queryset)
        
    def _get_free_products(self, queryset: QuerySet, all_products: set):
        filter_queryset = Q(calculation_metric__pay_time=models.ShopLogisticUnitCalculationMetric.PayTimes.WHEN_BUYING)
        filter_queryset &= Q(calculation_metric__payer=models.ShopLogisticUnitCalculationMetric.PayerTypes.SHOP)
        free_products_qs = queryset.filter(filter_queryset)
        free_products = Product.objects.filter(ID__in=free_products_qs.values_list('constraint__products__ID', flat=True))
        return free_products

        
        
               
    def _get_pad_lu_name(self, pad_products):
        return 'پسکرایه'

    def _get_free_lu_name(self, free_products):
        return 'رایگان'


    def calculate_logistic_unit_price(self, shop_dict, invoice):
        total_price = 0
        for logistic_unit_id, products in shop_dict.items():
            logistic_unit = models.ShopLogisticUnit.objects.get(id=logistic_unit_id)
            items = invoice.items.filter(product__Slug__in=[product['slug'] for product in products['products']])
            price = logistic_unit.calculation_metric.price_per_kilogram
            price += logistic_unit.calculation_metric.price_per_extra_kilogram * self.get_extra_weight(items)
            total_price += price
        return total_price


    def get_acceptable_logistic_units(self, invoice, shop):
        if not models.ShopLogisticUnit.objects.filter(shop=shop, is_active=True).exists():
            return None
        filter_queryset = Q()
        sum_shop_cart_price = invoice.products.filter(FK_Shop=shop).aggregate(
            total_price=Sum('Price')
        )['total_price']
        filter_queryset &= Q(is_active=True)
        filter_queryset &= Q(shop=shop)
        filter_queryset &= Q(
            Q(constraint__cities=invoice.address.city) |
            Q(constraint__cities=None)
        )
        filter_queryset &= Q(constraint__min_cart_price__lte=sum_shop_cart_price)
        return models.ShopLogisticUnit.objects.filter(filter_queryset)
            
    def get_product_available_lus(self, queryset: QuerySet, product: Product, *, exclude_pads=False):
        filter_queryset = Q()
        filter_queryset &= Q(
            Q(constraint__products=product) |
            Q(constraint__products=None)
        )
        # TODO: max weight should be calculated base on all products, not just one
        weight = int(product.Weight_With_Packing) / 1000
        filter_queryset &= Q(
            Q(constraint__max_weight__gte=weight) |
            Q(constraint__max_weight=0)
        )
        queryset = queryset.filter(filter_queryset)
        if exclude_pads:
            pad_filter_queryset = Q(calculation_metric__pay_time=models.ShopLogisticUnitCalculationMetric.PayTimes.AT_DELIVERY)
            pad_filter_queryset &= Q(calculation_metric__payer=models.ShopLogisticUnitCalculationMetric.PayerTypes.CUSTOMER)
            queryset = queryset.exclude(pad_filter_queryset)

        return queryset


    def is_only_pad(self, product: Product, invoice):
        all_logistics = self.get_available_logistic_units(invoice, product)
        if len(all_logistics) == 1 and all_logistics[0].logistic_type == 'pad':
            return True
        return False
        
    def get_optimal_unit_and_price(self, units, total_weight):
        minimum_price = None
        optimal_unit = None
        for unit in units:
            price = self.calculate_logistic_price(unit, total_weight)
            if minimum_price is None or price < minimum_price:
                minimum_price = price
                optimal_unit = unit
        return optimal_unit, minimum_price
            
        
    def calculate_logistic_price(self, unit, total_weight):
        extra_weight = int((total_weight + 1) / 1000)
        price = unit.calculation_metric.price_per_kilogram
        price += unit.calculation_metric.price_per_extra_kilogram * extra_weight
        return price
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        


def generate_shop_logistic_units():
    SLU = models.ShopLogisticUnit
    for shop in Shop.objects.all():
        SLU.objects.generate_logistic_units(shop)
        



from logistic import models
