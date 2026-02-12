from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
import json

from .models import (
    Notification,
    NotificationTemplate,
    NotificationStatus,
)


# =========================================================
# NOTIFICATION ADMIN
# =========================================================

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """
    Enterprise monitoring panel for notifications.
    """

    list_display = (
        "id",
        "user_phone",
        "notification_type",
        "channel",
        "status_badge",
        "retry_info",
        "created_at",
        "sent_at",
    )

    list_filter = (
        "notification_type",
        "channel",
        "status",
        "created_at",
        "sent_at",
    )

    search_fields = (
        "user__phone_number",
        "phone_number",
        "message",
    )

    readonly_fields = (
        "user",
        "phone_number",
        "created_at",
        "updated_at",
        "sent_at",
        "retry_count",
        "last_attempt_at",
        "pretty_metadata",
        "pretty_provider_response",
    )

    ordering = ("-created_at",)
    date_hierarchy = "created_at"

    fieldsets = (
        ("Asosiy ma'lumotlar", {
            "fields": (
                "user",
                "notification_type",
                "channel",
                "phone_number",
                "message",
            )
        }),
        ("Holat", {
            "fields": (
                "status",
                "sent_at",
                "error_message",
                "retry_count",
                "last_attempt_at",
            )
        }),
        ("Metadata", {
            "fields": ("pretty_metadata",),
            "classes": ("collapse",),
        }),
        ("Provider Response", {
            "fields": ("pretty_provider_response",),
            "classes": ("collapse",),
        }),
        ("Vaqt", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    # -------------------------------------------------
    # BADGES
    # -------------------------------------------------

    def status_badge(self, obj):
        colors = {
            NotificationStatus.PENDING: "#ffc107",
            NotificationStatus.PROCESSING: "#17a2b8",
            NotificationStatus.SENT: "#28a745",
            NotificationStatus.FAILED: "#dc3545",
            NotificationStatus.CANCELLED: "#6c757d",
        }

        color = colors.get(obj.status, "#6c757d")

        return format_html(
            '<span style="background:{};color:white;padding:4px 10px;border-radius:4px;">{}</span>',
            color,
            obj.get_status_display(),
        )

    status_badge.short_description = "Holat"

    def retry_info(self, obj):
        return f"{obj.retry_count}/{obj.max_retries}"

    retry_info.short_description = "Retry"

    def user_phone(self, obj):
        return obj.user.phone_number

    user_phone.short_description = "Telefon"

    # -------------------------------------------------
    # JSON PRETTY VIEW
    # -------------------------------------------------

    def pretty_metadata(self, obj):
        if not obj.metadata:
            return "-"
        return mark_safe(
            "<pre style='white-space: pre-wrap;'>"
            + json.dumps(obj.metadata, indent=2, ensure_ascii=False)
            + "</pre>"
        )

    pretty_metadata.short_description = "Metadata"

    def pretty_provider_response(self, obj):
        if not obj.provider_response:
            return "-"
        return mark_safe(
            "<pre style='white-space: pre-wrap;'>"
            + json.dumps(obj.provider_response, indent=2, ensure_ascii=False)
            + "</pre>"
        )

    pretty_provider_response.short_description = "Provider Response"

    # -------------------------------------------------
    # BULK ACTIONS
    # -------------------------------------------------

    actions = ["retry_failed_notifications"]

    def retry_failed_notifications(self, request, queryset):
        from .services import NotificationService

        service = NotificationService()
        count = 0

        for notification in queryset:
            if notification.status == NotificationStatus.FAILED:
                service.send(notification)
                count += 1

        self.message_user(
            request,
            f"{count} ta notification qayta yuborildi."
        )

    retry_failed_notifications.short_description = "Tanlangan FAILED notificationlarni qayta yuborish"

    # -------------------------------------------------
    # PROTECTION
    # -------------------------------------------------

    def has_add_permission(self, request):
        return False  # manual create taqiqlanadi


# =========================================================
# NOTIFICATION TEMPLATE ADMIN
# =========================================================

@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    """
    Notification template management.
    """

    list_display = (
        "id",
        "notification_type",
        "channel",
        "template_text",
        "is_active_badge",
        "created_at",
    )

    list_filter = (
        "notification_type",
        "channel",
        "is_active",
        "created_at",
    )

    search_fields = (
        "notification_type",
        "template_text",
    )

    readonly_fields = ("created_at", "updated_at")

    ordering = ("notification_type",)

    fieldsets = (
        ("Ma'lumot", {
            "fields": (
                "notification_type",
                "channel",
                "template_text",
                "is_active",
            )
        }),
        ("Vaqt", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    def is_active_badge(self, obj):
        color = "#28a745" if obj.is_active else "#6c757d"
        return format_html(
            '<span style="background:{};color:white;padding:4px 10px;border-radius:4px;">{}</span>',
            color,
            "✅ Faol" if obj.is_active else "❌ Nofaol",
        )

    is_active_badge.short_description = "Holat"