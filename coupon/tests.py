from uuid import uuid4
from datetime import datetime, timedelta
from django.test import TestCase
from django.contrib.auth import get_user_model
from invoice.models import Invoice, InvoiceItem
from nakhll_market.models import Product, Shop
from .models import Coupon


User = get_user_model()


class CouponTest(TestCase):
    """UnitTest class for Coupons and Coupon validation"""

    def generate_users(self):
        """Generate two different user for testing"""
        self.user1, _ = User.objects.get_or_create(username='1')
        self.user2, _ = User.objects.get_or_create(username='2')

    def generate_invoice(self):
        """Generate an invoice with items for testing"""
        self.shop1, _ = Shop.objects.get_or_create(Title='shop1', Slug='shop1')
        self.shop2, _ = Shop.objects.get_or_create(Title='shop2', Slug='shop2')
        self.shop3, _ = Shop.objects.get_or_create(Title='shop3', Slug='shop3')
        self.product1, _ = Product.objects.get_or_create(
            Title='product1', Slug='prod1', FK_Shop=self.shop1, Price=100000)
        self.product2, _ = Product.objects.get_or_create(
            Title='product2', Slug='prod2', FK_Shop=self.shop2, Price=100000)
        invoice, _ = Invoice.objects.get_or_create(
            user=self.user1,
            invoice_price_with_discount=1500000,
            invoice_price_without_discount=1500000,
            logistic_price=150000,
        )
        InvoiceItem.objects.get_or_create(
            invoice=invoice,
            product=self.product1,
            price_with_discount=1500000,
            price_without_discount=1500000,
            count=1,
            weight=100,
            slug=self.product1.Slug,
            name=self.product1.Title,
        )
        InvoiceItem.objects.get_or_create(
            invoice=invoice,
            product=self.product2,
            price_with_discount=1500000,
            price_without_discount=1500000,
            count=1,
            weight=100,
            slug=self.product2.Slug,
            name=self.product2.Title,
        )
        self.invoice = invoice

    def generate_coupon(self):
        """Generate a coupon for testing"""
        self.code = str(uuid4())
        coupon = Coupon.objects.create(
            code=self.code,
            available=True,
            presentage=0,
            amount=10000,
            description='Some desc')
        self.coupon = coupon

    def generate_coupon_constraints(self):
        """Generate a coupon constraints for testing"""
        self.now = datetime.now().date()
        valid_from = self.now - timedelta(days=1)
        valid_to = self.now + timedelta(days=1)
        constraint = self.coupon.constraint
        constraint.valid_from = valid_from
        constraint.valid_to = valid_to
        constraint.budget = 2000000
        constraint.max_usage_per_user = 2
        constraint.max_usage = 3
        constraint.min_purchase_amount = 100000
        constraint.min_purchase_count = None
        constraint.max_purchase_amount = None
        constraint.max_purchase_count = 10
        constraint.users.add(self.user1)
        constraint.save()
        self.constraint = constraint

    def setUp(self):
        """Setup for unit test"""
        self.generate_users()
        self.generate_invoice()
        self.generate_coupon()
        self.generate_coupon_constraints()

    def test_valid_coupon(self):
        """Generated coupon must be valid without any change"""
        self.assertEqual(self.coupon.is_valid(self.invoice), True)

    def test_availability_validation(self):
        """Coupon with available=False must be invalid"""
        self.coupon.available = False
        self.assertEqual(self.coupon.is_valid(self.invoice), False)
        self.coupon.available = True

    def test_user_validation(self):
        """Coupon for user2 must be invalid for user1"""
        self.invoice.user = self.user2
        self.assertEqual(self.coupon.is_valid(self.invoice), False)
        self.invoice.user = self.user1

    def test_count_validation(self):
        """Coupon with max_usage of negative number must be invalid"""
        coupon = self.coupon
        coupon.constraint.max_usage = -1
        self.assertEqual(coupon.is_valid(self.invoice), False)
        coupon.constraint.max_usage = 1

    def test_min_price_validation(self):
        """Coupon with minimum purchase amount of 2,500,000 must be invalid
            for this invoice with total_price of 1,500,000
        """
        coupon = self.coupon
        coupon.constraint.min_purchase_amount = 2_500_000
        self.assertEqual(coupon.is_valid(self.invoice), False)
        coupon.constraint.min_purchase_amount = 100_000

    def test_max_price_validation(self):
        """Coupon with maximum purchase amount of 20_000 must be invalid
            for this invoice with total_price of 1,500,000
        """
        coupon = self.coupon
        coupon.constraint.max_purchase_amount = 20_000
        self.assertEqual(coupon.is_valid(self.invoice), False)
        coupon.constraint.max_purchase_amount = 200_000

    def test_start_datetime_validation(self):
        """Coupon with valid_from value of yesterday must be invalid"""
        coupon = self.coupon
        coupon.constraint.valid_from = self.now + timedelta(days=2)
        self.assertEqual(coupon.is_valid(self.invoice), False)
        coupon.constraint.valid_from = self.now - timedelta(days=2)

    def test_end_datetime_validation(self):
        """Coupon with valid_to value of tomorrow must be invalid"""
        coupon = self.coupon
        coupon.constraint.valid_to = self.now - timedelta(days=2)
        self.assertEqual(coupon.is_valid(self.invoice), False)
        coupon.constraint.valid_to = self.now + timedelta(days=2)

    def test_coupon_shop_validation(self):
        """Coupon with shop1, shop2 and shop3 in coupon constraint is valid,
            but coupon with shop1 is invalid if shop1 is not in coupon
            constraint, but other shops are in coupon constraint
        """
        coupon = self.coupon
        coupon.constraint.shops.add(*[self.shop1, self.shop2, self.shop3])
        self.assertEqual(coupon.is_valid(self.invoice), True)

        coupon.constraint.shops.remove(self.shop1)
        self.assertEqual(coupon.is_valid(self.invoice), True)

        coupon.constraint.shops.remove(self.shop2)
        self.assertEqual(coupon.is_valid(self.invoice), False)

        coupon.constraint.shops.remove(self.shop3)
        self.assertEqual(coupon.is_valid(self.invoice), True)
