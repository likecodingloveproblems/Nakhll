import os
from django.core import serializers
from django.db import models
from django.db.models.lookups import EndsWith
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.core.serializers.json import DjangoJSONEncoder
from accounting_new.models import Invoice, InvoiceItem
from cart.managers import CartItemManager, CartManager
from nakhll_market.models import Product
from nakhll_market.serializers import ProductLastStateSerializer


class Cart(models.Model):
    class Meta:
        verbose_name = _('سبد خرید')
        verbose_name_plural = _('سبدهای خرید')
    # class Statuses(models.TextChoices):
        # IN_PROGRESS = 'running', _('در حال اجرا')
        # ARCHIVED = 'archived', _('بایگانی شده')

    old_id = models.UUIDField(null=True, blank=True)
    user = models.OneToOneField(User, verbose_name=_('کاربر'), on_delete=models.CASCADE, related_name='cart', null=True)
    #// sessions will be deleted in django by clearsession command, so we assign 
    #// a cart for not-logged-in users by session
    #// session = models.ForeignKey(Session, verbose_name=_('Session کاربر'), on_delete=models.CASCADE, null=True)
    # In Token auth, no session used, so I should use a unique id instead of session
    guest_unique_id = models.CharField(_('شناسه کاربر مهمان'), max_length=100, null=True, blank=True)
    # status = models.CharField(max_length=10, verbose_name=_('وضعیت سبد خرید'), choices=Statuses.choices, default=Statuses.IN_PROGRESS)
    # created_datetime = models.DateTimeField(verbose_name=_('تاریخ ثبت سبد خرید'), auto_now_add=True)
    # change_status_datetime = models.DateTimeField(verbose_name=_('تاریخ تغییر وضعیت سبد'), null=True)
    extra_data = models.JSONField(null=True, encoder=DjangoJSONEncoder)
    objects = CartManager()

    @property
    def total_discount(self):
        discounts = []
        for item in self.items.all():
            price = item.product.Price 
            old_price = item.product.OldPrice or price
            discount = (old_price - price) * item.count
            discounts.append(discount)
        return sum(discounts)

    @property
    def total_old_price(self):
        old_prices= []
        for item in self.items.all():
            price = item.product.Price 
            old_price = item.product.OldPrice or price
            old_prices.append(old_price * item.count)
        return sum(old_prices)

    @property
    def shops(self):
        # TODO: Needs improvement
        shops = set()
        for item in self.items.all():
            shops.add(item.product.FK_Shop)
        return shops

    @property
    def products(self):
        # TODO: Needs improvement
        products = set()
        for item in self.items.all():
            products.add(item.product)
        return products

    @property
    def cart_weight(self):
        # TODO: Needs improvement
        total_weight = 0
        for item in self.items.all():
            try:
                product_weight = int(item.product.Weight_With_Packing)
            except:
                product_weight = 0
            total_weight += product_weight
        return total_weight

    @property
    def total_price(self):
        prices = []
        for item in self.items.all():
            price = item.product.Price 
            prices.append(price * item.count)
        return sum(prices)


    def check_cart_items(self):
        ''' Check for changes and product statuses in every item in cart, show changes for now '''
        # TODO
        return None

    @property
    def get_diffrences(self):
        ''' Compare current and latest state of products in the cart and show diffrences 
        '''
        # TODO: Check functionallity deeply
        items = self.items.all()
        diffs = {}
        for item in items:
            diff = self.__get_item_diffs(item.product, item.product_last_state)
            if diff:
                diffs[item.product_last_state.get('Title')] = diff
        return diffs

    @staticmethod
    def __get_item_diffs(item, item_json):
        diffs = []
        if not item_json:
            return []
        for key in item_json:
           old = item_json[key] 
           new = getattr(item, key)
           if old != new:
               diffs.append({'prop': key, 'old': old, 'new': new})
        return diffs


    @property
    def ordered_items(self):
        ''' Return all cart items in order by shop'''
        return self.items.order_by('-product__FK_Shop')

    # def archive(self):
    #     ''' Archive this cart '''
    #     self.status = self.Statuses.CLOSED
    #     self.save()

    def convert_to_invoice(self):
        ''' Convert cart to invoice '''
        invoice = Invoice.objects.create(
            user=self.user,
            created_datetime=timezone.now(),
            invoice_price_with_discount=self.total_price,
            invoice_price_without_discount=self.total_old_price or self.total_price,
            total_weight_gram=self.cart_weight,
        )
        cart_items = self.items.all()
        for item in cart_items:
            item.convert_to_invoice_item(invoice)
        self.__clear_items()
        return invoice

    def __clear_items(self):
        self.items.all().delete()

    def add_product(self, product):
        product_jsonify = ProductLastStateSerializer(product).data
        cart_item = CartItem.objects.create(
            cart=self,
            product=product,
            count=1,
            added_datetime=timezone.now(),
            product_last_state=product_jsonify
        )
        return cart_item

class CartItem(models.Model):
    class Meta:
        verbose_name = 'کالای سبد خرید'
        verbose_name_plural = 'کالاهای سبد خرید'

    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, verbose_name=_(
        'آیتم‌های سبد خرید'), related_name='items')
    product = models.ForeignKey(Product, verbose_name=_(
        'محصول'), on_delete=models.CASCADE, related_name='cart_items')
    count = models.PositiveSmallIntegerField(verbose_name=_('تعداد'))
    added_datetime = models.DateTimeField(_('زمان اضافه شدن'), auto_now_add=True)
    product_last_state = models.JSONField(null=True, encoder=DjangoJSONEncoder)
    objects = CartItemManager()
    extra_data = models.JSONField(null=True, encoder=DjangoJSONEncoder)

    @property
    def get_total_old_price(self):
        return int(self.product.OldPrice) * self.count

    @property
    def get_total_price(self):
        return int(self.product.Price) * self.count

    def get_cartitem_changes(self):
        ''' Check for any changes, show them to user and save new product state as last_known_state '''

    def convert_to_invoice_item(self, invoice):
        ''' Convert cart item to invoice item '''
        image = self.product.Image if os.path.exists(self.product.Image.path) else None
        image_thumbnail = self.product.Image_thumbnail if os.path.exists(self.product.Image_thumbnail.path) else None
        InvoiceItem.objects.create(
            invoice=invoice,
            product=self.product,
            count=self.count,
            name=self.product.Title,
            slug=self.product.Slug,
            price_with_discount=self.product.Price,
            price_without_discount=self.product.OldPrice or self.product.Price,
            weight=self.product.Weight_With_Packing,
            image=image,
            image_thumbnail=image_thumbnail,
            shop_name=self.product.FK_Shop.Title,
            added_datetime=timezone.now(),
        )

