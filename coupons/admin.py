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
from django.contrib import admin
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.views.generic.base import TemplateView

from .forms import CouponGenerationForm
from .models import Coupon, CouponUser, Campaign


class CouponUserInline(admin.TabularInline):
    model = CouponUser
    extra = 0

    def get_max_num(self, request, obj=None, **kwargs):
        if obj:
            return obj.user_limit
        return None  # disable limit for new objects (e.g. admin add)


class CouponAdmin(admin.ModelAdmin):
    list_display = [
        'created_at', 'code', 'type', 'value', 'user_count', 'user_limit', 'is_redeemed', 'valid_until', 'campaign'
    ]
    list_filter = ['type', 'campaign', 'created_at', 'valid_until']
    raw_id_fields = ()
    search_fields = ('code', 'value')
    inlines = (CouponUserInline,)
    exclude = ('users',)

    def user_count(self, inst):
        return inst.users.count()

    def get_urls(self):
        urls = super(CouponAdmin, self).get_urls()
        my_urls = [
            url(r'generate-coupons', self.admin_site.admin_view(GenerateCouponsAdminView.as_view()), name='generate_coupons'),
        ]
        return my_urls + urls


class GenerateCouponsAdminView(TemplateView):
    template_name = 'admin/generate_coupons.html'

    def get_context_data(self, **kwargs):
        context = super(GenerateCouponsAdminView, self).get_context_data(**kwargs)
        if self.request.method == 'POST':
            form = CouponGenerationForm(self.request.POST)
            if form.is_valid():
                context['coupons'] = Coupon.objects.create_coupons(
                    form.cleaned_data['quantity'],
                    form.cleaned_data['type'],
                    form.cleaned_data['value'],
                    form.cleaned_data['valid_until'],
                    form.cleaned_data['prefix'],
                    form.cleaned_data['campaign'],
                )
                messages.success(self.request, _("Your coupons have been generated."))
        else:
            form = CouponGenerationForm()
        context['form'] = form
        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)


class CampaignAdmin(admin.ModelAdmin):
    list_display = ['name', 'num_coupons', 'num_coupons_used', 'num_coupons_unused', 'num_coupons_expired']

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


admin.site.register(Coupon, CouponAdmin)
admin.site.register(Campaign, CampaignAdmin)
