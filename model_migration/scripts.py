import random, json
from re import I
from django.utils import timezone
from Payment.models import (Factor, FactorPost, FactorPost,
                            PecOrder, PecTransaction, Coupon as OldCoupon)
from coupon.models import Coupon as NewCoupon, CouponConstraint, CouponUsage
from cart.models import Cart, CartItem
from logistic.models import Address
from accounting_new.models import Invoice
from payoff.models import Transaction, TransactionResult
from model_migration.exceptions import SkipItemException
from model_migration.base import BaseMigrationScript



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
    cart_users = set()
    def parse_data(self, data):
        self.__parse_status(data.PaymentStatus)
        user = self.__parse_user(data.FK_User)
        return {
            'old_id': data.ID,
            'user': user,
            'guest_unique_id': None,
        }
    def __parse_user(self, user):
        if user in self.cart_users:
            raise SkipItemException('User ${user} already has a cart')
        self.cart_users.add(user)

    def __parse_status(self, is_paid):
        if is_paid:
            raise SkipItemException('This factor is paid, not creating cart form it')

class CartItemMigrationScript(BaseMigrationScript):
    old_model = FactorPost
    new_model = CartItem
    def parse_data(self, data):
        factor = data.Factor_Products.first()
        if not factor:
            raise SkipItemException('This FactorPost has no factor assigned to')
        if not data.FK_Product:
            raise SkipItemException('This FactorPost has no product')
        cart = Cart.objects.filter(old_id=factor.ID).first()
        if not cart:
            raise SkipItemException(f'No cart created base on FactorPost with id ${factor.ID}')
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
        final_coupon_price = self.__parse_coupon_price(data)
        address_json = self.__parse_address(data)
        return {
            'old_id': data.ID,
            'FctorNumber': data.FactorNumber,
            'status': self.__parse_status(data.OrderStatus),
            'address_json': address_json,
            'logistic_price': data.PostPrice,
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
            return Invoice.Statuses.AWAIT_PAYMENT
        elif order_status == '4':
            return Invoice.Statuses.CANCELED
        elif order_status == '5':
            return Invoice.Statuses.AWAIT_CUSTOMER_APPROVAL
        else:
            return Invoice.Statuses.AWAIT_PAYMENT

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
            'TotalPrice': data.TotalPrice,
            'FK_Staff_Checkout': data.FK_Staff_Checkout.id if data.FK_Staff_Checkout else None,
        }

class CouponUsageMigrationScript(BaseMigrationScript):
    old_model = Factor
    new_model = CouponUsage
    def parse_data(self, data):
        invoice = Invoice.objects.filter(old_id=data.ID).first()
        coupon_id = data.FK_Coupon.id if data.FK_Coupon else None
        if not invoice or not coupon_id:
            raise SkipItemException('Invoice with id: ${data.ID} does not exists!')
        if not coupon_id:
            raise SkipItemException(f'Factor has no coupon assigned to')
        return {
            'invoice': invoice,
            'coupon_id': coupon_id,
            'price_applied': data.DiscountRate,
        }

class TransactionMigrationScript(BaseMigrationScript):
    old_model = PecOrder
    new_model = Transaction
    def parse_data(self, data):
        return {
            'referrer_model': 'Invoice',
            'referrer_app': 'accounting_new',
            'amount': data.Amount,
            'order_number': data.FactorNumber,
            'created_datetime': timezone.now(),
            'payoff_datetime': timezone.now(),
            'description': data.AdditionalData,
            'ipg': Transaction.IPGTypes.PEC,
            'token_request_status': str(data.Stauts or 200),
            'token': int(data.Token or 0),
            'token_request_message': data.Message,
            'mobile': data.Orginator,
        }


class TransactionResultMigrationScript(BaseMigrationScript):
    old_model = PecTransaction
    new_model = TransactionResult
    def parse_data(self, data):
        order_id = data.OrderId
        transaction = Transaction.objects.filter(order_number=order_id).first()
        return {
            'transaction': transaction,
            'token': data.Token,
            'order_id': order_id,
            'terminal_no': data.TerminalNo,
            'rrn': data.RRN,
            'status': data.status,
            'hash_card_number': data.HashCartNumber,
            'amount': data.Amount,
            'discounted_amount': data.DiscountedAmount,
            'created_datetime': timezone.now(),
        }