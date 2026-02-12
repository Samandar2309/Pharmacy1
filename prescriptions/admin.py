import logging

from django import forms
from django.contrib import admin, messages
from django.contrib.admin.helpers import ActionForm
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Count, Prefetch
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import (
    Prescription,
    PrescriptionImage,
    PrescriptionItem,
)
from .services import (
    approve_prescription,
    reject_prescription,
)

logger = logging.getLogger(__name__)


# ============================================================
# ACTION FORM (ADMIN ACTION INPUT)
# ============================================================

class RejectPrescriptionActionForm(ActionForm):
    """
    Admin action orqali retseptni rad etishda
    sabab kiritish uchun forma.
    """
    reason = forms.CharField(
        label="Rad etish sababi",
        required=False,
        widget=forms.Textarea(attrs={
            "rows": 3,
            "placeholder": "Rad etish sababini kiriting (majburiy)",
        })
    )


# ============================================================
# INLINES
# ============================================================

class PrescriptionImageInline(admin.TabularInline):
    model = PrescriptionImage
    extra = 0
    can_delete = False
    readonly_fields = ("image_preview", "uploaded_at")
    fields = ("image_preview", "uploaded_at")

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<a href="{0}" target="_blank">'
                '<img src="{0}" style="max-height:120px; border-radius:6px;" />'
                '</a>',
                obj.image.url,
            )
        return mark_safe("<span style='color:#999'>Rasm yo‘q</span>")

    image_preview.short_description = "Retsept rasmi"

    def has_add_permission(self, request, obj=None):
        return False


class PrescriptionItemInline(admin.TabularInline):
    model = PrescriptionItem
    extra = 0
    can_delete = False
    readonly_fields = ("product_link", "quantity")
    fields = ("product_link", "quantity")

    def product_link(self, obj):
        if obj.product:
            url = reverse(
                "admin:products_product_change",
                args=[obj.product.pk]
            )
            return format_html(
                '<a href="{}" target="_blank">{}</a>',
                url,
                obj.product.name
            )
        return "-"

    product_link.short_description = "Dori"

    def has_add_permission(self, request, obj=None):
        return False


# ============================================================
# MAIN ADMIN
# ============================================================

@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    """
    ENTERPRISE darajadagi Prescription admin panel.
    HTML templatesiz, toza Django admin.
    """

    action_form = RejectPrescriptionActionForm

    # ----------------------------
    # LIST
    # ----------------------------

    list_display = (
        "id",
        "user_info",
        "status_badge",
        "images_count",
        "items_count",
        "order_link",
        "created_at",
        "reviewed_info",
    )

    list_filter = ("status", "created_at", "reviewed_at")
    search_fields = (
        "id",
        "user__phone_number",
        "user__username",
        "user__first_name",
        "user__last_name",
    )
    ordering = ("-created_at",)
    list_per_page = 25
    date_hierarchy = "created_at"

    # ----------------------------
    # DETAIL
    # ----------------------------

    readonly_fields = (
        "id",
        "user_info",
        "order_link",
        "status_badge",
        "reviewed_by",
        "reviewed_at",
        "rejection_reason_display",
        "created_at",
        "updated_at",
        "images_count",
        "items_count",
    )

    fieldsets = (
        ("Asosiy ma’lumotlar", {
            "fields": ("id", "user_info", "order_link", "created_at"),
        }),
        ("Holat va tekshiruv", {
            "fields": (
                "status_badge",
                "reviewed_by",
                "reviewed_at",
                "rejection_reason_display",
            ),
        }),
        ("Statistika", {
            "fields": ("images_count", "items_count"),
            "classes": ("collapse",),
        }),
    )

    inlines = (PrescriptionImageInline, PrescriptionItemInline)

    actions = (
        "approve_selected_prescriptions",
        "reject_selected_prescriptions",
    )

    # ----------------------------
    # QUERY OPTIMIZATION
    # ----------------------------

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("user", "order", "reviewed_by")
            .prefetch_related(
                Prefetch(
                    "images",
                    queryset=PrescriptionImage.objects.order_by("uploaded_at"),
                ),
                Prefetch(
                    "items",
                    queryset=PrescriptionItem.objects.select_related("product"),
                ),
            )
            .annotate(
                _images_count=Count("images", distinct=True),
                _items_count=Count("items", distinct=True),
            )
        )

    # ----------------------------
    # DISPLAY HELPERS
    # ----------------------------

    def user_info(self, obj):
        user = obj.user
        url = reverse("admin:users_user_change", args=[user.pk])
        return format_html(
            "<a href='{}'><strong>{}</strong></a><br>"
            "<small>{}</small>",
            url,
            user.get_full_name() or user.username,
            getattr(user, "phone_number", "—"),
        )

    user_info.short_description = "Mijoz"

    def status_badge(self, obj):
        colors = {
            Prescription.Status.PENDING: "#ff9800",
            Prescription.Status.APPROVED: "#4caf50",
            Prescription.Status.REJECTED: "#f44336",
        }
        return format_html(
            "<span style='background:{};color:white;"
            "padding:4px 10px;border-radius:12px;'>"
            "{}"
            "</span>",
            colors.get(obj.status, "#999"),
            obj.get_status_display(),
        )

    status_badge.short_description = "Holat"

    def images_count(self, obj):
        return getattr(obj, "_images_count", obj.images.count())

    def items_count(self, obj):
        return getattr(obj, "_items_count", obj.items.count())

    def order_link(self, obj):
        if obj.order:
            url = reverse("admin:orders_order_change", args=[obj.order.pk])
            return format_html(
                "<a href='{}'>Buyurtma #{}</a>",
                url,
                obj.order.pk,
            )
        return "—"

    def reviewed_info(self, obj):
        if obj.reviewed_by:
            return format_html(
                "<strong>{}</strong><br><small>{}</small>",
                obj.reviewed_by.get_full_name()
                or obj.reviewed_by.username,
                obj.reviewed_at.strftime("%d.%m.%Y %H:%M"),
            )
        return "—"

    def rejection_reason_display(self, obj):
        if obj.rejection_reason:
            return format_html(
                "<div style='background:#ffebee;padding:8px;"
                "border-left:4px solid #f44336;'>"
                "{}"
                "</div>",
                obj.rejection_reason,
            )
        return "—"

    # ----------------------------
    # ACTIONS
    # ----------------------------

    def approve_selected_prescriptions(self, request, queryset):
        pending = queryset.filter(status=Prescription.Status.PENDING)

        if not pending.exists():
            self.message_user(
                request,
                "Tasdiqlash uchun PENDING retsept yo‘q.",
                messages.WARNING,
            )
            return

        success = 0
        with transaction.atomic():
            for prescription in pending:
                try:
                    approve_prescription(
                        prescription=prescription,
                        operator=request.user,
                    )
                    success += 1
                except ValidationError as e:
                    self.message_user(
                        request,
                        f"#{prescription.id}: {e}",
                        messages.ERROR,
                    )

        self.message_user(
            request,
            f"{success} ta retsept tasdiqlandi.",
            messages.SUCCESS,
        )

    approve_selected_prescriptions.short_description = "✓ Retseptlarni TASDIQLASH"

    def reject_selected_prescriptions(self, request, queryset):
        reason = request.POST.get("reason")

        if not reason:
            self.message_user(
                request,
                "Rad etish sababi majburiy.",
                messages.ERROR,
            )
            return

        pending = queryset.filter(status=Prescription.Status.PENDING)
        success = 0

        with transaction.atomic():
            for prescription in pending:
                try:
                    reject_prescription(
                        prescription=prescription,
                        operator=request.user,
                        reason=reason,
                    )
                    success += 1
                except ValidationError as e:
                    self.message_user(
                        request,
                        f"#{prescription.id}: {e}",
                        messages.ERROR,
                    )

        self.message_user(
            request,
            f"{success} ta retsept rad etildi.",
            messages.SUCCESS,
        )

    reject_selected_prescriptions.short_description = "✗ Retseptlarni RAD ETISH"

    # ----------------------------
    # PERMISSIONS
    # ----------------------------

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff
