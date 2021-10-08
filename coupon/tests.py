from uuid import uuid4
from datetime import datetime, timedelta
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils.timezone import make_aware
from coupon.models import Coupon, CouponConstraint, CouponUsage


# Create your tests here.

class CouponTest(TestCase):

    def generate_users(self):
        self.user1, _ = User.objects.get_or_create(username='1')
        self.user2, _ = User.objects.get_or_create(username='2')
 
    def generate_invoice(self):
        class FakeInvoice:
            total_price = 200000
            products = None
            shops = None
            class cart:
                user = self.user1
        self.invoice = FakeInvoice()

    def generate_coupon(self):
        self.code = str(uuid4())
        coupon = Coupon.objects.create(
            code=self.code,
            available=True,
            presentage=0, 
            amount=10000,
            description='Some desc')
        self.coupon = coupon

    def generate_coupon_constraints(self):
        self.now = datetime.now().date()
        valid_from = self.now - timedelta(days=1)
        valid_to = self.now + timedelta(days=1)
        constraint = self.coupon.constraint
        constraint.valid_from=valid_from
        constraint.valid_to=valid_to
        constraint.budget=2000000
        constraint.max_usage_per_user=2
        constraint.max_usage=3
        constraint.min_purchase_amount=100000
        constraint.min_purchase_count=None
        constraint.max_purchase_amount=None
        constraint.max_purchase_count=10
        constraint.users.add(self.user1)
        constraint.save()
        self.constraint = constraint




    def setUp(self):
        self.generate_users()
        self.generate_invoice()
        self.generate_coupon()
        self.generate_coupon_constraints()

    def test_valid_coupon(self):
        self.assertEqual(self.coupon.is_valid(self.invoice), True)

    def test_availability_validation(self):
        self.coupon.available = False
        self.assertEqual(self.coupon.is_valid(self.invoice), False)
        self.coupon.available = True
    
    def test_user_validation(self):
        self.invoice.cart.user = self.user2
        self.assertEqual(self.coupon.is_valid(self.invoice), False)
        self.invoice.cart.user = self.user1

    # def test_count_validation(self):
    #     coupon = self.coupon
    #     coupon.constraint.max_usage = 0
    #     self.assertEqual(coupon.is_valid(self.invoice), False)
    #     coupon.constraint.max_usage = 1
    
    def test_min_price_validation(self):
        coupon = self.coupon
        coupon.constraint.min_purchase_amount = 250000
        self.assertEqual(coupon.is_valid(self.invoice), False)
        coupon.constraint.min_purchase_amount = 100000

    def test_max_price_validation(self):
        coupon = self.coupon
        coupon.constraint.max_purchase_amount = 20000
        self.assertEqual(coupon.is_valid(self.invoice), False)
        coupon.constraint.max_purchase_amount = 200000




    # def test_start_datetime_validation(self):
    #     coupon = self.coupon
    #     coupon.valid_from = self.now + timedelta(days=2)
    #     coupon(self.other_user, self.invoice)
    #     self.assertEqual(coupon.is_valid(self.invoice), False)
    #     coupon.valid_from = self.now - timedelta(days=2)

    # def test_end_datetime_validation(self):
    #     coupon = self.coupon
    #     coupon.valid_to = self.now - timedelta(days=2)
    #     coupon(self.other_user, self.invoice)
    #     self.assertEqual(coupon.is_valid(self.invoice), False)
    #     coupon.valid_to = self.now + timedelta(days=2)

    # def test_price_validation(self):
    #     coupon = self.coupon
    #     coupon(self.other_user, self.invoice)
    #     coupon.is_valid(self.invoice)
    #     final_price = coupon.final_price
    #     self.assertEqual(final_price, 10000)

    #     coupon.is_publish = False
    #     coupon(self.other_user, self.invoice)
    #     coupon.is_valid(self.invoice)
    #     final_price = coupon.final_price
    #     self.assertEqual(final_price, None)
 
