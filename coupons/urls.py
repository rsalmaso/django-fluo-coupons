try:
    from django.urls import re_path as url
except ImportError:
    from django.conf.urls import url

from . import views

urlpatterns = [
    url(r"^check$", views.CheckCouponView.as_view(), name="coupons-check"),
]
