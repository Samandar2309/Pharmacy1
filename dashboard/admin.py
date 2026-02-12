from django.contrib import admin
from django.utils.html import format_html

from .models import (
    DailyStats,
    ProductPerformance,
    CourierPerformance,
    SystemHealthLog,
)
@admin.register(DailyStats)
class DailyStatsAdmin(admin.ModelAdmin):

    list_display = (
        "date",
        "total_users",
        "total_orders",
        "completed_orders",
        "cancelled_orders",
        "total_revenue",
    )

    list_filter = ("date",)
    ordering = ("-date",)
    search_fields = ("date",)

    readonly_fields = [field.name for field in DailyStats._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
@admin.register(ProductPerformance)
class ProductPerformanceAdmin(admin.ModelAdmin):

    list_display = (
        "product",
        "total_sold",
        "total_revenue",
        "last_sold_at",
    )

    ordering = ("-total_sold",)
    search_fields = ("product__name",)
    readonly_fields = [field.name for field in ProductPerformance._meta.fields]

    autocomplete_fields = ("product",)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
@admin.register(CourierPerformance)
class CourierPerformanceAdmin(admin.ModelAdmin):

    list_display = (
        "courier",
        "total_deliveries",
        "successful_deliveries",
        "average_delivery_time_minutes",
        "total_earnings",
    )

    ordering = ("-total_deliveries",)
    search_fields = ("courier__phone_number",)

    readonly_fields = [field.name for field in CourierPerformance._meta.fields]

    autocomplete_fields = ("courier",)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
@admin.register(SystemHealthLog)
class SystemHealthLogAdmin(admin.ModelAdmin):

    list_display = (
        "level_badge",
        "source",
        "resolved",
        "created_at",
    )

    list_filter = ("level", "resolved")
    search_fields = ("message", "source")
    ordering = ("-created_at",)

    readonly_fields = ("level", "message", "source", "created_at", "updated_at")

    def level_badge(self, obj):
        colors = {
            "info": "blue",
            "warning": "orange",
            "error": "red",
            "critical": "darkred",
        }
        color = colors.get(obj.level, "black")

        return format_html(
            f'<span style="color:{color}; font-weight:bold;">{obj.level.upper()}</span>'
        )

    level_badge.short_description = "Level"
