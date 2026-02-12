from rest_framework import serializers
from products.models import Category, Product, ActiveSubstance


# =====================================
# COMMON SMALL SERIALIZERS (lightweight)
# =====================================

class CategoryMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug"]


class ActiveSubstanceMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActiveSubstance
        fields = ["id", "name"]


# =====================================
# BASE PRODUCT SERIALIZER (DRY pattern)
# =====================================

class ProductBaseSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True)
    is_available = serializers.BooleanField(read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "price",
            "image",
            "is_prescription_required",
            "is_available",
        ]


# =====================================
# PRODUCT LIST (FAST CATALOG)
# =====================================
# Eng yengil, tez ishlashi uchun

class ProductListSerializer(ProductBaseSerializer):
    category = CategoryMiniSerializer(read_only=True)

    class Meta(ProductBaseSerializer.Meta):
        fields = ProductBaseSerializer.Meta.fields + [
            "category",
        ]


# =====================================
# PRODUCT DETAIL (FULL INFO)
# =====================================

class ProductDetailSerializer(ProductBaseSerializer):
    category = CategoryMiniSerializer(read_only=True)
    active_substances = ActiveSubstanceMiniSerializer(many=True, read_only=True)

    class Meta(ProductBaseSerializer.Meta):
        fields = ProductBaseSerializer.Meta.fields + [
            "description",
            "usage",
            "stock",
            "manufacturer",
            "expiry_date",
            "category",
            "active_substances",
        ]


# =====================================
# PRODUCT WRITE (ADMIN/OPERATOR)
# =====================================

class ProductWriteSerializer(serializers.ModelSerializer):
    active_substances = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=ActiveSubstance.objects.all()
    )

    class Meta:
        model = Product
        fields = [
            "name",
            "category",
            "active_substances",
            "description",
            "usage",
            "price",
            "stock",
            "is_prescription_required",
            "manufacturer",
            "image",
            "expiry_date",
            "sku",
            "is_active",
        ]

    # =====================
    # VALIDATIONS (senior)
    # =====================

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Price cannot be negative")
        return value

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("Stock cannot be negative")
        return value
