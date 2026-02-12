from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Admin - CRUD
    Boshqalar - faqat read
    """

    def has_permission(self, request, view):
        # Read permissions - har kim
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions - faqat admin
        return request.user and request.user.is_authenticated and request.user.is_admin


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Foydalanuvchi faqat o'z bildirishnomalarini ko'ra oladi.
    Admin barcha bildirishnomalarni ko'ra oladi.
    """

    def has_object_permission(self, request, view, obj):
        # Admin - hamma narsani ko'ra oladi
        if request.user.is_admin:
            return True

        # Foydalanuvchi - faqat o'ziniki
        return obj.user == request.user


class CanManageTemplates(permissions.BasePermission):
    """
    Faqat admin shablonlarni boshqara oladi.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_admin
