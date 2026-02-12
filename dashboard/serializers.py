from rest_framework import serializers

from .models import (
    DailyStats,
    ProductPerformance,
    CourierPerformance,
    SystemHealthLog,
)


class DailyStatsSerializer(serializers.ModelSerializer):

    class Meta:
        model = DailyStats
        fields = [
            "date",
            "total_users",
            "total_operators",
            "total_couriers",
            "total_orders",
            "completed_orders",
            "cancelled_orders",
            "total_revenue",
            "prescriptions_pending",
            "prescriptions_approved",
            "prescriptions_rejected",
        ]
        read_only_fields = fields


class ProductPerformanceSerializer(serializers.ModelSerializer):

    product_name = serializers.CharField(source="product.name", read_only=True)
    product_id = serializers.IntegerField(source="product.id", read_only=True)

    class Meta:
        model = ProductPerformance
        fields = [
            "product_id",
            "product_name",
            "total_sold",
            "total_revenue",
            "last_sold_at",
        ]
        read_only_fields = fields


class CourierPerformanceSerializer(serializers.ModelSerializer):

    courier_id = serializers.IntegerField(source="courier.id", read_only=True)
    courier_phone = serializers.CharField(source="courier.phone_number", read_only=True)

    class Meta:
        model = CourierPerformance
        fields = [
            "courier_id",
            "courier_phone",
            "total_deliveries",
            "successful_deliveries",
            "average_delivery_time_minutes",
            "total_earnings",
        ]
        read_only_fields = fields


class SystemHealthLogSerializer(serializers.ModelSerializer):

    class Meta:
        model = SystemHealthLog
        fields = [
            "id",
            "level",
            "message",
            "source",
            "resolved",
            "created_at",
        ]
        read_only_fields = fields


class AdminDashboardSerializer(serializers.Serializer):

    global_stats = serializers.DictField()
    order_stats = serializers.DictField()
    revenue_stats = serializers.DictField()
    product_stats = serializers.DictField()
    prescription_stats = serializers.DictField()
    courier_stats = serializers.DictField()
    system_health = serializers.DictField()


class OperatorDashboardSerializer(serializers.Serializer):

    order_queue = serializers.DictField()
    prescription_queue = serializers.DictField()
    operator_kpi = serializers.DictField()


class CourierDashboardSerializer(serializers.Serializer):

    assigned_orders = serializers.DictField()
    courier_kpi = serializers.DictField()


class CustomerDashboardSerializer(serializers.Serializer):

    order_summary = serializers.DictField()
    prescription_summary = serializers.DictField()
    purchase_stats = serializers.DictField()