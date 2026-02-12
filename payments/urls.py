from django.urls import path
from .views import (
    PaymentCreateView,
    PaymentListView,
    PaymentDetailView,
    PaymentLogListView,
    ClickPrepareView,
    ClickCompleteView,
    PaymeWebhookView,
)

app_name = "payments"

urlpatterns = [
    # Customer endpoints
    path("create/", PaymentCreateView.as_view(), name="create"),
    path("", PaymentListView.as_view(), name="list"),
    path("<str:payment_id>/", PaymentDetailView.as_view(), name="detail"),
    path("<str:payment_id>/logs/", PaymentLogListView.as_view(), name="logs"),

    # Webhook endpoints
    path("webhook/click/prepare/", ClickPrepareView.as_view(), name="click-prepare"),
    path("webhook/click/complete/", ClickCompleteView.as_view(), name="click-complete"),
    path("webhook/payme/", PaymeWebhookView.as_view(), name="payme-webhook"),
]
