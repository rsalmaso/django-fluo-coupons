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

from django import forms
from django.contrib.admin.widgets import AdminSplitDateTime
from django.utils.translation import gettext_lazy as _

from . import settings
from .models import Campaign, Coupon, CouponUser


class CouponGenerationForm(forms.Form):
    campaign = forms.ModelChoiceField(
        required=False,
        queryset=Campaign.objects.all(),
        label=_("Campaign"),
    )
    quantity = forms.IntegerField(
        label=_("Quantity"),
    )
    value = forms.IntegerField(
        label=_("Value"),
    )
    type = forms.ChoiceField(
        choices=settings.COUPON_TYPES,
        label=_("Type"),
    )
    action = forms.ChoiceField(
        choices=settings.ACTION_TYPES,
        label=_("Action"),
    )
    valid_from = forms.SplitDateTimeField(
        required=False,
        widget=AdminSplitDateTime,
        label=_("Valid from"),
        help_text=_("Coupons are valid from this date"),
    )
    valid_until = forms.SplitDateTimeField(
        required=False,
        widget=AdminSplitDateTime,
        label=_("Valid until"),
        help_text=_("Coupons expire at this date"),
    )
    prefix = forms.CharField(
        required=False,
        label=_("Prefix"),
    )
    code_length = forms.IntegerField(
        initial=settings.CODE_LENGTH,
        label=_("Code length"),
        help_text=_("Number of characters of generated code"),
    )
    code_chars = forms.CharField(
        initial=settings.CODE_CHARS,
        label=_("Code symbols"),
        help_text=_("Use these charaters to generate code"),
    )


class CouponForm(forms.Form):
    code = forms.CharField(
        label=_("Coupon code"),
    )

    def __init__(self, *args, **kwargs):
        self.user = None
        self.types = None
        if "user" in kwargs:
            self.user = kwargs["user"]
            del kwargs["user"]
        if "types" in kwargs:
            self.types = kwargs["types"]
            del kwargs["types"]
        super().__init__(*args, **kwargs)

    def clean_code(self):
        code = self.cleaned_data["code"]
        try:
            coupon = Coupon.objects.get(code=code)
        except Coupon.DoesNotExist:
            raise forms.ValidationError(_("This code is not valid."))
        self.coupon = coupon

        if self.user is None and coupon.user_limit is not 1:
            # coupons with can be used only once can be used without tracking the user, otherwise there is no chance
            # of excluding an unknown user from multiple usages.
            raise forms.ValidationError(_(
                "The server must provide an user to this form to allow you to use this code. Maybe you need to sign in?"
            ))

        if coupon.is_redeemed:
            raise forms.ValidationError(_("This code has already been used."))

        try:  # check if there is a user bound coupon existing
            user_coupon = coupon.users.get(user=self.user)
            if user_coupon.redeemed_at is not None:
                raise forms.ValidationError(_("This code has already been used by your account."))
        except CouponUser.DoesNotExist:
            if coupon.user_limit is not 0:  # zero means no limit of user count
                # only user bound coupons left and you don't have one
                if coupon.user_limit is coupon.users.filter(user__isnull=False).count():
                    raise forms.ValidationError(_("This code is not valid for your account."))
                if coupon.user_limit is coupon.users.filter(redeemed_at__isnull=False).count():  # all coupons redeemed
                    raise forms.ValidationError(_("This code has already been used."))
        if self.types is not None and coupon.type not in self.types:
            raise forms.ValidationError(_("This code is not meant to be used here."))
        if coupon.expired():
            raise forms.ValidationError(_("This code is expired."))
        return code
