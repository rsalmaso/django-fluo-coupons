from distutils.version import StrictVersion
from unittest import skipIf

import django
from coupons.admin import CouponAdmin
from coupons.models import Coupon
from django.contrib.admin.sites import AdminSite
from django.test import TestCase


class MockRequest(object):
    pass


request = MockRequest()


class CouponAdminTestCase(TestCase):
    def setUp(self):
        self.site = AdminSite()

    @skipIf(StrictVersion(django.get_version()) < StrictVersion('1.7'), "Skip list display test due to missing method.")
    def test_list_display(self):
        admin = CouponAdmin(Coupon, self.site)

        self.assertEquals(
            list(admin.get_fields(request)),
            ['value', 'code', 'type', 'user_limit', 'valid_from', 'valid_until', 'campaign']
        )
