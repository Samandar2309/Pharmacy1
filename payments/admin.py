from django.contrib import admin
from .models import Payment, PaymentLog


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        "payment_id",
        "order",
        "user",
        "provider",
        "status",
        "amount",
        "created_at",
        "completed_at",
    ]
    list_filter = ["provider", "status", "created_at"]
    search_fields = [
        "payment_id",
        "click_trans_id",
        "payme_transaction_id",
        "user__phone_number",
        "order__id",
    ]
    readonly_fields = [
        "payment_id",
        "created_at",
        "updated_at",
        "completed_at",
        "cancelled_at",
    ]
    ordering = ["-created_at"]

    fieldsets = (
        ("Asosiy ma'lumot", {
            "fields": (
                "payment_id",
                "order",
                "user",
                "provider",
                "status",
                "amount",
            )
        }),
        ("Click ma'lumotlari", {
            "fields": (
                "click_trans_id",
                "click_paydoc_id",
            )
        }),
        ("Payme ma'lumotlari", {
            "fields": (
                "payme_transaction_id",
                "payme_time",
            )
        }),
        ("Qo'shimcha", {
            "fields": (
                "provider_response",
                "error_message",
                "created_at",
                "updated_at",
                "completed_at",
                "cancelled_at",
            )
        }),
    )


@admin.register(PaymentLog)
class PaymentLogAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "payment",
        "event_type",
        "created_at",
    ]
    list_filter = ["event_type", "created_at"]
    search_fields = ["payment__payment_id"]
    readonly_fields = ["created_at"]
    ordering = ["-created_at"]
