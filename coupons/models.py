# Copyright (C) 2016-2017, Raffaele Salmaso <raffaele@salmaso.org>
# Copyright (C) 2013, byteweaver
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     * Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of django-coupons nor the names of its contributors may
#       be used to endorse or promote products derived from this software without
#       specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import random

from django.conf import settings
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.dispatch import Signal
from django.utils import timezone
from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy as _
from fluo.db import models

from . import exceptions
from .settings import (
    ACTION_TYPES, CODE_CHARS, CODE_LENGTH, COUPON_TYPES, DEFAULT_ACTION_TYPE, SEGMENT_LENGTH, SEGMENT_SEPARATOR,
    SEGMENTED_CODES,
)

redeem_done = Signal(providing_args=["coupon"])


class Campaign(models.TimestampModel):
    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name=_("Name"),
    )
    description = models.TextField(
        blank=True,
        verbose_name=_("Description"),
    )

    class Meta:
        ordering = ["name"]
        verbose_name = _("Campaign")
        verbose_name_plural = _("Campaigns")

    def __str__(self):
        return self.name


class CouponQuerySet(models.QuerySet):
    def used(self):
        return self.exclude(users__redeemed_at__isnull=True)

    def unused(self):
        return self.filter(users__redeemed_at__isnull=True)

    def expired(self):
        return self.filter(valid_until__lt=timezone.now())

    def active(self):
        now = timezone.now()
        q1 = Q(Q(valid_from__isnull=True) | Q(valid_from__lte=now))
        q2 = Q(Q(valid_until__isnull=True) | Q(valid_until__gte=now))
        return self.filter(q1 & q2)


class CouponManager(models.Manager.from_queryset(CouponQuerySet)):
    def create_coupon(self, type, action, value, users=[], valid_from=None, valid_until=None, prefix="", campaign=None, user_limit=None, code_chars=CODE_CHARS, code_length=CODE_LENGTH):  # noqa
        coupon = self.create(
            value=value,
            code=Coupon.generate_code(prefix=prefix, code_chars=code_chars, code_length=code_length),
            type=type,
            action=action,
            valid_from=valid_from,
            valid_until=valid_until,
            campaign=campaign,
        )
        if user_limit is not None:  # otherwise use default value of model
            coupon.user_limit = user_limit
        try:
            coupon.save()
        except IntegrityError:
            # Try again with other code
            coupon = Coupon.objects.create_coupon(
                type=type,
                action=action,
                value=value,
                users=users,
                valid_from=valid_from,
                valid_until=valid_until,
                prefix=prefix,
                campaign=campaign,
                code_chars=code_chars,
                code_length=code_length,
            )
        if not isinstance(users, list):
            users = [users]
        for user in users:
            if user:
                CouponUser(user=user, coupon=coupon).save()
        return coupon

    def create_coupons(self, quantity, type, action, value, valid_from=None, valid_until=None, prefix="", campaign=None, code_chars=CODE_CHARS, code_length=CODE_LENGTH):  # noqa
        return [
            self.create_coupon(
                type=type,
                action=action,
                value=value,
                users=None,
                valid_from=valid_from,
                valid_until=valid_until,
                prefix=prefix,
                campaign=campaign,
                code_chars=code_chars,
                code_length=code_length,
            )
            for i in range(quantity)
        ]

    def redeem(self, code, user, source=None, action=None):
        q = {"code": code}
        if action is not None:
            q["action"] = action
        coupon = self.active().get(**q)
        return coupon.redeem(user=user, source=source)


class Coupon(models.TimestampModel):
    Error = exceptions.CouponError
    UserLimitError = exceptions.CouponUserLimitError
    ExpiredError = exceptions.CouponExpiredError

    objects = CouponManager()

    value = models.IntegerField(
        verbose_name=_("Value"),
        help_text=_("Arbitrary coupon value"),
    )
    code = models.CharField(
        max_length=30,
        unique=True,
        blank=True,
        verbose_name=_("Code"),
        help_text=_("Leaving this field empty will generate a random code."),
    )
    type = models.CharField(
        choices=COUPON_TYPES,
        max_length=20,
        verbose_name=_("Type"),
    )
    action = models.CharField(
        choices=ACTION_TYPES,
        max_length=20,
        blank=True,
        default=DEFAULT_ACTION_TYPE,
        verbose_name=_("Action"),
    )
    user_limit = models.PositiveIntegerField(
        default=1,
        verbose_name=_("User limit"),
    )
    valid_from = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_("Valid from"),
        help_text=_("Coupons are valid from this date"),
    )
    valid_until = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_("Valid until"),
        help_text=_("Coupons expire at this date"),
    )
    campaign = models.ForeignKey(
        Campaign,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="coupons",
        verbose_name=_("Campaign"),
    )

    class Meta:
        ordering = ["created_at"]
        verbose_name = _("Coupon")
        verbose_name_plural = _("Coupons")

    def __str__(self):
        return self.code

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = Coupon.generate_code()
        super().save(*args, **kwargs)

    def expired(self):
        return self.is_expired

    @property
    def is_expired(self):
        return self.valid_until is not None and self.valid_until < timezone.now()

    @property
    def is_redeemed(self):
        """ Returns true is a coupon is redeemed (completely for all users) otherwise returns false. """
        return self.users.filter(
            redeemed_at__isnull=False
        ).count() >= self.user_limit and self.user_limit is not 0

    @property
    def redeemed_at(self):
        try:
            return self.users.filter(redeemed_at__isnull=False).order_by('redeemed_at').last().redeemed_at
        except self.users.through.DoesNotExist:
            return None

    @classmethod
    def generate_code(cls, prefix="", segmented=SEGMENTED_CODES, code_chars=CODE_CHARS, code_length=CODE_LENGTH):
        code = "".join(random.choice(code_chars) for i in range(code_length))
        if segmented:
            code = SEGMENT_SEPARATOR.join([code[i:i + SEGMENT_LENGTH] for i in range(0, len(code), SEGMENT_LENGTH)])
            return prefix + code
        else:
            return prefix + code

    @property
    def is_usable(self):
        user_limit = self.user_limit
        is_usable = -1 < CouponUser.objects.filter(coupon=self).count() < user_limit
        if is_usable:
            is_usable = self.do_is_usable_pipeline()
        return is_usable

    @transaction.atomic
    def redeem(self, user=None, source=None, **kwargs):
        if not self.is_usable:
            raise Coupon.UserLimitError()

        coupon_user = CouponUser(coupon=self, user=user)
        coupon_user.redeemed_at = timezone.now()
        if source is not None:
            coupon_user.source_type = models.ContentType.objects.get_for_model(source)
            coupon_user.source_id = source.pk

        coupon_user.save()
        redeem_done.send(sender=self.__class__, coupon=self)

        self.do_redeem_pipeline(coupon_user=coupon_user, user=user, source=source, **kwargs)

        return coupon_user

    def do_is_usable_pipeline(self, **kwargs):
        coupon = self
        for name in getattr(settings, "COUPONS_IS_USABLE_PIPELINE", []):
            pipeline = import_string(name)
            coupon, is_usable = pipeline(coupon=coupon, **kwargs)
            if not is_usable:
                return False
        return True

    def do_redeem_pipeline(self, **kwargs):
        coupon = self
        for name in getattr(settings, "COUPONS_REDEEM_PIPELINE", []):
            pipeline = import_string(name)
            coupon = pipeline(coupon=coupon, **kwargs)


class CouponUser(models.TimestampModel):
    coupon = models.ForeignKey(
        Coupon,
        on_delete=models.CASCADE,
        related_name="users",
        verbose_name=_("Coupon"),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_("User"),
    )
    redeemed_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_("Redeemed at"),
    )
    source_type = models.ForeignKey(
        models.ContentType,
        db_index=True,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("source content type"),
    )
    source_id = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name=_("source id"),
    )
    source = models.GenericForeignKey(
        "source_type", "source_id",
    )

    class Meta:
        verbose_name = _("Coupon")
        verbose_name_plural = _("Coupons")

    def __str__(self):
        return str(self.user)
