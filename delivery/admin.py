from django.contrib import admin
from django.conf import settings

from delivery.models import Delivery, DeliveryStatusHistory

User = settings.AUTH_USER_MODEL


# =========================================================
# DELIVERY ADMIN
# =========================================================

@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    """
    Yetkazib berishlar (Admin panel).
    """

    list_display = (
        "id",
        "order_display",
        "courier_display",
        "status",
        "is_active",
        "courier_assigned_at",
        "delivered_at",
        "created_at",
    )

    list_filter = (
        "status",
        "is_active",
        "created_at",
    )

    # ❗ FAQAT XAVFSIZ FIELDLAR
    search_fields = (
        "id",
        "order__id",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "courier_assigned_at",
        "delivered_at",
        "canceled_at",
    )

    fieldsets = (
        ("Asosiy ma’lumotlar", {
            "fields": (
                "order",
                "courier",
                "status",
                "is_active",
            )
        }),
        ("Vaqt ma’lumotlari", {
            "fields": (
                "courier_assigned_at",
                "delivered_at",
                "canceled_at",
            )
        }),
        ("Izoh", {
            "fields": ("note",)
        }),
        ("Texnik ma’lumotlar", {
            "fields": (
                "created_at",
                "updated_at",
            )
        }),
    )

    ordering = ("-created_at",)

    # ---------- DISPLAY METHODS ----------

    def order_display(self, obj):
        return f"Buyurtma #{obj.order_id}"
    order_display.short_description = "Buyurtma"

    def courier_display(self, obj):
        if obj.courier:
            return str(obj.courier)
        return "Biriktirilmagan"
    courier_display.short_description = "Kuryer"


# =========================================================
# DELIVERY STATUS HISTORY ADMIN (AUDIT)
# =========================================================

@admin.register(DeliveryStatusHistory)
class DeliveryStatusHistoryAdmin(admin.ModelAdmin):
    """
    Yetkazib berish holatlari tarixi (AUDIT).
    """

    list_display = (
        "id",
        "delivery_display",
        "old_status",
        "new_status",
        "changed_by_display",
        "changed_at",
    )

    list_filter = (
        "old_status",
        "new_status",
        "changed_at",
    )

    # ❗ FAQAT XAVFSIZ FIELD
    search_fields = (
        "id",
        "delivery__id",
    )

    readonly_fields = (
        "delivery",
        "old_status",
        "new_status",
        "changed_by",
        "changed_at",
    )

    ordering = ("-changed_at",)

    # ---------- PERMISSION LOCK ----------

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    # ---------- DISPLAY METHODS ----------

    def delivery_display(self, obj):
        return f"Delivery #{obj.delivery_id}"
    delivery_display.short_description = "Yetkazib berish"

    def changed_by_display(self, obj):
        if obj.changed_by:
            return str(obj.changed_by)
        return "Tizim"
    changed_by_display.short_description = "O‘zgartirgan shaxs"
