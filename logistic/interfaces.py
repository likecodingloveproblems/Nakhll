from rest_framework.validators import ValidationError


class PostPriceSettingInterface:
    ''' Create an interface for other apps to communicate with PostPriceSetting

        This class should be inharited by PostPriceSetting model.
        It provide some functionallities for other apps to use.
        After inharitance, self variable reference to a setting object
        which contains prices to calculate post_price.
    '''

    def _is_vaild_product_post_range(self, invoice_item, user_address):
        ''' Check if user_address is in range of shop post range '''
        dst_state = user_address.state
        dst_big_city = user_address.big_city
        dst_city = user_address.city

        if invoice_item.product.PostRangeType == '1': # This is a post inside coutry and is true
            return True
        elif invoice_item.product.PostRangeType == '2': # This is a post in a state
            if dst_state == invoice_item.product.FK_Shop.State:
                return True
            return False
        elif invoice_item.product.PostRangeType == '3' or invoice_item.product.PostRangeType == '4': # This is a post in a big city or city
            if invoice_item.product.FK_Shop.State == dst_state and invoice_item.product.FK_Shop.BigCity == dst_big_city and invoice_item.product.FK_Shop.City == dst_city:
                return True
            else:
                return False

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
        for shop in invoice.shops:
            total_post_price += self._get_shop_post_price(shop, user_address)
        return total_post_price

    def _get_shop_post_price(self, shop, user_address):
        ''' Get post price from a specific shop '''
        dst_state = user_address.state
        dst_big_city = user_address.big_city
        return self.inside_city_price if shop.BigCity == dst_big_city and shop.State == dst_state\
            else self.outside_city_price

    def _get_factor_post_wieght_price(self, invocie):
        ''' Get post wieght price from factor '''
        total_post_price = 0
        # TODO: This needs more check and is not completed yet
        weight_gram = invocie.total_weight_gram or 1
        weight_kilogram = weight_gram / 1000
        if weight_kilogram > 1: # There is a fee for more than 1kg
            extra_weight = weight_kilogram - 1 # for example 2.5kg is 2.5kg - 1kg = 1.5kg
            extra_weight = int(extra_weight) + 1 # 1.5kg is 1kg when converted to int, so add 1kg 
            total_post_price += self.extra_weight_fee * extra_weight
        return total_post_price

        for weight_gram in factor.shop_total_weight:
            weight_kilogram = weight_gram / 1000
            if weight_kilogram > 1: # There is a fee for more than 1kg
                extra_weight = weight_kilogram - 1 # for example 2.5kg is 2.5kg - 1kg = 1.5kg
                extra_weight = int(extra_weight) + 1 # 1.5kg is 1kg when converted to int, so add 1kg 
                total_post_price += self.extra_weight_fee * extra_weight
        return total_post_price



