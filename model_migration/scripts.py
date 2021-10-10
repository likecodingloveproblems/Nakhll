import os, random, json
from django.utils import timezone
from Payment.models import (Factor, FactorPost, FactorPost, PecConfirmation,
                            PecOrder, PecReverse, PecTransaction, Coupon as OldCoupon)
from coupon.models import Coupon as NewCoupon, CouponConstraint, CouponUsage
from cart.models import Cart, CartItem
from logistic.models import Address
from accounting_new.models import Invoice, InvoiceItem
from payoff.models import Transaction, TransactionResult, TransactionConfirmation, TransactionReverse
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
            raise SkipItemException(f'User {user} already has a cart')
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
            raise SkipItemException(f'No cart created base on FactorPost with id {factor.ID}')
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
        # final_coupon_price = self.__parse_coupon_price(data)
        address_json = self.__parse_address(data)
        user = self.__parse_user(data)
        logistic_price = self.__parse_logistic_price(data)
        total_price = self.__parse_total_price(data)
        total_old_price = self.__parse_total_old_price(data)
        return {
            'user': user, 
            'old_id': data.ID,
            'FactorNumber': data.FactorNumber,
            'status': self.__parse_status(data.OrderStatus),
            'address_json': address_json,
            'invoice_price_with_discount': total_price,
            'invoice_price_without_discount': total_old_price,
            'logistic_price': logistic_price,
            'extra_data': self.__parse_extra_data(data)
        }

    def __parse_total_price(self, data):
        total = 0
        for item in data.FK_FactorPost.all():
            price = item.FK_Product.Price if item.FK_Product else 0
            count = item.ProductCount or 0
            total += price * count
        return total

    def __parse_total_old_price(self, data):
        total = 0
        for item in data.FK_FactorPost.all():
            price = item.FK_Product.OldPrice if item.FK_Product else 0
            count = item.ProductCount or 0
            total += price * count
        return total

    def __parse_logistic_price(self, data):
        try:
            return float(data.PostPrice or 0)
        except:
            raise SkipItemException(
                f'Cannot convert PostPrice to decimal: ${data.PostPrice}')

    def __parse_user(self, data):
        if not data.FK_User:
            raise SkipItemException(f'No user assigned to factor: {data.ID}')
        return data.FK_User

    def __parse_coupon_price(self, data):
        coupon_price = 0
        discount_rate = int(data.DiscountRate)
        discount_type = data.DiscountType
        total_price = int(data.TotalPrice or 0)
        logistic_price = data.PostPrice
        if discount_type == '1': # Percentage
            coupon_price = total_price * discount_rate / 100
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
            return Invoice.Statuses.AWAIT_SHOP_APPROVAL
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


class InvoiceItemMigrationScript(BaseMigrationScript):
    old_model = FactorPost
    new_model = InvoiceItem
    def parse_data(self, data):
        product = self.__parse_product(data)
        return {
            'invoice': self.__parse_invoice(data),
            'product': product,
            'count': data.ProductCount,
            'status': self.__parse_status(data),
            'slug': product.Slug,
            'name': product.Title,
            'price_with_discount': product.Price,
            'price_without_discount': product.OldPrice,
            'weight': product.Net_Weight,
            'image': self.__parse_image(product.Image),
            'image_thumbnail': self.__parse_image(product.Image_thumbnail),
            'shop_name': product.Title,
            'added_datetime': timezone.now(),
            # 'post_tracking_code': data, TODO: Calc this
        }
    
    def __parse_invoice(self, data):
        factor = data.Factor_Products.all().first()
        if not factor:
            raise SkipItemException(f'No Factor found for FactorPost: {data.ID}')
        invoice = Invoice.objects.filter(old_id=factor.ID).first()
        if not invoice:
            raise SkipItemException(f'No invoice found for Factor: {factor.ID}')
        return invoice

    def __parse_product(self, data):
        if not data.FK_Product:
            raise SkipItemException(f'No product assiged to FactorPost: {data.ID}')
        return data.FK_Product

    def __parse_status(self, data):
        status = data.ProductStatus
        if status == '0':
            return InvoiceItem.ItemStatuses.CANCELED
        if status == '1':
            return InvoiceItem.ItemStatuses.AWAIT_SHOP_APPROVAL
        if status == '2':
            return InvoiceItem.ItemStatuses.PREPATING_PRODUCT
        if status == '3':
            return InvoiceItem.ItemStatuses.AWAIT_CUSTOMER_APPROVAL
        return InvoiceItem.ItemStatuses.AWAIT_PAYMENT

    def __parse_image(self, image):
        try:
            if not image or not hasattr(image, 'path'):
                return None
            if not os.path.exists(image.path):
                return None
            return image
        except:
            return None

class CouponUsageMigrationScript(BaseMigrationScript):
    old_model = Factor
    new_model = CouponUsage
    def parse_data(self, data):
        invoice = Invoice.objects.filter(old_id=data.ID).first()
        coupon_id = data.FK_Coupon.id if data.FK_Coupon else None
        if not invoice:
            raise SkipItemException(f'Invoice with id: {data.ID} does not exists!')
        if not coupon_id:
            raise SkipItemException('Factor has no coupon assigned to')
        coupon_price = data.DiscountRate
        return {
            'invoice': invoice,
            'coupon_id': coupon_id,
            'price_applied': coupon_price,
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
            'token_request_status': str(data.Status or 200),
            'token': int(data.Token or 0),
            'token_request_message': data.Message,
            'mobile': data.Originator,
        }


class TransactionResultMigraitionScript(BaseMigrationScript):
    old_model = PecTransaction
    new_model = TransactionResult
    def parse_data(self, data):
        transaction = self.__parse_transaction(data)
        return {
            'transaction': transaction,
            'token': str(data.Token),
            'order_id': str(data.OrderId),
            'terminal_no': str(data.TerminalNo),
            'rrn': str(data.RRN),
            'status': data.status,
            'hash_card_number': data.HashCardNumber,
            'amount': str(data.Amount),
            'discounted_amount': str(data.DiscountedAmount),
        }

    def __parse_transaction(self, data):
        order_id = data.OrderId
        transaction = Transaction.objects.filter(order_number=order_id).first()
        if not transaction:
            raise SkipItemException(f'Transaction with order_id: {order_id} does not exists!')
        return transaction


class TransactionConfirmationMigrationScript(BaseMigrationScript):
    old_model = PecConfirmation
    new_model = TransactionConfirmation
    def parse_data(self, data):
        order_id = data.OrderId
        transaction_result = TransactionResult.objects.filter(order_id=order_id).first()
        return {
            'status': data.Status,
            'card_number_masked': data.CardNumberMasked,
            'token': data.Token,
            'rrn': data.RRN,
            'transaction_result': transaction_result,
            'extra_data': self.__parse_extra_data(data)
        }
    def __parse_extra_data(self, data):
        data = {
            'order_id': data.OrderId,
        }
        return json.dumps(data)


class TransactionReverseMigrationScript(BaseMigrationScript):
    old_model = PecReverse
    new_model = TransactionReverse
    def parse_data(self, data):
        order_id = data.OrderId
        transaction_result = TransactionResult.objects.filter(order_id=order_id).first()
        return {
            'status': data.Status,
            'token': data.Token,
            'message': data.Message,
            'transaction_result': transaction_result,
            'extra_data': self.__parse_extra_data(data)
        }
    def __parse_extra_data(self, data):
        data = {
            'order_id': data.OrderId,
        }
        return json.dumps(data)


