from django.urls import path, include
from rest_framework.routers import DefaultRouter

from orders.views import CartViewSet, OrderViewSet


app_name = "orders"


# =========================================================
# 🔹 ROUTER
# =========================================================

router = DefaultRouter()

# plural → resource collection
router.register(r"orders", OrderViewSet, basename="order")

# singular mantiqan ham to‘g‘ri (userda bitta cart)
router.register(r"cart", CartViewSet, basename="cart")


# =========================================================
# 🔹 URL PATTERNS
# =========================================================

urlpatterns = [
    path("", include(router.urls)),
]
