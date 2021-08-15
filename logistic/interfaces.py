from rest_framework.validators import ValidationError


class PostPriceSettingInterface:
    ''' Create an interface for other apps to communicate with PostPriceSetting

        This class should be inharited by PostPriceSetting model.
        It provide some functionallities for other apps to use.
        After inharitance, self variable reference to a setting object
        which contains prices to calculate post_price.
    '''


    def _is_vaild_shop_post_range(self, shop, user_address):
        ''' Check if user_address is in range of shop post range '''
        dst_state = user_address.state
        dst_big_city = user_address.big_city
        dst_city = user_address.city

        if shop.PostRangeType == '1': # This is a post inside coutry and is true
            return True
        elif shop.PostRangeType == '2': # This is a post in a state
            if dst_state == shop.State:
                return True
            return False
        elif shop.PostRangeType == '3' or shop.PostRangeType == '4': # This is a post in a big city or city
            if shop.State == dst_state and shop.BigCity == dst_big_city and shop.City == dst_city:
                return True
            else:
                return False

    def get_out_of_range_shops(self, factor):
        ''' Check if all shops in factor can sent to user address'''
        if not all(hasattr(factor, 'shops') and hasattr(factor, 'user_address')):
            msg = 'factor should have attribute shops'
            raise ValidationError(msg)

        user_address = factor.user_address
        out_of_range_shops = []
        for shop in factor.shops.all():
            if self._is_vaild_shop_post_range(shop, user_address):
                out_of_range_shops.append(shop) 
        return out_of_range_shops

        

    def get_post_price(self, factor):
        ''' Calculate each shop post_price based on user address '''
        if not all(hasattr(factor, 'shops') and hasattr(factor, 'user_address')):
            msg = 'factor should have attribute shops'
            raise ValidationError(msg)
        if not self.is_valid_post_range(factor):
            msg = 'There is errors in post_range. Run .is_valid_post_range(factor) to see them'
            raise ValidationError(msg)
        post_range_price = self._get_factor_post_range_price(factor)
        post_wieght_price = self._get_factor_post_wieght_price(factor)
        return post_range_price + post_wieght_price

        
    def _get_factor_post_range_price(self, factor):
        ''' Get post range price from factor '''
        user_address = factor.user_address
        total_post_price = 0
        for shop in factor.shops.all():
            total_post_price += self._get_shop_post_price(shop, user_address)
        return total_post_price

    def _get_shop_post_price(self, shop, user_address):
        ''' Get post price from a specific shop '''
        dst_state = user_address.state
        dst_big_city = user_address.big_city
        return self.inside_city_price if shop.BigCity == dst_big_city and shop.State == dst_state\
            else self.outside_city_price

    def _get_factor_post_wieght_price(self, factor):
        ''' Get post wieght price from factor '''
        total_post_price = 0
        for weight_gram in factor.shop_total_weigths:
            weight_kilogram = weight_gram / 1000
            if weight_kilogram > 1: # There is a fee for more than 1kg
                extra_weight = weight_kilogram - 1 # for example 2.5kg is 2.5kg - 1kg = 1.5kg
                extra_weight = int(extra_weight) + 1 # 1.5kg is 1kg when converted to int, so add 1kg 
                total_post_price += self.extra_weight_fee * extra_weight
        return total_post_price



