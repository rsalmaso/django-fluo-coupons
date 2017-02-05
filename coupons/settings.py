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

import string

from django.conf import settings
from django.utils.translation import gettext_lazy as _


COUPON_TYPES = getattr(settings, "COUPONS_COUPON_TYPES", (
    ("monetary", _("Money based coupon")),
    ("percentage", _("Percentage discount")),
    ("virtual_currency", _("Virtual currency")),
))

ACTION_TYPES = getattr(settings, "COUPONS_ACTION_TYPES", (
    ("discount", _("Discount")),
))
try:
    DEFAULT_ACTION_TYPE = getattr(settings, "COUPONS_DEFAULT_ACTION_TYPE", ACTION_TYPES[0][0])
except IndexError:
    DEFAULT_ACTION_TYPE = ""

CODE_LENGTH = getattr(settings, "COUPONS_CODE_LENGTH", 15)

CODE_CHARS = getattr(settings, "COUPONS_CODE_CHARS", string.ascii_letters+string.digits)

SEGMENTED_CODES = getattr(settings, "COUPONS_SEGMENTED_CODES", False)
SEGMENT_LENGTH = getattr(settings, "COUPONS_SEGMENT_LENGTH", 4)
SEGMENT_SEPARATOR = getattr(settings, "COUPONS_SEGMENT_SEPARATOR", "-")
