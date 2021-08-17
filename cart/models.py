from django.core import serializers
from django.db import models
from django.db.models.lookups import EndsWith
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.core.serializers.json import DjangoJSONEncoder
from cart.managers import CartItemManager, CartManager
from nakhll_market.models import Product

# Create your models here.

# NOTE: These should be considered in design phase
#   - This is a minimal solution for users to be able to buy products and
#     many things can be added to it, so be prepared!
#   - unregistered users should be able to add products to cart
#   - After login, cart should be assigned to user
#   - If not logged-in user, add products to cart and never came back,
#     then the cart should be deleted after some time (like a week)
#   - Changes sice user add produdct to cart, should be stored
#   - Check if products is available or has enough inventory (when?)
#   - Conserning about changes in product, there is some approachs
#       -- Save last known details of product and notice user from changes
#           --- Changes should save base on each field or jsonify whole
#               product and compare it with prev json?
#       -- Delete changed product and ask user to re-add it to cart
#          (why? owner may change product to something completely different)
#       -- Support stop owner from that kind of changes
#       -- A combination of these approachs


#       nextjs                     comm data                       django
# ----------------------------------------------------------------------------
#                       |                               |
#                       |                               |
#   non logged in user  |                               |
#   send a product to   |                               | 
#   store in cart       |           product_id=5        |
#                       |  ---------------------------> | django check if guid is
#                       |                               | available or not, if not,
#                       |                               | create new cart with guid
#                       |            guid=xyz           | and send it to nextjs
#                       |  <--------------------------  | 
#   save guid and send  |                               |
#   it back to server   |                               |
#   with next requests  |                               |
#                       |    product_id=7, guid=xyz     |
#                       |  ---------------------------> |
#                       |                               | get guid, and save new 
#                       |                               | products in related cart
#                       |                               |
#                       |                               |
#  user logged in       |                               |
#  send login data      |                               |
#  with guid            |                               |
#                       |     user, password, guid      |
#                       |  -------------------------->  |
#                       |                               | convert guid to user
#                       |                               | 



# NOTE: CART FUNCTIONS
#   -Create Card
#   --logged-in users
#   --non logged-in users
#   -convert cart
#   -add to cart
#   -delete from cart
#   -check cart items
#   -clear cart
#   -send cart to accounting
#   -change cart state
#   -jsonify cart


class Cart(models.Model):
    class Meta:
        verbose_name = _('سبد خرید')
        verbose_name_plural = _('سبدهای خرید')
    class Statuses(models.TextChoices):
        IN_PROGRESS = 'prog', _('در حال اجرا')
        CLOSED = 'fact', _('بسته شده')
    user = models.ForeignKey(User, verbose_name=_(
        'کاربر'), on_delete=models.CASCADE, related_name='cart', null=True)
    #// sessions will be deleted in django by clearsession command, so we assign 
    #// a cart for not-logged-in users by session
    #// session = models.ForeignKey(Session, verbose_name=_('Session کاربر'), on_delete=models.CASCADE, null=True)
    # In Token auth, no session used, so I should use a unique id instead of session
    guest_unique_id = models.CharField(_('شناسه کاربر مهمان'), max_length=100, null=True, blank=True)
    status = models.CharField(max_length=4, verbose_name=_('وضعیت سبد خرید'), choices=Statuses.choices, default=Statuses.IN_PROGRESS)
    created_datetime = models.DateTimeField(verbose_name=_('تاریخ ثبت سبد خرید'), auto_now_add=True)
    change_status_datetime = models.DateTimeField(verbose_name=_('تاریخ تغییر وضعیت سبد'), null=True)
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
        shops = []
        for item in self.items.all():
            shop = item.product.FK_Shop
            if shop not in shops:
                shops.append(shop)
        return shops

    @property
    def products(self):
        # TODO: Needs improvement
        products = []
        for item in self.items.all():
            products.append(item.product)
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
        return sum([item.product.Price * item.count for item in self.items.all()])

    def check_cart_items(self):
        ''' Check for changes and product statuses in every item in cart, show changes for now '''
        return None

    @property
    def get_diffrences(self):
        ''' Compare current and last state of products in the cart and show diffrences 
            TODO: Discuss needed for:
            For now, I just comapre them and return them both as comparing one by one
            should be done in another module (maybe a third-party). 
        '''
        # TODO: Check functionallity deeply
        items = self.cart_items.all()
        last_items_json = f"[{','.join([item.product_last_known_state for item in items])}]"
        products = [item.product for item in items]
        new_items_json = serializers.serialize('json', products, ensure_ascii=False)
        return (
            last_items_json != new_items_json,
            last_items_json, new_items_json)

    @property
    def ordered_items(self):
        ''' Return all cart items in order by shop'''
        return self.items.order_by('-product__FK_Shop')



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
    product_last_known_state = models.JSONField(encoder=DjangoJSONEncoder)
    objects = CartItemManager()

    @property
    def get_total_old_price(self):
        return int(self.product.OldPrice) * self.count

    @property
    def get_total_price(self):
        return int(self.product.Price) * self.count

    def get_cartitem_changes(self):
        ''' Check for any changes, show them to user and save new product state as last_known_state '''
        pass

   

class CartTransmission(models.Model):
    class Meta:
        verbose_name = _('ارسال سبد خرید')
        verbose_name_plural = _('ارسال‌های سبد خرید')
    
    cart = models.ForeignKey(Cart, verbose_name=_('سبد خرید'), on_delete=models.CASCADE, related_name='transmissions')
    datetime = models.DateTimeField(_('زمان ارسال'), auto_now_add=True)
