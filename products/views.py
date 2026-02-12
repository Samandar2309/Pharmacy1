import logging

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Category, Product
from .serializers import (
    CategoryMiniSerializer,
    ProductListSerializer,
    ProductDetailSerializer,
    ProductWriteSerializer,
)

logger = logging.getLogger(__name__)


# =====================================
# CATEGORY VIEWSET (LIGHTWEIGHT)
# =====================================

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.filter(is_active=True, is_deleted=False)
    serializer_class = CategoryMiniSerializer
    permission_classes = [permissions.AllowAny]


# =====================================
# PRODUCT VIEWSET (PRODUCTION READY)
# =====================================

class ProductViewSet(viewsets.ModelViewSet):
    """
    Professional Product API:
    - search
    - filtering
    - ordering
    - pagination
    - alternatives
    """

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    # ⭐ automatic filters
    filterset_fields = {
        "category": ["exact"],
        "price": ["gte", "lte"],
        "is_prescription_required": ["exact"],
        "is_active": ["exact"],
    }

    search_fields = ["name", "manufacturer"]
    ordering_fields = ["price", "created_at", "order_count"]
    ordering = ["-created_at"]

    # =====================================
    # OPTIMIZED QUERYSET PER ACTION
    # =====================================

    def get_queryset(self):
        base = Product.objects.filter(
            is_deleted=False
        ).select_related("category")

        if self.action == "list":
            # list tez bo‘lishi uchun minimal
            return base.only(
                "id",
                "name",
                "slug",
                "price",
                "image",
                "is_prescription_required",
                "stock",
                "category",
            )

        if self.action == "retrieve":
            return base.prefetch_related("active_substances")

        return base.prefetch_related("active_substances")

    # =====================================
    # SERIALIZERS
    # =====================================

    def get_serializer_class(self):
        if self.action == "list":
            return ProductListSerializer
        if self.action == "retrieve":
            return ProductDetailSerializer
        return ProductWriteSerializer

    # =====================================
    # PERMISSIONS
    # =====================================

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [permissions.IsAdminUser()]  # yoki custom permission
        return [permissions.AllowAny()]

    # =====================================
    # ALTERNATIVE PRODUCTS
    # =====================================

    @action(detail=True, methods=["get"])
    def alternatives(self, request, pk=None):
        product = self.get_object()

        substances = product.active_substances.all()

        alternatives = (
            Product.objects.filter(
                active_substances__in=substances,
                is_active=True,
                stock__gt=0,
                is_deleted=False,
            )
            .exclude(id=product.id)
            .select_related("category")
            .order_by("price")
            .distinct()
        )

        serializer = ProductListSerializer(
            alternatives,
            many=True,
            context={"request": request}
        )
        return Response(serializer.data)
