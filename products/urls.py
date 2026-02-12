from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import CategoryViewSet, ProductViewSet


app_name = "products"   # ⭐ namespace


router = DefaultRouter(trailing_slash=True)

router.register("categories", CategoryViewSet, basename="category")
router.register("products", ProductViewSet, basename="product")


urlpatterns = [
    path("", include(router.urls)),
]
