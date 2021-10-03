import random, json, datetime, jdatetime
from Payment.models import Factor, FactorPost, FactorPost, Coupon as OldCoupon
from coupon.models import Coupon as NewCoupon, CouponConstraint, CouponUsage
from cart.models import Cart, CartItem
from logistic.models import Address
from accounting_new.models import Invoice
from payoff.models import Transaction, TransactionResult

class SkipItemException(Exception):
    pass

class BaseMigrationScript:
    old_model = None
    new_model = None
    many2many_relation_fields = []
    _datetime_str_format = '%Y-%m-%d %H:%M:%S'
    _date_str_format = '%Y-%m-%d'

    def __init__(self):
        self._all_parsed_data = []

    def migrate(self):
        ''' Get all data from old model, parse them and create new model'''
        old_data = self.get_old_model_data()
        for data in old_data:
            try:
                parsed_data = self.parse_data(data)
                self._all_parsed_data.append(parsed_data)
            except SkipItemException:
                print('Cannot parse, Skiping item: {}'.format(data))
        self.create_new_model()

    def __jsonify(self, data):
        ''' Convert data to json '''
        data = data.__dict__
        del data['_state']
        for item in data:
            if isinstance(data[item], datetime.datetime) or isinstance(data[item], jdatetime.datetime):
                data[item] = data[item].strftime(self._datetime_str_format)
            elif isinstance(data[item], datetime.date) or isinstance(data[item], jdatetime.date):
                data[item] = data[item].strftime(self._date_str_format)
        return data

    def get_old_model_data(self):
        ''' Get all data from old model '''
        assert self.old_model is not None, 'old_model is not defined. You should define old_model attribute or override .get_old_model_data()'
        return self.old_model.objects.all()


    def parse_data(self, data):
        ''' Parse old data to new model fields'''
        raise NotImplementedError('`parse_data()` must be implemented.')

    def create_new_model(self):
        ''' Create new model '''
        assert self.new_model is not None, 'new_model is not defined. You should define new_model attribute or override .create_new_model()'
        assert self._all_parsed_data is not [], 'Parsed data is empty. You should parse data before creating new model'
        if self.many2many_relation_fields:
            self.__onebyone_create_method()
        else:
            self.__bulk_create_method()


    def __bulk_create_method(self):
        bulk_list = []
        for data in self._all_parsed_data:
            bulk_list.append(self.new_model(**data))
        self.new_model.objects.bulk_create(bulk_list)

    def __onebyone_create_method(self):
        for data in self._all_parsed_data:
            many2many_fields = dict()
            for item in self.many2many_relation_fields:
                many2many_fields[item] = data.pop(item)
            instance = self.new_model.objects.create(**data)
            for key, value in many2many_fields.items():
                instance_field = getattr(instance, key)
                instance_field.set(value)
            instance.save()
















class CouponMigrationScript(BaseMigrationScript):
    old_model = OldCoupon
    new_model = NewCoupon
    serials = set()
    def parse_data(self, data):
        amount, presentage = self.__parse_coupon_value(data)
        serial = self.__get_unique_serial(data.SerialNumber)
        return {
            'id': data.id,
            'code': serial,
            'title': data.Title,
            'description': data.Description,
            'amount': amount,
            'max_amount': 0,
            'presentage': presentage,
            'creator': data.FK_Creator,
            'available': data.Available and data.Publish,
            'log': data.Log,
        }

    def __parse_coupon_value(self, data):
        if data.DiscountType == '1':
            amount = 0
            presentage = data.DiscountRate
        else:
            amount = data.DiscountRate
            presentage = 0
        return amount, presentage

    def __get_unique_serial(self, serial):
        new_serial = serial
        while new_serial in self.serials:
            rand_int = random.randint(11, 99)
            new_serial = f'DUPLICATED_{serial}_{rand_int}'
        self.serials.add(new_serial)
        return new_serial

class CouponConstraintMigrationScript(BaseMigrationScript):
    old_model = OldCoupon
    new_model = CouponConstraint
    many2many_relation_fields = ['users', 'shops', 'products']
    def parse_data(self, data):
        return {
            'coupon_id': data.id,
            'users': data.FK_Users.all(),
            'shops': data.FK_Shops.all(),
            'products': data.FK_Products.all(),
            'valid_from': data.StartDate.togregorian(),
            'valid_to': data.EndDate.togregorian(),
            'budget': 0,
            'max_usage_per_user': data.NumberOfUse,
            'max_usage': data.max_total_number_of_use,
            'min_purchase_amount': data.MinimumAmount,
            'min_purchase_count': 0,
            'max_purchase_amount': data.MaximumAmount,
            'max_purchase_count': 0,
            'extra_data': self.__parse_extra_data(data)
        }

    def __parse_extra_data(self, data):
        data = {
            'FK_Categories': list(data.FK_Categories.all().values_list('id', flat=True)),
            'TextRequest': data.TextRequest,
            'FK_InvitationShops': list(data.FK_InvitationShops.all().values_list('id', flat=True)),
        }
        return json.dumps(data)



class CartMigrationScript(BaseMigrationScript):
    old_model = Factor
    new_model = Cart
    def parse_data(self, data):
        status = self.__parse_status(data.PaymentStatus)
        return {
            'old_id': data.ID,
            'user': data.FK_User,
            'guest_unique_id': None,
            'status': status,
            'created_datetime': data.OrderDate,
            'extra_data': self.__parse_extra_data(data)
        }
    def __parse_status(self, is_paid):
        if is_paid:
            return Cart.Statuses.ARCHIVED
        return Cart.Statuses.IN_PROGRESS
    def __parse_extra_data(self, data):
        return {
            'Description': data.Description,
        }

class CartItemMigrationScript(BaseMigrationScript):
    old_model = FactorPost
    new_model = CartItem
    def parse_data(self, data):
        factor = data.Factor_Products.first()
        if not factor:
            raise SkipItemException()
        if not data.FK_Product:
            raise SkipItemException()
        cart = Cart.objects.get(old_id=factor.ID)
        return {
            'cart': cart,
            'product': data.FK_Product,
            'count': data.ProductCount,
            'extra_data': self.__parse_extra_data(data)
        }
    def __parse_extra_data(self, data):
        return {
            'EndPrice': data.EndPrice,
            'Description': data.Description,
            'FK_User': data.FK_User.username if data.FK_User else None,
            'ProductStatus': data.ProductStatus,
            'FK_AttrPrice': list(data.FK_AttrPrice.all().values_list('id', flat=True)),
        }
    

class InvoiceMigrationScript(BaseMigrationScript):
    old_model = Factor
    new_model = Invoice
    def parse_data(self, data):
        cart = Cart.objects.filter(old_id=data.ID).first()
        if not cart:
            raise SkipItemException()
        final_coupon_price = self.__parse_coupon_price(data)
        address_json = self.__parse_address(data)
        return {
            'old_id': data.ID,
            'FctorNumber': data.FactorNumber,
            'status': self.__parse_status(data.OrderStatus),
            'cart': cart,
            'address_json': address_json,
            'final_logistic_price': data.PostPrice,
            'final_invoice_price': data.TotalPrice,
            'extra_data': self.__parse_extra_data(data)
        }

    def __parse_coupon_price(self, data):
        coupon_price = 0
        discount_rate = int(data.DiscountRate)
        discount_type = data.DiscountType
        logistic_price = data.PostPrice
        if discount_type == '1': # Percentage
            coupon_price = data.TotalPrice * discount_rate / 100
        elif discount_type == '2': # amount
            coupon_price = discount_rate
        else:
            coupon_price = logistic_price
        return coupon_price

    def __parse_status(self, order_status):
        if order_status == '0':
            return Invoice.Statuses.AWAIT_SHOP_CHECKOUT
        elif order_status == '1':
            return Invoice.Statuses.AWAIT_CUSTOMER_APPROVAL
        elif order_status == '2':
            return Invoice.Statuses.PREPATING_PRODUCT
        elif order_status == '3':
            return Invoice.Statuses.AWAIT_PAYING
        elif order_status == '4':
            return Invoice.Statuses.CANCELED
        elif order_status == '5':
            return Invoice.Statuses.AWAIT_CUSTOMER_APPROVAL
        else:
            return Invoice.Statuses.AWAIT_PAYING

    def __parse_address(self, data):
        address_data = {
            'MobileNumber': data.MobileNumber,
            'ZipCode': data.ZipCode,
            'Address': data.Address,
            'Location': data.Location,
            'FaxNumber': data.FaxNumber,
            'CityPerCode': data.CityPerCode,
            'City': data.City,
            'BigCity': data.BigCity,
            'State': data.State,
            'PhoneNumber': data.PhoneNumber,
        }
        json.dumps(address_data)

    def __parse_extra_data(self, data):
        delivery_date = data.DeliveryDate.togregorian().\
            strftime(self._date_str_format) if data.DeliveryDate else None
        return {
            'CountrPreCode': data.CountrPreCode,
            'FactorType': data.FactorType,
            'ShopInfo': data.ShopInfo,
            'UserInfo': data.UserInfo,
            'FK_Campaign': data.FK_Campaign.id if data.FK_Campaign else None,
            'CampaingType': data.CampaingType,
            'PaymentType': data.PaymentType,
            'DeleveryDate': delivery_date,
            'FK_Staff': data.FK_Staff.id if data.FK_Staff else None,
            'FK_Staff_Checkout': data.FK_Staff_Checkout.id if data.FK_Staff_Checkout else None,
        }

class CouponUsageMigrationScript(BaseMigrationScript):
    old_model = Factor
    new_model = CouponUsage
    def parse_data(self, data):
        invoice = Invoice.objects.filter(old_id=data.ID).first()
        coupon_id = data.FK_Coupon.id if data.FK_Coupon else None
        if not invoice or not coupon_id:
            raise SkipItemException()
        return {
            'invoice': invoice,
            'coupon_id': coupon_id,
            'price_applied': data.DiscountRate,
        }

class TransactionMigrationScript(BaseMigrationScript):
    old_model = ''
    new_model = Transaction
    def parse_data(self, data):
        pass

class TransactionResultMigrationScript(BaseMigrationScript):
    old_model = ''
    new_model = TransactionResult
    def parse_data(self, data):
        pass