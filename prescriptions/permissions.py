from rest_framework.permissions import BasePermission, SAFE_METHODS
class IsCustomer(BasePermission):
    """
    Faqat oddiy mijozlar uchun.
    """
    message = "Bu amal faqat mijozlar uchun ruxsat etilgan."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and not request.user.is_staff
            and not getattr(request.user, 'is_courier', False)
        )
class IsOperator(BasePermission):
    """
    Faqat dorixona operatorlari.
    """
    message = "Bu amal faqat operatorlar uchun ruxsat etilgan."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.is_staff
            and not getattr(request.user, 'is_superuser', False)
        )
class IsAdmin(BasePermission):
    """
    Faqat adminlar.
    """
    message = "Bu amal faqat adminlar uchun ruxsat etilgan."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.is_superuser
        )
class IsAdminOrOperator(BasePermission):
    """
    Admin yoki operatorlar.
    """
    message = "Bu amal uchun admin yoki operator bo‘lishingiz kerak."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.is_staff
        )
class IsPrescriptionOwner(BasePermission):
    """
    Mijoz faqat o‘z retseptini ko‘ra oladi.
    """
    message = "Siz faqat o‘zingizga tegishli retseptni ko‘ra olasiz."

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
class PrescriptionObjectPermission(BasePermission):
    """
    Retsept uchun class-level va object-level permission.

    Class-level (list, create):
    - Authenticated users can create and list

    Object-level (retrieve, approve, reject):
    - Admin/Operator can do everything
    - Customer can only view their own prescriptions
    """

    message = "Bu retsept ustida amal bajarishga ruxsatingiz yo'q."

    def has_permission(self, request, view):
        """
        Class-level permission check.
        Barcha authenticated userlar list va create qila oladi.
        """
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """
        Object-level permission check.
        """
        user = request.user

        # Admin — hamma narsani qila oladi
        if user.is_superuser:
            return True

        # Operator — ko'rish + tekshirish
        if user.is_staff:
            return True

        # Mijoz — faqat o'z retsepti va faqat SAFE metodlar
        if obj.user == user and request.method in SAFE_METHODS:
            return True

        return False
