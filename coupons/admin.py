# -*- coding: utf-8 -*-

# Copyright (C) 2016, Raffaele Salmaso <raffaele@salmaso.org>
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

from __future__ import absolute_import, division, print_function, unicode_literals
from django.conf.urls import url
from django import forms
from django.utils.translation import ugettext_lazy as _
from fluo import admin

from .models import Coupon, CouponUser, Campaign
from . import views
from . import get_coupon_types


class CouponUserInline(admin.ReadOnlyTabularInline):
    model = CouponUser


class CouponAdminForm(forms.ModelForm):
    type = forms.ChoiceField(
        choices=get_coupon_types,
        label=_("Type"),
    )

    class Meta:
        model = Coupon
        fields = "__all__"


class CouponAdmin(admin.ModelAdmin):
    form = CouponAdminForm
    list_display = [
        "created_at", "code", "type", "value", "user_count", "user_limit", "is_redeemed", "valid_until", "campaign"
    ]
    list_filter = ["type", "campaign", "created_at", "valid_until"]
    raw_id_fields = []
    search_fields = ["code", "value"]
    inlines = [CouponUserInline]
    exclude = ["users"]

    def user_count(self, inst):
        return inst.users.count()

    def get_urls(self):
        urls = super(CouponAdmin, self).get_urls()
        my_urls = [
            url(r"^generate-coupons$", self.admin_site.admin_view(views.GenerateCouponsAdminView.as_view()), name="generate_coupons"),
        ]
        return my_urls + urls
admin.site.register(Coupon, CouponAdmin)


class CampaignAdmin(admin.ModelAdmin):
    list_display = ["name", "num_coupons", "num_coupons_used", "num_coupons_unused", "num_coupons_expired"]

    def num_coupons(self, obj):
        return obj.coupons.count()
    num_coupons.short_description = _("coupons")

    def num_coupons_used(self, obj):
        return obj.coupons.used().count()
    num_coupons_used.short_description = _("used")

    def num_coupons_unused(self, obj):
        return obj.coupons.used().count()
    num_coupons_unused.short_description = _("unused")

    def num_coupons_expired(self, obj):
        return obj.coupons.expired().count()
    num_coupons_expired.short_description = _("expired")
admin.site.register(Campaign, CampaignAdmin)
