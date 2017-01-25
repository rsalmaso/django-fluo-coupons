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

import csv

from django.http import StreamingHttpResponse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _, ugettext
from django.views.generic.base import TemplateView, View
from fluo.http import JsonResponse

from .forms import CouponGenerationForm
from .models import Coupon


class Echo:
    def write(self, value):
        return value

class GenerateCouponsAdminView(TemplateView):
    template_name = "admin/coupons/generate_coupons.html"

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context["form"] = CouponGenerationForm()
        return self.render_to_response(context)

    def get_elements_as_csv(self, coupons):
        count = 0
        yield [_("Count"), _("ID"), _("Code"), _("Value"), _("Start Date"), _("Expiration Date"), _("Campaign")]
        for item in coupons:
            count += 1
            yield self.to_csv(count, item)

    def to_csv(self, count, coupon):
        return [
            count,
            coupon.pk,
            coupon.code,
            coupon.value,
            coupon.valid_from.strftime("%Y-%m-%d %H:%M:%S") if coupon.valid_from else "",
            coupon.valid_until.strftime("%Y-%m-%d %H:%M:%S") if coupon.valid_until else "",
            coupon.campaign if coupon.campaign else "",
        ]

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        form = CouponGenerationForm(self.request.POST)
        if form.is_valid():
            coupons = Coupon.objects.create_coupons(
                form.cleaned_data["quantity"],
                form.cleaned_data["type"],
                form.cleaned_data["value"],
                form.cleaned_data["valid_from"],
                form.cleaned_data["valid_until"],
                form.cleaned_data["prefix"],
                form.cleaned_data["campaign"],
            )
            buffer = Echo()
            writer = csv.writer(buffer)
            response = StreamingHttpResponse((writer.writerow(row) for row in self.get_elements_as_csv(coupons)), content_type="text/csv")
            response['Content-Disposition'] = "attachment; filename=coupons-{}.csv".format(timezone.now().strftime("-%Y%m%d-%H%M%S"))
            return response
        context["form"] = form
        return self.render_to_response(context)


def is_authenticated(user):
    import django
    if django.VERSION < (1, 10):
        return user.is_authenticated()
    return user.is_authenticated


class CheckCouponView(View):
    def post(self, request):
        if is_authenticated(request.user):
            status, message, data = 404, ugettext("not found"), {}
            code = request.POST.get("code", None)
            if code:
                try:
                    coupon = Coupon.objects.active().get(code=code)
                    #coupon = Coupon.objects.get(code=code)
                    if coupon.is_usable:
                        status, message, data = 200, ugettext("ok"), {
                            "value": coupon.value,
                            "code": coupon.code,
                            "type": coupon.type,
                        }
                except Coupon.DoesNotExist:
                    pass
        else:
            status, message, data = 403, ugettext("forbidden"), {}
        return JsonResponse({"status": status, "message": message, "data": data}, status=status)
