from django.contrib.auth import get_user_model
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.db.models.aggregates import Sum
from django.db.models.functions import Cast
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from rest_framework.exceptions import ValidationError
from coupon.serializers import CouponSerializer
from coupon.validators import (DateTimeValidator, MaxUserCountValidator,
                               MaxCountValidator, PriceValidator,
                               MinPriceValidator, MaxPriceValidator,
                               ProductValidator, AvailableValidator,
                               UserValidator, ShopValidator,
                               BudgetValidator, CityValidator)
from invoice.models import Invoice, InvoiceItem
from logistic.interfaces import LogisticUnitInterface
from logistic.models import Address
from nakhll_market.models import Product, ProductManager, Shop
from nakhll_market.serializers import ProductLastStateSerializer
from payoff.exceptions import NoItemException
from cart.managers import CartItemManager, CartManager


User = get_user_model()


class Cart(models.Model):
    """Cart model which store each user's item that wants to buy

    Attributes:
        old_id: UUID of cart in previous DB version. This value is None if
            cart is new. This value is kept for only reference. This value is
            not used in any process anymore.
        extra_data: JSON string which contains extra data that migrated from
            previous DB version. This value is None for new carts. This value
            is kept for only reference. This value is not used in any process
            anymore.
        user (User): user who owns this cart
        address (Address): address of user who owns this cart, this address is
            None at first, but user must set this address before buying
        logistic_details: JSON string which contains logistic details of this
            cart. This value is None at first, but after user set address,
            calculated details of logistic unit will be set in this value.
            change in :attr:`address` should replace this value.
        coupons (Coupon): list of coupons that user used in this cart. These
            coupons is not considered as applied coupons for user. So other
            users can use these coupons without affecting coupon total usage.
            these coupons will be applied in invoice, after success buying.
        items (CartItem): list of items that user want to buy. Each item is a
            class of :class:`cart.models.CartItem`
    """
    class Meta:
        verbose_name = _('سبد خرید')
        verbose_name_plural = _('سبدهای خرید')

    old_id = models.UUIDField(null=True, blank=True)
    user = models.OneToOneField(
        User,
        verbose_name=_('کاربر'),
        on_delete=models.CASCADE,
        related_name='cart',
        null=True)
    guest_unique_id = models.CharField(
        _('شناسه کاربر مهمان'),
        max_length=100, null=True, blank=True)
    extra_data = models.JSONField(null=True, encoder=DjangoJSONEncoder)
    address = models.ForeignKey(
        Address,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invoices',
        verbose_name=_('آدرس'))
    logistic_details = models.JSONField(
        null=True, blank=True, encoder=DjangoJSONEncoder,
        verbose_name=_('جزئیات واحد ارسال'))
    coupons = models.ManyToManyField(
        'coupon.Coupon',
        verbose_name=_('کوپن ها'),
        blank=True)
    objects = CartManager()

    @property
    def total_discount(self):
        """Total amount of discount of all products in cart

        This is different from coupons discount which user can get by setting
        coupon before payment. This discount is set by shop manager in
        creation process of product.
        """
        discounts = []
        for item in self.items.all():
            price = item.product.Price
            old_price = item.product.OldPrice or price
            discount = (old_price - price) * item.count
            discounts.append(discount)
        return sum(discounts)

    @property
    def cart_price(self):
        """Total price of items in cart

        This is the discounted-price of items multiplied by each items count
        Note that, this is not the end price that user should pay. It must be
        added to shipping price. Also total coupons price must be deducted
        from this price.
        """
        prices = []
        for item in self.items.all():
            price = item.product.Price
            prices.append(price * item.count)
        return sum(prices)

    @property
    def cart_old_price(self):
        """Total price of items without shop owner discount

        This price is not used for any calculation. It is just for
        user to see the price before discount in the cart page.
        """
        old_prices = []
        for item in self.items.all():
            price = item.product.Price
            old_price = item.product.OldPrice or price
            old_prices.append(old_price * item.count)
        return sum(old_prices)

    @property
    def shops(self):
        """All shops that have products in cart

            Returns:
                QuerySet: queryset of shops
        """
        shop_ids = self.items.values_list(
            'product__FK_Shop__ID', flat=True).distinct()
        return Shop.objects.filter(ID__in=shop_ids)

    @property
    def products(self):
        """All products in cart

        Returns:
            QuerySet: queryset of products
        """
        product_ids = self.items.values_list(
            'product__ID', flat=True).distinct()
        return Product.objects.filter(ID__in=product_ids)

    @property
    def logistic_price(self):
        """Calculated value of logistic price

        If :attr:`logistic_details` is not set, this method will return 0.

        Returns:
            int: logistic price
        """
        return self.logistic_details.get(
            'total_price', 0) if self.logistic_details else 0

    @property
    def cart_weight(self):
        """Total weight of items in cart

        Returns:
            int: total weight of items in cart
        """
        return self.items.aggregate(tw=Sum(Cast(
            'product__Weight_With_Packing', output_field=models.IntegerField()
        )))['tw'] or 0

    @property
    def total_price(self):
        """Total price of items in cart including shipping price and coupons

        Returns:
            int: total price of items in cart
        """
        total_coupon_price = sum([coupon['price']
                                 for coupon in self.get_coupons_price()])
        return self.cart_price + self.logistic_price - total_coupon_price

    @property
    def ordered_items(self):
        """Return all cart items in order by shop"""
        return self.items.order_by('-product__FK_Shop')

    def convert_to_invoice(self):
        """Convert cart to invoice

        Validate invoice, items, coupons and logistic details in cart, create
        invoice from cart and clear cart items.

        Returns:
            Invoice: created invoice
        """
        logistic_details = self._generate_logistic_details()
        self._validate_coupons()
        self._validate_items()
        invoice = self._create_invoice(logistic_details)
        self._clear_cart_items()
        return invoice

    def _create_invoice(self, lud):
        """Create invoice from cart

        Args:
            lud (LogisticUnit): logistic unit object which includes all
                details of logistic unit in cart

        Returns:
            Invoice: created invoice
        """
        invoice = Invoice.objects.create(
            user=self.user,
            created_datetime=timezone.now(),
            invoice_price_with_discount=self.cart_price,
            invoice_price_without_discount=self.cart_old_price,
            total_weight_gram=self.cart_weight,
            logistic_price=lud.total_price,
            logistic_unit_details=lud.as_dict(),
            address_json=self.address.as_json(),
        )
        validators_list = [
            DateTimeValidator(),
            MaxUserCountValidator(self.user),
            MaxCountValidator(),
            PriceValidator(self),
            MinPriceValidator(self),
            MaxPriceValidator(self),
            ProductValidator(self),
            AvailableValidator(),
            UserValidator(self.user),
            ShopValidator(self),
            BudgetValidator(),
            CityValidator(self),
        ]
        for coupon in self.coupons.all():
            if coupon.is_valid(self, validators_list):
                coupon.apply(invoice)

        cart_items = self.items.all()
        for item in cart_items:
            item.convert_to_invoice_item(invoice)

        return invoice

    def _clear_cart_items(self):
        """Remove all items in cart"""
        self.items.all().delete()

    def _validate_items(self):
        """Check if there is at least on item in cart"""
        if self.items.count() < 1:
            raise NoItemException

    def add_product(self, product):
        """Add product to cart

        This function do all validations to add item in cart. Therefore, it's
        beter to use this function in any end point that user can add product,
        instead of directly adding item in cart.

        Args:
            product (Product): the product to add

        Raises:
            ValidationError: raise if product is not available
            ValidationError: raise if shop owner has not enough item in stock

        Returns:
            CartItem: created cart item
        """
        cart_item = CartItem.objects.filter(product=product, cart=self).first()
        count = cart_item.count + 1 if cart_item else 1

        if not product.is_available():
            raise ValidationError(_('محصول در دسترس نیست'))

        if not ProductManager.has_enough_items_in_stock(product, count):
            raise ValidationError(
                _('فروشنده قادر به تامین کالا به میزان درخواستی شما نمی‌باشد'))

        product_jsonify = ProductLastStateSerializer(product).data
        if cart_item:
            cart_item.count = count
            cart_item.product_last_state = product_jsonify
            cart_item.save()
        else:
            cart_item = CartItem.objects.create(
                cart=self,
                product=product,
                count=count,
                added_datetime=timezone.now(),
                product_last_state=product_jsonify
            )
        return cart_item

    @staticmethod
    def get_cart(request):
        """Get or create a cart for current user or guest

        It does not require authentication. Guest users can have a cart too,
        which is stored in database with a unique id, called guid.
        This guid is stored as a cookie in the client, user should send it
        with every request to be able to get his/her cart.

        Args:
            user (User): if provided, we will get or create a cart for
                this user, if not, this is a cart for a guest user.
            guid (str, optional): if user provided, this item we will get or
                create a cart for this guest, if guid not provided, we will
                generate a new one

        Returns:
            Cart: cart for current user or guest
        """
        user = request.user if request.user.is_authenticated else None
        guid = request.COOKIES.get('guest_unique_id')
        if user and guid:
            CartManager.convert_guest_to_user_cart(user, guid)
        if user:
            return Cart._get_user_cart(user)
        return Cart._get_guest_cart(guid)

    @staticmethod
    def _get_user_cart(user):
        """Given an authenticated user, it will return users cart"""
        cart, _ = Cart.objects.get_or_create(
            user=user)
        return cart

    @staticmethod
    def _get_guest_cart(guid):
        """Given guest unique id, it will return guest cart"""
        cart, _ = Cart.objects.get_or_create(
            guest_unique_id=guid or CartManager.generate_guid())
        return cart

    def get_coupon_errors(self):
        """Validate all coupons in cart and return errors as list

        Returns:
            list: list of errors
        """
        errors = []
        validators_list = [
            DateTimeValidator(),
            MaxUserCountValidator(self.user),
            MaxCountValidator(),
            PriceValidator(self),
            MinPriceValidator(self),
            MaxPriceValidator(self),
            ProductValidator(self),
            AvailableValidator(),
            UserValidator(self.user),
            ShopValidator(self),
            BudgetValidator(),
            CityValidator(self),
        ]
        for coupon in self.coupons.all():
            if coupon.is_valid(self, validators_list):
                continue
            errors.extend(coupon.errors)
        return errors

    def get_coupons_price(self):
        """Get price of all coupons in cart

        Returns:
            list: list of coupons details with applied price.
            example:

            .. code-block:: python

                [
                    {'coupon': {
                        'code': 'xyz',
                        'title': 'XYZ',
                        'descriptoin': ''
                    }, 'price': 100},
                ]

        """
        result = []
        for coupon in self.coupons.all():
            price = coupon.calculate_coupon_price()
            result.append({
                'coupon': CouponSerializer(coupon).data,
                'price': price
            })
        return result

    def _generate_logistic_details(self):
        lui = LogisticUnitInterface(self)
        lui.generate_logistic_unit_list()
        return lui

    def _validate_coupons(self):
        errors = self.get_coupon_errors()
        if errors:
            raise errors

    def reset_coupons(self):
        """Remove all coupons in cart

        Removing coupons is necessary when user changes his/her cart, as
        changing cart may invalidates some of the coupons. So user has to
        re-submit his/her coupons and validate them again.
        """
        self.coupons.clear()

    def reset_address(self):
        """Remove user address from cart

        Removing user address is necessary when user changes his/her cart, as
        new items in cart may not be available in user's address. So user has
        re-submit his/her addresss and validate it again.
        """
        self.address = None
        self.logistic_details = None
        self.save()


class CartItem(models.Model):
    """Each Item in Cart

    Attributes:
        cart (Cart): cart that this item belongs to
        product (Product): product that this item belongs to
        count (int): count of this item
        added_datetime: datetime when this item was added to cart
        product_last_state: used previously to store product last state
            to compare any change in product, but now it is not used
            anymore.
        extra_data: same as :attr:`cart.models.Cart.extra_data`.
    """
    class Meta:
        verbose_name = 'کالای سبد خرید'
        verbose_name_plural = 'کالاهای سبد خرید'

    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, verbose_name=_(
        'آیتم‌های سبد خرید'), related_name='items')
    product = models.ForeignKey(Product, verbose_name=_(
        'محصول'), on_delete=models.CASCADE, related_name='cart_items')
    count = models.PositiveSmallIntegerField(verbose_name=_('تعداد'))
    added_datetime = models.DateTimeField(
        _('زمان اضافه شدن'), auto_now_add=True)
    product_last_state = models.JSONField(null=True, encoder=DjangoJSONEncoder)
    objects = CartItemManager()
    extra_data = models.JSONField(null=True, encoder=DjangoJSONEncoder)

    @property
    def get_total_old_price(self):
        """Get total old price of this single cart item multiplied by count

        Returns:
            int: total old price
        """
        return int(self.product.OldPrice) * self.count

    @property
    def get_total_price(self):
        """Get total price of this single cart item multiplied by count

        Returns:
            int: total price
        """
        return int(self.product.Price) * self.count

    def convert_to_invoice_item(self, invoice):
        """Convert item to invoice item during invoice creation from cart"""
        InvoiceItem.objects.create(
            invoice=invoice,
            product=self.product,
            count=self.count,
            name=self.product.Title,
            slug=self.product.Slug,
            price_with_discount=self.product.Price,
            price_without_discount=self.product.OldPrice or self.product.Price,
            weight=self.product.Weight_With_Packing,
            shop_name=self.product.FK_Shop.Title,
            added_datetime=timezone.now(),
        )

    def reduce_count(self):
        """Reduce count of this cart item by 1, or remove it if count is 1"""
        if self.count == 1:
            self.delete()
        else:
            self.count = self.count - 1
            self.save()
