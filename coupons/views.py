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
from django.utils.translation import ugettext_lazy as _
from django.views.generic.base import TemplateView
from django.contrib import messages

from .forms import CouponGenerationForm
from .models import Coupon


class GenerateCouponsAdminView(TemplateView):
    template_name = "admin/coupons/generate_coupons.html"

    def get_context_data(self, **kwargs):
        context = super(GenerateCouponsAdminView, self).get_context_data(**kwargs)
        if self.request.method == "POST":
            form = CouponGenerationForm(self.request.POST)
            if form.is_valid():
                context["coupons"] = Coupon.objects.create_coupons(
                    form.cleaned_data["quantity"],
                    form.cleaned_data["type"],
                    form.cleaned_data["value"],
                    form.cleaned_data["valid_until"],
                    form.cleaned_data["prefix"],
                    form.cleaned_data["campaign"],
                )
                messages.success(self.request, _("Your coupons have been generated."))
        else:
            form = CouponGenerationForm()
        context["form"] = form
        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)
