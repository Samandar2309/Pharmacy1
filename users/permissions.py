from rest_framework.permissions import BasePermission, SAFE_METHODS


class HasRole(BasePermission):
    """
    Foydalanuvchi ma'lum role'lardan biriga ega bo‘lishi kerak
    """

    allowed_roles = []

    def has_permission(self, request, view):
        return (
                request.user.is_authenticated and
                request.user.role in self.allowed_roles
        )


class IsAdmin(HasRole):
    allowed_roles = ['admin']


class IsOperator(HasRole):
    allowed_roles = ['operator']


class IsCourier(HasRole):
    allowed_roles = ['courier']


class IsCustomer(HasRole):
    allowed_roles = ['customer']


class IsAdminOrOperator(HasRole):
    allowed_roles = ['admin', 'operator']


class IsAdminOrCourier(HasRole):
    allowed_roles = ['admin', 'courier']


class IsOwner(BasePermission):
    """
    Faqat obyekt egasi ruxsat oladi
    Masalan: buyurtma, profil
    """

    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and obj.user == request.user


class ReadOnly(BasePermission):
    """
    Faqat o‘qish mumkin (GET, HEAD, OPTIONS)
    """

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS
