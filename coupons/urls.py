from django.conf.urls import url

from . import views

urlpatterns = [
    url(r"^check$", views.CheckCouponView.as_view(), name="coupons-check"),
]
