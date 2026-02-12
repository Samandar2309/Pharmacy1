from django.contrib import admin
from django.utils.html import format_html

from .models import Category, Product, ActiveSubstance


# =========================================
# CATEGORY ADMIN
# =========================================

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "is_active",
        "product_count",
        "created_at",
    )

    list_filter = ("is_active",)
    search_fields = ("name",)
    ordering = ("name",)

    prepopulated_fields = {"slug": ("name",)}

    list_per_page = 30
    date_hierarchy = "created_at"

    # tezlik
    list_select_related = ()

    def product_count(self, obj):
        return obj.products.count()

    product_count.short_description = "Mahsulotlar soni"


# =========================================
# ACTIVE SUBSTANCE ADMIN
# =========================================

@admin.register(ActiveSubstance)
class ActiveSubstanceAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "product_count",
    )

    search_fields = ("name",)
    ordering = ("name",)
    list_per_page = 30

    def product_count(self, obj):
        return obj.products.count()

    product_count.short_description = "Dori soni"


# =========================================
# PRODUCT ADMIN (ENTERPRISE LEVEL)
# =========================================

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    # =====================
    # TABLE KO‘RINISHI
    # =====================
    list_display = (
        "image_preview",
        "name",
        "category",
        "price",
        "stock_status",
        "manufacturer",
        "is_prescription_required",
        "is_active",
        "created_at",
    )

    list_filter = (
        "is_active",
        "is_prescription_required",
        "category",
        "manufacturer",
    )

    search_fields = (
        "name",
        "manufacturer",
        "sku",
    )

    ordering = ("-created_at",)

    # =====================
    # PERFORMANCE (MUHIM)
    # =====================
    list_select_related = ("category",)
    list_per_page = 25
    date_hierarchy = "created_at"

    autocomplete_fields = ("category",)
    filter_horizontal = ("active_substances",)

    # =====================
    # READONLY
    # =====================
    readonly_fields = (
        "order_count",
        "created_at",
        "updated_at",
        "image_preview",
    )

    # =====================
    # FORM STRUCTURE (UX)
    # =====================
    fieldsets = (
        ("📦 Asosiy ma’lumotlar", {
            "fields": (
                "name",
                "category",
                "active_substances",
                "description",
                "usage",
                "image",
                "image_preview",
            )
        }),

        ("💰 Narx va ombor", {
            "fields": (
                "price",
                "stock",
                "expiry_date",
            )
        }),

        ("⚙ Qo‘shimcha", {
            "fields": (
                "manufacturer",
                "sku",
                "is_prescription_required",
                "is_active",
            )
        }),

        ("📊 Statistika (readonly)", {
            "fields": (
                "order_count",
                "created_at",
                "updated_at",
            )
        }),
    )

    # =====================
    # BULK ACTIONS
    # =====================

    actions = [
        "mark_active",
        "mark_inactive",
        "increase_stock",
    ]

    def mark_active(self, request, queryset):
        queryset.update(is_active=True)
    mark_active.short_description = "Tanlanganlarni faol qilish"

    def mark_inactive(self, request, queryset):
        queryset.update(is_active=False)
    mark_inactive.short_description = "Tanlanganlarni nofaol qilish"

    def increase_stock(self, request, queryset):
        queryset.update(stock=10)
    increase_stock.short_description = "Stockni 10 ga qo‘yish (test)"

    # =====================
    # IMAGE PREVIEW
    # =====================

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="60" style="border-radius:6px;" />',
                obj.image.url
            )
        return "-"
    image_preview.short_description = "Rasm"

    # =====================
    # STOCK STATUS (VIZUAL)
    # =====================

    def stock_status(self, obj):
        if obj.stock == 0:
            return format_html(
                '<span style="color:red;font-weight:bold;">❌ Tugagan</span>'
            )
        elif obj.stock < 10:
            return format_html(
                '<span style="color:orange;font-weight:bold;">⚠ Kam ({})</span>',
                obj.stock
            )
        return format_html(
            '<span style="color:green;">✅ Yetarli</span>'
        )

    stock_status.short_description = "Ombor holati"
