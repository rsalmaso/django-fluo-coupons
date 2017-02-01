import re
from datetime import timedelta

from coupons.models import Campaign, Coupon
from coupons.settings import (CODE_CHARS, CODE_LENGTH, SEGMENT_LENGTH,
                              SEGMENT_SEPARATOR)
from django.test import TestCase
from django.utils import timezone


class CouponTestCase(TestCase):
    def test_generate_code(self):
        self.assertIsNotNone(re.match("^[%s]{%d}" % (CODE_CHARS, CODE_LENGTH,), Coupon.generate_code()))

    def test_generate_code_segmented(self):
        num_segments = CODE_LENGTH // SEGMENT_LENGTH  # full ones
        num_rest = CODE_LENGTH - num_segments * SEGMENT_LENGTH
        self.assertIsNotNone(
            re.match(
                "^([{chars}]{{{sl}}}{sep}){{{ns}}}[{chars}]{{{nr}}}$".format(
                    chars=CODE_CHARS,
                    sep=SEGMENT_SEPARATOR,
                    sl=SEGMENT_LENGTH,
                    ns=num_segments,
                    nr=num_rest),
                Coupon.generate_code("", True)
            )
        )

    def test_save(self):
        coupon = Coupon(type='monetary', value=100)
        coupon.save()
        self.assertTrue(coupon.pk)

    def test_create_coupon(self):
        coupon = Coupon.objects.create_coupon(type='monetary', value=100)
        self.assertTrue(coupon.pk)

    def test_create_coupons(self):
        coupons = Coupon.objects.create_coupons(quantity=50, type='monetary', value=100)
        for coupon in coupons:
            self.assertTrue(coupon.pk)

    def test_redeem(self):
        coupon = Coupon.objects.create_coupon(type='monetary', value=100)
        coupon.redeem()
        self.assertIsNotNone(coupon.redeemed_at)

    def test_expired(self):
        coupon = Coupon.objects.create_coupon(type='monetary', value=100)
        self.assertFalse(coupon.expired())
        self.assertEqual(Coupon.objects.expired().count(), 0)
        coupon.valid_until = timezone.now() - timedelta(1)
        coupon.save()
        self.assertTrue(coupon.expired())
        self.assertEqual(Coupon.objects.expired().count(), 1)

    def test_coupon_already_active_and_not_yet_expired(self):
        now = timezone.now()
        coupon = Coupon.objects.create_coupon(
            type='monetary',
            value=100,
            valid_from=now - timedelta(1),
            valid_until=now + timedelta(2),
        )
        self.assertFalse(coupon.expired())
        self.assertEqual(Coupon.objects.active().count(), 1)

    def test_coupon_with_no_initial_date_and_not_yet_expired(self):
        now = timezone.now()
        coupon = Coupon.objects.create_coupon(
            type='monetary',
            value=100,
            valid_from=None,
            valid_until=now + timedelta(2),
        )
        self.assertFalse(coupon.expired())
        self.assertEqual(Coupon.objects.active().count(), 1)

    def coupon_not_yet_active_and_not_yet_expired(self):
        now = timezone.now()
        coupon = Coupon.objects.create_coupon(
            type='monetary',
            value=100,
            valid_from=now + timedelta(1),
            valid_until=now + timedelta(2),
        )
        self.assertFalse(coupon.expired())
        self.assertEqual(Coupon.objects.active().count(), 0)

    def test_str(self):
        coupon = Coupon.objects.create_coupon(type='monetary', value=100)
        self.assertEqual(coupon.code, str(coupon))

    def test_prefix(self):
        coupon = Coupon.objects.create_coupon(type='monetary', value=100, users=None, valid_from=None, valid_until=None, prefix="prefix-")
        self.assertTrue(coupon.code.startswith("prefix-"))

    def test_used_unused(self):
        coupon = Coupon.objects.create_coupon(type='monetary', value=100)
        self.assertEqual(Coupon.objects.used().count(), 0)
        self.assertEqual(Coupon.objects.unused().count(), 1)
        coupon.redeem()
        coupon.save()
        self.assertEqual(Coupon.objects.used().count(), 1)
        self.assertEqual(Coupon.objects.unused().count(), 0)


class CampaignTestCase(TestCase):
    def test_str(self):
        campaign = Campaign(name="test")
        campaign.save()
        self.assertEqual("test", str(campaign))
