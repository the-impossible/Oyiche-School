from django.urls import path
from oyiche_payment.views import *

app_name = "payment"

urlpatterns = [
    path("payment_dashboard", PaymentDashboard.as_view(), name="payment_dashboard"),
    path("verify_payment/", VerifyPayment.as_view(), name="verify_payment"),
    # path("payment_history", PaymentHistoryView.as_view(), name="payment_history"),
    # path("payment_settings", PaymentSettingsView.as_view(), name="payment_settings"),
]