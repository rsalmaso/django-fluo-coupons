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

from django.core.exceptions import PermissionDenied
from django.http import Http404, StreamingHttpResponse
from django.utils import timezone
from django.utils.translation import gettext, gettext_lazy as _
from django.views import View
from django.views.generic.base import TemplateView
from fluo.http import JsonResponse

from .forms import CouponGenerationForm
from .models import Coupon


class Echo:
    def write(self, value):
        return value


class GenerateCouponsAdminView(TemplateView):
    form = CouponGenerationForm
    template_name = "admin/coupons/generate_coupons.html"

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context["form"] = self.form()
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
        form = self.form(self.request.POST)
        if form.is_valid():
            coupons = Coupon.objects.create_coupons(
                quantity=form.cleaned_data["quantity"],
                type=form.cleaned_data["type"],
                action=form.cleaned_data["action"],
                value=form.cleaned_data["value"],
                valid_from=form.cleaned_data["valid_from"],
                valid_until=form.cleaned_data["valid_until"],
                prefix=form.cleaned_data["prefix"],
                campaign=form.cleaned_data["campaign"],
                code_chars=form.cleaned_data["code_chars"],
                code_length=form.cleaned_data["code_length"],
            )
            buffer = Echo()
            writer = csv.writer(buffer)
            response = StreamingHttpResponse(
                (writer.writerow(row) for row in self.get_elements_as_csv(coupons)),
                content_type="text/csv",
            )
            response['Content-Disposition'] = "attachment; filename=coupons-{}.csv".format(
                timezone.now().strftime("-%Y%m%d-%H%M%S"),
            )
            return response
        context["form"] = form
        return self.render_to_response(context)


class CheckCouponView(View):
    def handle(self, request, coupon):
        return True

    def get_queryset(self):
        code = self.request.POST.get("code")
        return Coupon.objects.active().filter(code=code)

    def get_object(self):
        queryset = self.get_queryset()
        try:
            return queryset.get()
        except Coupon.DoesNotExist:
            raise Http404

    def handle_exception(self, request, exc, *args, **kwargs):
        if isinstance(exc, Http404):
            status, message = 404, _("Not found")
        elif isinstance(exc, PermissionDenied):
            status, message = 403, _("Permission denied.")
        elif isinstance(exc, (Coupon.ExpiredError, Coupon.UserLimitError)):
            status, message = 409, _("Coupon expired.")
        else:
            status, message = 500, str(exc)
        data = {'detail': message}
        return JsonResponse({"status": status, "message": message, "data": data}, status=status)

    def post(self, request):
        coupon = self.get_object()
        if not coupon.is_usable:
            raise Coupon.UserLimitError()
        if coupon.is_expired:
            raise Coupon.ExpiredError()
        self.handle(request, coupon)
        status, message, data = 200, gettext("ok"), {
            "value": coupon.value,
            "code": coupon.code,
            "type": coupon.type,
        }
        return JsonResponse({"status": status, "message": message, "data": data}, status=status)

    def dispatch(self, request, *args, **kwargs):
        if not (request.user and request.user.is_authenticated):
            raise PermissionDenied()
        self.args = args
        self.kwargs = kwargs
        self.request = request

        try:
            response = super().dispatch(request, *args, **kwargs)
        except Exception as exc:
            response = self.handle_exception(request, exc, *args, **kwargs)

        return response
