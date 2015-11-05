from datetime import datetime

from django.contrib.auth.models import User
from django.test import TestCase

from coupons.forms import CouponForm
from coupons.models import Coupon


class DefaultCouponTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="user1")
        self.coupon = Coupon.objects.create_coupon('monetary', 100)

    def test_redeem(self):
        self.coupon.redeem(self.user)
        self.assertTrue(self.coupon.is_redeemed)
        self.assertEquals(self.coupon.users.count(), 1)
        self.assertIsInstance(self.coupon.users.first().redeemed_at, datetime)
        self.assertEquals(self.coupon.users.first().user, self.user)

    def test_redeem_via_form(self):
        form = CouponForm(data={'code': self.coupon.code}, user=self.user)
        # form should be valid
        self.assertTrue(form.is_valid())
        # perform redeem
        self.coupon.redeem(self.user)
        # coupon should be redeemed properly now
        self.assertTrue(self.coupon.is_redeemed)
        self.assertEquals(self.coupon.users.count(), 1)
        self.assertIsInstance(self.coupon.users.first().redeemed_at, datetime)
        self.assertEquals(self.coupon.users.first().user, self.user)
        # form should be invalid after redeem
        self.assertTrue(form.is_valid())

    def test_redeem_via_form_without_user(self):
        form = CouponForm(data={'code': self.coupon.code})
        # form should be valid
        self.assertTrue(form.is_valid())
        # perform redeem
        self.coupon.redeem()
        # coupon should be redeemed properly now
        self.assertTrue(self.coupon.is_redeemed)
        self.assertEquals(self.coupon.users.count(), 1)
        self.assertIsInstance(self.coupon.users.first().redeemed_at, datetime)
        self.assertIsNone(self.coupon.users.first().user)
        # form should be invalid after redeem
        self.assertTrue(form.is_valid())


class SingleUserCouponTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="user1")
        self.coupon = Coupon.objects.create_coupon('monetary', 100, self.user)

    def test_user_limited_coupon(self):
        self.assertEquals(self.coupon.users.count(), 1)
        self.assertEquals(self.coupon.users.first().user, self.user)
        # not redeemed yet
        self.assertIsNone(self.coupon.users.first().redeemed_at)

    def test_redeem_with_user(self):
        self.coupon.redeem(self.user)
        # coupon should be redeemed properly now
        self.assertTrue(self.coupon.is_redeemed)
        self.assertEquals(self.coupon.users.count(), 1)
        self.assertIsInstance(self.coupon.users.first().redeemed_at, datetime)
        self.assertEquals(self.coupon.users.first().user, self.user)

    def test_form_without_user(self):
        """ This should fail since the coupon is bound to an user, but we do not provide any user. """
        form = CouponForm(data={'code': self.coupon.code})
        self.assertFalse(form.is_valid())
        self.assertEquals(
            form.errors,
            {'code': ['This code is not valid for your account.']}
        )

    def test_redeem_with_user_twice(self):
        self.test_redeem_with_user()
        # try to redeem again with form
        form = CouponForm(data={'code': self.coupon.code}, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertEquals(
            form.errors,
            {'code': ['This code has already been used.']}
        )


class UnlimitedCouponTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="user1")
        self.coupon = Coupon.objects.create_coupon('monetary', 100, user_limit=0)

    def test_redeem_with_user(self):
        self.coupon.redeem(self.user)
        # coupon is not redeemed since it can be used unlimited times
        self.assertFalse(self.coupon.is_redeemed)
        # coupon should be redeemed properly now
        self.assertEquals(self.coupon.users.count(), 1)
        self.assertIsInstance(self.coupon.users.first().redeemed_at, datetime)
        self.assertEquals(self.coupon.users.first().user, self.user)

    def test_redeem_with_multiple_users(self):
        for i in range(100):
            user = User.objects.create(username="test%s" % (i))
            form = CouponForm(data={'code': self.coupon.code}, user=user)
            self.assertTrue(form.is_valid())

    def test_form_without_user(self):
        """ This should fail since we cannot track single use of a coupon without an user. """
        form = CouponForm(data={'code': self.coupon.code})
        self.assertFalse(form.is_valid())
        self.assertEquals(
            form.errors,
            {'code': ['The server must provide an user to this form to allow you to use this code. Maybe you need to sign in?']}
        )

    def test_redeem_with_user_twice(self):
        self.test_redeem_with_user()
        # try to redeem again with form
        form = CouponForm(data={'code': self.coupon.code}, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertEquals(
            form.errors,
            {'code': ['This code has already been used by your account.']}
        )
