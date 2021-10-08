''' Copy all of this file into manage.py shell, then start test() function '''
from coupon.models import Coupon
from uuid import uuid4
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.utils.timezone import make_aware

me = User.objects.get(username='09384918664')
other_user = User.objects.get(id=72)
now = make_aware(datetime.now())
valid_from = now - timedelta(days=1)
valid_to = now + timedelta(days=1)
count = 2
price = 10000
min_price = 100000
max_price = None
product = None
shop = None
code = str(uuid4())


class FakeFactor:
    total_price = 200000
    products = None
    shops = None


ff = FakeFactor()


def start():
    coupon = Coupon.objects.create(
        code=code,
        valid_from=valid_from,
        valid_to=valid_to,
        max_count=count,
        is_publish=True,
        price=price,
        min_price=min_price,
        max_price=max_price,
        shop=shop,
        product=product,
        description='Some desc')
    coupon.users.add(other_user)
    print("Test 1: Check valid status")
    coupon(other_user, ff)
    assert coupon.is_valid() == True, "coupon is invalid"
    print("Test 2: Check coupon publish validation")
    coupon.is_publish = False
    coupon(other_user, ff)
    assert coupon.is_valid() == False, "is_publish invalid"
    coupon.is_publish = True
    print("Test 3: Check coupn user validation")
    coupon(me, ff)
    assert coupon.is_valid() == False, "user invalid"
    print("Test 4: Check coupon count validation")
    coupon.max_count = 1
    coupon(other_user, ff)
    if coupon.is_valid():
        coupon.apply(order=None)
    assert coupon.is_valid() == False, "max_count invalid"
    coupon.max_count = 2
    print("Test 5: Check coupon min price validation")
    coupon.min_price = 250000
    coupon(other_user, ff)
    assert coupon.is_valid() == False, "min_price invalid"
    coupon.min_price = 25000
    print("Test 6: Check coupon max price validation")
    coupon.max_price = 100000
    coupon(other_user, ff)
    assert coupon.is_valid() == False, "max_price invalid"
    coupon.max_price = 1000000
    print("Test 7: Check coupon start date validation")
    coupon.valid_from = now + timedelta(days=2)
    coupon(other_user, ff)
    assert coupon.is_valid() == False, "valid_from invalid"
    coupon.valid_from = now - timedelta(days=2)
    print("Test 8: Check coupon end date validation")
    coupon.valid_to = now - timedelta(days=2)
    coupon(other_user, ff)
    assert coupon.is_valid() == False, "valid_to invalid"
    coupon.valid_to = now + timedelta(days=2)
    print("Test 9: Check coupon price validation")
    coupon(other_user, ff)
    coupon.is_valid()
    final_price = coupon.final_price
    assert final_price == 10000, "final_price invalid"
    print("Test 10: Check coupon price validation")
    coupon.is_publish = False
    coupon(other_user, ff)
    coupon.is_valid()
    final_price = coupon.final_price
    assert final_price == None, "final_price invalid"
    





def clear():
    c = Coupon.objects.filter(code=code).first()
    if c:
        c.delete()


def test():
    try:
        start()
    finally:
        clear()

