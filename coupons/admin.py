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
from django.conf.urls import url
from django.utils.translation import gettext_lazy as _
from fluo import admin

from . import views
from .models import Campaign, Coupon, CouponUser


class CouponUserInline(admin.ReadOnlyTabularInline):
    model = CouponUser


class CouponAdminForm(forms.ModelForm):
    pass


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    form = CouponAdminForm
    generate_coupons_view = views.GenerateCouponsAdminView
    list_display = ["code", "type", "_user_count", "value", "_user_limit", "_is_redeemed", "valid_from", "valid_until", "campaign"]  # noqa: E501
    list_filter = ["type", "action", "campaign", "created_at", "valid_from", "valid_until"]
    raw_id_fields = []
    search_fields = ["code", "value"]
    inlines = [CouponUserInline]
    related_search_fields = {
        "user": ("pk", "username", "first_name", "last_name", "email"),
        "campaign": ("pk", "name"),
    }

    def _user_count(self, coupon):
        return coupon.users.count()
    _user_count.short_description = _("user count")

    def _user_limit(self, coupon):
        return coupon.user_limit
    _user_limit.short_description = _("user limit")

    def _is_redeemed(self, coupon):
        return coupon.is_redeemed
    _is_redeemed.short_description = _("is redeemed")

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            url(r"^generate-coupons$", self.admin_site.admin_view(self.generate_coupons_view.as_view()), name="generate_coupons"),  # noqa
        ]
        return my_urls + urls


class CouponInline(admin.ReadOnlyTabularInline):
    model = Coupon
    exclude = ["created_at", "last_modified_at"]


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ["name", "num_coupons", "num_coupons_used", "num_coupons_unused", "num_coupons_expired", "created_at"]  # noqa
    inlines = [CouponInline]

    def num_coupons(self, obj):
        return obj.coupons.count()
    num_coupons.short_description = _("coupons")

    def num_coupons_used(self, obj):
        return obj.coupons.used().count()
    num_coupons_used.short_description = _("used")

    def num_coupons_unused(self, obj):
        return obj.coupons.unused().count()
    num_coupons_unused.short_description = _("unused")

    def num_coupons_expired(self, obj):
        return obj.coupons.expired().count()
    num_coupons_expired.short_description = _("expired")
