from rest_framework.permissions import BasePermission
class IsAdminRole(BasePermission):
    """
    Faqat admin roli kira oladi.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and getattr(request.user, "role", None) == "admin"
        )
class IsOperatorRole(BasePermission):
    """Faqat operator roli kira oladi."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and getattr(request.user, "role", None) == "operator"
        )
class IsCourierRole(BasePermission):
    """Faqat courier roli kira oladi."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and getattr(request.user, "role", None) == "courier"
        )
class IsCustomerRole(BasePermission):
    """Faqat customer roli kira oladi."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and getattr(request.user, "role", None) == "customer"
        )
class IsAdminOrOperator(BasePermission):
    """
    Admin yoki operator kira oladi.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role in ["admin", "operator"]
        )
class IsCourierSelf(BasePermission):
    """
    Courier faqat o‘z statistikasi uchun.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == "courier"
        )

    def has_object_permission(self, request, view, obj):
        return obj.courier == request.user
class IsSystemHealthAdmin(BasePermission):
    """
    System monitoring faqat admin ko‘ra oladi.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == "admin"
            and request.user.is_active
        )
class IsStrictAdmin(BasePermission):

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == "admin"
            and request.user.is_staff
            and request.user.is_active
        )