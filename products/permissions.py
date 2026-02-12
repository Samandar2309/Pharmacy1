from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdmin(BasePermission):
    """
    Faqat admin foydalanuvchilar uchun
    """

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_staff
        )


class IsOperator(BasePermission):
    """
    Operator (dorixona xodimi)
    """

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "is_operator", False)
        )


class IsAdminOrReadOnly(BasePermission):
    """
    Admin to‘liq ruxsat,
    boshqalar faqat o‘qish
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_staff
        )


class IsOperatorOrAdmin(BasePermission):
    """
    Operator yoki Admin:
    - POST
    - PUT
    - PATCH
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        if not request.user or not request.user.is_authenticated:
            return False

        return (
            request.user.is_staff
            or getattr(request.user, "is_operator", False)
        )
