from django.core.files import File
from django.db.models.aggregates import Sum
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

    def create_logistic_unit_dict(self, invoice):
        list = []
        errors = []
        for shop in invoice.shops:
            shop_dict = {}
            for item in invoice.products.filter(FK_Shop=shop):
                product: Product = item
                logistic_unit = self.get_logistic_unit(invoice, product)
                if not logistic_unit:
                    errors.append(product)
                logistic_units= shop_dict.pop(logistic_unit.id, None)
                if not logistic_units:
                    logistic_units = {
                        'name': logistic_unit.name,
                        'products': [],
                    }
                products = logistic_units.pop('products')
                products.append({'title': product.Title, 'slug': product.Slug, 'image': product.image_thumbnail_url})
                logistic_units['products'] = products
                shop_dict[logistic_unit.id] = logistic_units
            price = self.calculate_logistic_unit_price(shop_dict, invoice)
            self.total_post_price += price
            list.append({
                'shop_name': shop.Title,
                'shop_slug': shop.Slug,
                'logistic_units': shop_dict,
                'price': price
            })
        if errors:
            invoice.items.filter(product__in=errors).delete()
            raise ValidationError(_('این محصولات هیچ روش ارسالی ندارند و از سبد خرید شما حذف خواهند شد<br>{}').format(
                '<br>'.join([product.Title for product in errors])
                ))
        return list


    def calculate_logistic_unit_price(self, shop_dict, invoice):
        total_price = 0
        for logistic_unit_id, products in shop_dict.items():
            logistic_unit = models.ShopLogisticUnit.objects.get(id=logistic_unit_id)
            items = invoice.items.filter(product__Slug__in=[product['slug'] for product in products['products']])
            price = logistic_unit.calculation_metric.price_per_kilogram
            price += logistic_unit.calculation_metric.price_per_extra_kilogram * self.get_extra_weight(items)
            total_price += price
        return total_price

        
    def get_extra_weight(self, items):
        total_weight = 0
        for item in items:
            total_weight += int(item.weight or 0) * item.count
        return int(total_weight / 1000)


    def get_logistic_unit(self, invoice, product: Product):
        if not models.ShopLogisticUnit.objects.filter(shop=product.FK_Shop, is_active=True).exists():
            return None

        filter_queryset = Q(
            Q(constraint__products=product) |
            Q(constraint__products=None)
        )
        sum_shop_cart_weight = invoice.products.filter(FK_Shop=product.FK_Shop).aggregate(
            total_price=Sum('Price')
        )['total_price']
        filter_queryset |= Q(is_active=True)
        filter_queryset |= Q(constraint__cities=invoice.address.city)
        filter_queryset |= Q(constraint__max_weight__gte=product.Weight_With_Packing)
        filter_queryset |= Q(constraint__min_cart_price__lte=sum_shop_cart_weight)

        return models.ShopLogisticUnit.objects.filter(filter_queryset).first()

def generate_shop_logistic_units():
    SLU = models.ShopLogisticUnit
    for shop in Shop.objects.all():
        logo_path = 'defaults/lu_free.png'
        logo_file = File(open(logo_path, 'rb'))
        slu = SLU.objects.create(shop=shop, name='ارسال رایگان', is_active=False, logo=logo_file)
        sluc = models.ShopLogisticUnitConstraint.objects.create(
            shop_logistic_unit=slu
        )
        slum = models.ShopLogisticUnitCalculationMetric.objects.create(
            shop_logistic_unit=slu, price_per_kilogram=0, price_per_extra_kilogram=0
        )

        logo_path = 'defaults/lu_delivery.png'
        logo_file = File(open(logo_path, 'rb'))
        slu = SLU.objects.create(shop=shop, name='پیک', is_active=False, logo=logo_file)
        sluc = models.ShopLogisticUnitConstraint.objects.create(
            shop_logistic_unit=slu,
        )
        try:
            sluc.cities.add(City.objects.get(name=shop.City))
        except:
            pass
        slum = models.ShopLogisticUnitCalculationMetric.objects.create(
            shop_logistic_unit=slu, price_per_kilogram=0, price_per_extra_kilogram=0
        )
  
        logo_path = 'defaults/lu_pad.png'
        logo_file = File(open(logo_path, 'rb'))
        slu = SLU.objects.create(shop=shop, name='پسکرایه', is_active=True, logo=logo_file)
        sluc = models.ShopLogisticUnitConstraint.objects.create(
            shop_logistic_unit=slu
        )
        slum = models.ShopLogisticUnitCalculationMetric.objects.create(
            shop_logistic_unit=slu, price_per_kilogram=0, price_per_extra_kilogram=0
        )

        logo_path = 'defaults/lu_post_pishtaz.png'
        logo_file = File(open(logo_path, 'rb'))
        slu = SLU.objects.create(shop=shop, name='پست پیشتاز', is_active=True, logo=logo_file)
        sluc = models.ShopLogisticUnitConstraint.objects.create(
            shop_logistic_unit=slu, max_weight=40
        )
        slum = models.ShopLogisticUnitCalculationMetric.objects.create(
            shop_logistic_unit=slu, price_per_kilogram=150000, price_per_extra_kilogram=25000
        )
        
        logo_path = 'defaults/lu_post_sefareshi.png'
        logo_file = File(open(logo_path, 'rb'))
        slu = SLU.objects.create(shop=shop, name='پست سفارشی', is_active=True, logo=logo_file)
        sluc = models.ShopLogisticUnitConstraint.objects.create(
            shop_logistic_unit=slu, max_weight=40
        )
        slum = models.ShopLogisticUnitCalculationMetric.objects.create(
            shop_logistic_unit=slu, price_per_kilogram=140000, price_per_extra_kilogram=20000
        )



from logistic import models
