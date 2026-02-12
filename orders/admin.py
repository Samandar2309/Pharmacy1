from decimal import Decimal

from django.contrib import admin
from django.db.models import Sum
from django.utils.html import format_html

from orders.models import (
    Cart,
    CartItem,
    Order,
    OrderItem,
    Prescription,
    OrderStatusHistory,
)

from orders.services import (
    OrderStatusService,
    OrderCancelService,
)


# =========================================================
# 🔹 BADGE HELPER
# =========================================================

def badge(text, color):
    return format_html(
        '<span style="padding:3px 8px;border-radius:6px;'
        'color:white;background:{};font-size:12px;">{}</span>',
        color,
        text,
    )


# =========================================================
# 🔹 CART ADMIN
# =========================================================

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    can_delete = False
    readonly_fields = ("product", "quantity", "subtotal", "created_at")

    def subtotal(self, obj):
        return obj.subtotal


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "items_count",
        "total_price_display",
        "updated_at",
    )

    list_select_related = ("user",)
    search_fields = ("user__phone", "user__first_name", "user__last_name")
    ordering = ("-updated_at",)

    readonly_fields = (
        "user",
        "created_at",
        "updated_at",
        "items_count",
        "total_price_display",
    )

    inlines = [CartItemInline]

    # 🔥 auto user
    def save_model(self, request, obj, form, change):
        if not change and not obj.user_id:
            obj.user = request.user
        super().save_model(request, obj, form, change)

    def items_count(self, obj):
        return obj.items.aggregate(total=Sum("quantity"))["total"] or 0

    def total_price_display(self, obj):
        return obj.total_price


# =========================================================
# 🔹 ORDER ITEM INLINE (🔥 PRODUCT TANLASH ISHLAYDI)
# =========================================================

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

    # 🔥 MUHIM: product tanlash uchun
    autocomplete_fields = ("product",)

    # price freeze + subtotal readonly
    readonly_fields = ("price", "subtotal")

    fields = ("product", "price", "quantity", "subtotal")

    def subtotal(self, obj):
        return obj.subtotal


# =========================================================
# 🔹 PRESCRIPTION INLINE
# =========================================================

class PrescriptionInline(admin.StackedInline):
    model = Prescription
    extra = 0
    readonly_fields = ("image_preview", "status", "reviewed_by", "reviewed_at")

    def image_preview(self, obj):
        if obj and obj.image:
            return format_html(
                '<img src="{}" style="max-height:250px;border-radius:6px;" />',
                obj.image.url,
            )
        return "-"


# =========================================================
# 🔹 ORDER HISTORY INLINE
# =========================================================

class OrderHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0
    can_delete = False
    readonly_fields = ("from_status", "to_status", "changed_by", "created_at")


# =========================================================
# 🔹 ORDER ADMIN (ENTERPRISE / PRODUCTION SAFE)
# =========================================================

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    # -----------------------------
    # LIST
    # -----------------------------

    list_display = (
        "id",
        "user",
        "status_badge",
        "total_price",
        "needs_prescription",
        "courier",
        "created_at",
    )

    list_filter = (
        "status",
        "needs_prescription",
        "created_at",
    )

    search_fields = (
        "id",
        "user__phone",
        "user__first_name",
        "user__last_name",
    )

    ordering = ("-created_at",)
    list_select_related = ("user", "courier")

    inlines = [
        OrderItemInline,
        PrescriptionInline,
        OrderHistoryInline,
    ]

    readonly_fields = (
        "user",
        "total_price",
        "needs_prescription",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        ("Order", {
            "fields": (
                "user",
                "status",
                "total_price",
                "needs_prescription",
            )
        }),
        ("Delivery", {
            "fields": ("delivery_address", "courier")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at")
        }),
    )

    # -----------------------------
    # 🔥 AUTO FILL REQUIRED FIELDS
    # -----------------------------

    def save_model(self, request, obj, form, change):
        if not change:
            obj.user = request.user

            if obj.total_price is None:
                obj.total_price = Decimal("0.00")

        super().save_model(request, obj, form, change)

    # -----------------------------
    # 🔥 PAID / DELIVERED LOCK
    # -----------------------------

    def has_change_permission(self, request, obj=None):
        if obj and obj.status in (
            Order.Status.PAID,
            Order.Status.DELIVERED,
        ):
            return False
        return super().has_change_permission(request, obj)

    # -----------------------------
    # STATUS BADGE
    # -----------------------------

    def status_badge(self, obj):
        COLORS = {
            Order.Status.AWAITING_PAYMENT: "#0d6efd",
            Order.Status.AWAITING_PRESCRIPTION: "#ffc107",
            Order.Status.PAID: "#198754",
            Order.Status.PREPARING: "#0dcaf0",
            Order.Status.READY_FOR_DELIVERY: "#6610f2",
            Order.Status.ON_THE_WAY: "#6f42c1",
            Order.Status.DELIVERED: "#20c997",
            Order.Status.CANCELLED: "#dc3545",
        }
        return badge(obj.get_status_display(), COLORS.get(obj.status, "#6c757d"))

    status_badge.short_description = "Status"

    # -----------------------------
    # SAFE ACTIONS (SERVICE BASED)
    # -----------------------------

    actions = (
        "mark_preparing",
        "mark_ready",
        "mark_delivered",
        "cancel_orders",
    )

    def mark_preparing(self, request, queryset):
        for order in queryset:
            OrderStatusService.change_status(
                order, Order.Status.PREPARING, request.user
            )

    def mark_ready(self, request, queryset):
        for order in queryset:
            OrderStatusService.change_status(
                order, Order.Status.READY_FOR_DELIVERY, request.user
            )

    def mark_delivered(self, request, queryset):
        for order in queryset:
            OrderStatusService.change_status(
                order, Order.Status.DELIVERED, request.user
            )

    def cancel_orders(self, request, queryset):
        for order in queryset:
            OrderCancelService.cancel(order, request.user)
