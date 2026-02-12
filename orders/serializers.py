from rest_framework import serializers

from orders.models import Cart, CartItem, Order, OrderItem
from orders.services import (
    OrderCreationService,
    OrderStatusService,
    OrderCancelService,
)


# =========================================================
# COMMON
# =========================================================

MONEY_FIELD = serializers.DecimalField(
    max_digits=16,
    decimal_places=2,
    read_only=True
)


# =========================================================
# 🔹 CART
# =========================================================

class CartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(source="product.id", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)
    product_price = serializers.DecimalField(
        source="product.price",
        max_digits=16,
        decimal_places=2,
        read_only=True
    )
    subtotal = serializers.DecimalField(
        max_digits=16,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = CartItem
        fields = (
            "id",
            "product_id",
            "product_name",
            "product_price",
            "quantity",
            "subtotal",
        )


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = MONEY_FIELD
    total_items = serializers.IntegerField(read_only=True)
    is_empty = serializers.BooleanField(read_only=True)

    class Meta:
        model = Cart
        fields = (
            "id",
            "items",
            "total_price",
            "total_items",
            "is_empty",
        )


# =========================================================
# 🔹 ORDER READ
# =========================================================

class OrderItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(source="product.id", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = OrderItem
        fields = (
            "id",
            "product_id",
            "product_name",
            "price",
            "quantity",
            "subtotal",
        )
        read_only_fields = fields


class OrderSerializer(serializers.ModelSerializer):
    """
    Read-only representation
    """

    items = OrderItemSerializer(many=True, read_only=True)
    items_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "status",
            "total_price",
            "delivery_address",
            "needs_prescription",
            "items_count",
            "items",
            "created_at",
        )
        read_only_fields = fields


# =========================================================
# 🔹 CHECKOUT
# =========================================================

class OrderCreateSerializer(serializers.Serializer):
    """
    Business logic faqat service'da
    """

    delivery_address = serializers.CharField(max_length=500)

    def validate_delivery_address(self, value):
        value = value.strip()
        if len(value) < 5:
            raise serializers.ValidationError("Manzil juda qisqa")
        return value

    def create(self, validated_data):
        request = self.context["request"]

        return OrderCreationService.checkout(
            user=request.user,
            delivery_address=validated_data["delivery_address"],
        )


# =========================================================
# 🔹 STATUS CHANGE (FSM safe)
# =========================================================

class OrderStatusChangeSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Order.Status.choices)

    def save(self, **kwargs):
        order = self.context["order"]
        actor = self.context["request"].user

        return OrderStatusService.change_status(
            order=order,
            new_status=self.validated_data["status"],
            actor=actor,
        )


# =========================================================
# 🔹 CANCEL
# =========================================================

class OrderCancelSerializer(serializers.Serializer):

    def save(self, **kwargs):
        order = self.context["order"]
        actor = self.context["request"].user

        return OrderCancelService.cancel(
            order=order,
            actor=actor,
        )
