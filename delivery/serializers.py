from rest_framework import serializers

from delivery.models import Delivery, DeliveryStatusHistory
from orders.models import Order
from users.models import User


# =========================================================
# BASIC / NESTED SERIALIZERS
# =========================================================

class CourierShortSerializer(serializers.ModelSerializer):
    """
    Kuryer haqida qisqa ma’lumot (TZ: kuryer paneli)
    """

    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "phone_number",
        )


class OrderShortSerializer(serializers.ModelSerializer):
    """
    Buyurtma haqida minimal ma’lumot
    (delivery kontekstida yetarli)
    """

    class Meta:
        model = Order
        fields = (
            "id",
            "status",
            "total_price",
            "created_at",
        )


# =========================================================
# DELIVERY SERIALIZERS
# =========================================================

class DeliveryListSerializer(serializers.ModelSerializer):
    """
    Kuryer / admin / operator ro‘yxat sahifasi uchun.

    TZ:
    - kuryer o‘ziga biriktirilgan buyurtmalarni ko‘radi
    """

    order = OrderShortSerializer(read_only=True)
    courier = CourierShortSerializer(read_only=True)

    class Meta:
        model = Delivery
        fields = (
            "id",
            "order",
            "courier",
            "status",
            "created_at",
            "courier_assigned_at",
            "delivered_at",
        )


class DeliveryDetailSerializer(serializers.ModelSerializer):
    """
    Delivery tafsilot sahifasi (detail view).

    TZ:
    - kuryer buyurtma holatini ko‘radi
    - admin monitoring qiladi
    """

    order = OrderShortSerializer(read_only=True)
    courier = CourierShortSerializer(read_only=True)

    class Meta:
        model = Delivery
        fields = (
            "id",
            "order",
            "courier",
            "status",
            "note",
            "created_at",
            "courier_assigned_at",
            "delivered_at",
            "canceled_at",
        )


# =========================================================
# ACTION SERIALIZERS (WRITE)
# =========================================================

class AssignCourierSerializer(serializers.Serializer):
    """
    Operator → kuryer biriktirish.

    TZ:
    - operator buyurtmani kuryerga beradi
    """

    courier_id = serializers.IntegerField()

    def validate_courier_id(self, value):
        try:
            courier = User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Kuryer topilmadi.")

        if getattr(courier, "role", None) != "courier":
            raise serializers.ValidationError("Tanlangan foydalanuvchi kuryer emas.")

        return value


class DeliveryStatusUpdateSerializer(serializers.Serializer):
    """
    Kuryer tomonidan holatni yangilash.

    TZ:
    - Yo‘lda
    - Yetkazildi
    """

    status = serializers.ChoiceField(
        choices=[
            Delivery.Status.ON_THE_WAY,
            Delivery.Status.DELIVERED,
        ]
    )


class CancelDeliverySerializer(serializers.Serializer):
    """
    Admin / operator tomonidan bekor qilish.

    TZ:
    - Bekor qilindi holati mavjud
    """

    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=255
    )


# =========================================================
# DELIVERY STATUS HISTORY
# =========================================================

class DeliveryStatusHistorySerializer(serializers.ModelSerializer):
    """
    Buyurtma holatlari tarixi (TZ 6.8)
    """

    changed_by = CourierShortSerializer(read_only=True)

    class Meta:
        model = DeliveryStatusHistory
        fields = (
            "id",
            "old_status",
            "new_status",
            "changed_by",
            "changed_at",
        )
