from datetime import datetime

from django.contrib.auth.models import User
from django.test import TestCase

from coupons.forms import CouponForm
from coupons.models import Coupon


class DefaultCouponTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="user1")
        self.coupon = Coupon.objects.create_coupon('monetary', 100)
        self.form = CouponForm(data={'code': self.coupon.code}, user=self.user)

    def test_redeem(self):
        self.coupon.redeem(self.user)
        self.assertTrue(self.coupon.is_redeemed)
        self.assertEquals(self.coupon.users.count(), 1)
        self.assertIsInstance(self.coupon.users.first().redeemed_at, datetime)
        self.assertEquals(self.coupon.users.first().user, self.user)

    def test_redeem_via_form(self):
        # form should be valid
        self.assertTrue(self.form.is_valid())
        # perform redeem via form
        self.form.save()
        # coupon should be redeemed properly now
        self.assertTrue(self.coupon.is_redeemed)
        self.assertEquals(self.coupon.users.count(), 1)
        self.assertIsInstance(self.coupon.users.first().redeemed_at, datetime)
        self.assertEquals(self.coupon.users.first().user, self.user)
