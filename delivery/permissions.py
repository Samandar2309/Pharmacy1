from rest_framework.permissions import BasePermission, SAFE_METHODS


# =========================================================
# BASE ROLE PERMISSION
# =========================================================

class HasDeliveryRole(BasePermission):
    """
    Delivery app bilan ishlashga ruxsati bor rollar:
    - admin
    - operator
    - courier
    """

    message = "Delivery bo‘limi bilan ishlash uchun ruxsatingiz yo‘q."

    allowed_roles = ("admin", "operator", "courier")

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "role", None) in self.allowed_roles
        )


# =========================================================
# COURIER OBJECT-LEVEL PERMISSION
# =========================================================

class IsCourierOwnDelivery(BasePermission):
    """
    Kuryer faqat O‘ZIGA biriktirilgan delivery bilan ishlay oladi.

    Admin va operator uchun cheklov yo‘q.
    """

    message = "Siz faqat o‘zingizga biriktirilgan yetkazib berish bilan ishlay olasiz."

    def has_object_permission(self, request, view, obj):
        role = getattr(request.user, "role", None)

        # Admin va operator — to‘liq ruxsat
        if role in ("admin", "operator"):
            return True

        # Kuryer — faqat o‘z delivery'si
        if role == "courier":
            return obj.courier_id == request.user.id

        return False


# =========================================================
# READ-ONLY FOR COURIER (OPTIONAL, SAFE)
# =========================================================

class ReadOnlyForCourier(BasePermission):
    """
    Kuryer faqat o‘qish (GET) qilishi mumkin bo‘lgan joylar uchun.
    Admin va operator to‘liq ruxsatga ega.
    """

    message = "Bu amal faqat ko‘rish uchun ruxsat etilgan."

    def has_permission(self, request, view):
        role = getattr(request.user, "role", None)

        if role in ("admin", "operator"):
            return True

        if role == "courier":
            return request.method in SAFE_METHODS

        return False


# =========================================================
# STATUS CHANGE PERMISSION (EXPLICIT)
# =========================================================

class CanCourierUpdateStatus(BasePermission):
    """
    Faqat kuryer delivery statusini o‘zgartira oladi
    (Yo‘lda / Yetkazildi).
    """

    message = "Delivery holatini o‘zgartirish uchun ruxsatingiz yo‘q."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and getattr(request.user, "role", None) == "courier"
        )
