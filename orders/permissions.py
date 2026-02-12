from rest_framework.permissions import BasePermission, SAFE_METHODS


class OrderPermission(BasePermission):
    """
    🔐 Enterprise-grade RBAC Permission

    Design goals:
    - declarative
    - scalable
    - clean
    - no if/else hell
    - easy to extend

    Roles:
    - customer
    - operator
    - courier
    - admin
    """

    message = "Sizda bu amalni bajarish uchun ruxsat yo‘q."

    # =====================================================
    # 🔹 ROLE → ACTION MAP (view-level)
    # =====================================================

    ROLE_ACTIONS = {
        "admin": {"*"},  # full access

        "customer": {
            "list",
            "retrieve",
            "create",
            "cancel",
        },

        "operator": {
            "list",
            "retrieve",
            "change_status",
        },

        "courier": {
            "list",
            "retrieve",
            "change_status",
        },
    }

    # =====================================================
    # 🔹 PERMISSION CHECK (view-level)
    # =====================================================

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        role = getattr(user, "role", None)
        action = getattr(view, "action", None)

        if not role:
            return False

        allowed = self.ROLE_ACTIONS.get(role, set())

        # admin wildcard
        if "*" in allowed:
            return True

        # SAFE methods (GET/HEAD/OPTIONS)
        if request.method in SAFE_METHODS and action in allowed:
            return True

        return action in allowed

    # =====================================================
    # 🔹 OBJECT-LEVEL RULES
    # =====================================================

    def has_object_permission(self, request, view, obj):
        """
        Object-level restriction:
        """

        role = getattr(request.user, "role", None)
        user_id = request.user.id

        # -----------------------
        # ADMIN → all
        # -----------------------
        if role == "admin":
            return True

        # -----------------------
        # CUSTOMER → only own
        # -----------------------
        if role == "customer":
            return obj.user_id == user_id

        # -----------------------
        # OPERATOR → all
        # -----------------------
        if role == "operator":
            return True

        # -----------------------
        # COURIER → only assigned
        # -----------------------
        if role == "courier":
            return obj.courier_id == user_id

        return False
