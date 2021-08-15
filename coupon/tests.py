from datetime import datetime, timedelta
from django.test import TestCase
from coupon.models import Coupon, CouponUsage

# Create your tests here.

class CouponTest(TestCase):
    def setUp(self):
        now = datetime.now()
        yesterday = now - timedelta(days=1)
        tomorrow = now + timedelta(days=1)
        self.coupon = Coupon.objects.create(
            code='xyz',
            valid_from=yesterday,
            valid_to=tomorrow,
            max_count=2,
            is_publish=True,
            price=10000,
            min_price=100000,
            max_price=None,
            shop=None,
            product=None,
            description='Some desc')

    def test_coupon_publish(self):
        coupon = self.coupon
        coupon.is_publish = False
        coupon.save()
        self.assertEqual(coupon.is_valid(), False)

    def test_coupon_date(self):
        now = datetime.now()
        self.coupon.valid_to = now
        self.assertEqual(self.coupon.is_valid(), False)
        
