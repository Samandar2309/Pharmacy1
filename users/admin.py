from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html

from .models import User, SMSVerification


# =====================================================
# 🔥 HELPERS (visual UX)
# =====================================================

def colored_bool(value: bool):
    color = "green" if value else "red"
    label = "✔" if value else "✖"
    return format_html(f'<b style="color:{color}">{label}</b>')


# =====================================================
# USER ADMIN (ENTERPRISE LEVEL)
# =====================================================

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Production grade admin:
    ✔ rangli role
    ✔ tez filter
    ✔ bulk actions
    ✔ readonly audit
    ✔ performance optimizatsiya
    """

    # =============================
    # PERFORMANCE
    # =============================
    list_select_related = True
    list_per_page = 30

    # =============================
    # LIST VIEW
    # =============================
    list_display = (
        "phone_number",
        "full_name",
        "role_badge",
        "verified_badge",
        "is_active",
        "is_staff",
        "created_at",
    )

    list_editable = (
        "is_active",
    )

    list_filter = (
        "role",
        "is_verified",
        "is_active",
        "is_staff",
        "created_at",
    )

    search_fields = (
        "phone_number",
        "first_name",
        "last_name",
    )

    ordering = ("-created_at",)

    # =============================
    # FIELDSETS
    # =============================
    fieldsets = (
        ("Asosiy", {
            "fields": (
                "phone_number",
                "password",
            )
        }),
        ("Profil", {
            "fields": (
                "first_name",
                "last_name",
                "address",
            )
        }),
        ("Rollar & Ruxsatlar", {
            "fields": (
                "role",
                "is_verified",
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            )
        }),
        ("Audit", {
            "fields": (
                "last_login",
                "date_joined",
                "created_at",
                "updated_at",
            )
        }),
    )

    readonly_fields = (
        "last_login",
        "date_joined",
        "created_at",
        "updated_at",
    )

    # username yashirin
    exclude = ("username",)

    # =============================
    # ADD FORM
    # =============================
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "phone_number",
                "password1",
                "password2",
                "role",
                "is_verified",
                "is_staff",
                "is_active",
            ),
        }),
    )

    filter_horizontal = (
        "groups",
        "user_permissions",
    )

    # =================================================
    # 🔥 VISUAL COLUMNS
    # =================================================

    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or "-"
    full_name.short_description = "Ism"

    def role_badge(self, obj):
        colors = {
            "admin": "#d9534f",
            "operator": "#0275d8",
            "courier": "#5bc0de",
            "customer": "#5cb85c",
        }
        color = colors.get(obj.role, "#777")

        return format_html(
            f'<span style="color:white;background:{color};padding:4px 8px;border-radius:6px">{obj.role.upper()}</span>'
        )
    role_badge.short_description = "Role"

    def verified_badge(self, obj):
        return colored_bool(obj.is_verified)
    verified_badge.short_description = "Verified"

    # =================================================
    # 🔥 BULK ACTIONS
    # =================================================

    actions = ["make_verified", "make_unverified"]

    def make_verified(self, request, queryset):
        queryset.update(is_verified=True)
    make_verified.short_description = "Tanlanganlarni verified qilish"

    def make_unverified(self, request, queryset):
        queryset.update(is_verified=False)
    make_unverified.short_description = "Tanlanganlarni unverified qilish"


# =====================================================
# SMS VERIFICATION ADMIN (IMPROVED)
# =====================================================

@admin.register(SMSVerification)
class SMSVerificationAdmin(admin.ModelAdmin):
    """
    OTP monitoring panel
    """

    list_display = (
        "phone_number",
        "code",
        "status_badge",
        "created_at",
    )

    list_filter = (
        "is_used",
        "created_at",
    )

    search_fields = (
        "phone_number",
        "code",
    )

    ordering = ("-created_at",)

    readonly_fields = (
        "phone_number",
        "code",
        "created_at",
    )

    list_per_page = 50

    # 🔥 rangli status
    def status_badge(self, obj):
        if obj.is_used:
            return format_html('<span style="color:green;font-weight:bold">USED</span>')
        if obj.is_expired:
            return format_html('<span style="color:red;font-weight:bold">EXPIRED</span>')
        return format_html('<span style="color:orange;font-weight:bold">ACTIVE</span>')

    status_badge.short_description = "Status"
