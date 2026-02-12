from datetime import date as date_class
from datetime import timedelta

from django.db import transaction
from django.db.models import Sum, Count, F, Avg, ExpressionWrapper, DurationField
from django.utils import timezone
from django.core.cache import cache

from users.models import User
from orders.models import Order, OrderItem, OrderStatusHistory
from prescriptions.models import Prescription
from delivery.models import Delivery
from products.models import Product
from payments.models import Payment

from .models import (
    DailyStats,
    ProductPerformance,
    CourierPerformance,
    SystemHealthLog,
)


def _date_range(days: int):
    today = timezone.now().date()
    start = today - timedelta(days=days - 1)
    return start, today


@transaction.atomic
def recalculate_daily_stats(target_date=None):
    """
    Berilgan sana uchun barcha statistikani qayta hisoblaydi.
    Idempotent. Har safar to‘liq overwrite qiladi.
    """

    if not target_date:
        target_date = timezone.now().date()

    stats, _ = DailyStats.objects.get_or_create(date=target_date)

    # Users
    stats.total_users = User.objects.count()
    stats.total_operators = User.objects.filter(role="operator").count()
    stats.total_couriers = User.objects.filter(role="courier").count()

    # Orders (created at date)
    daily_orders = Order.objects.filter(created_at__date=target_date)

    stats.total_orders = daily_orders.count()
    stats.completed_orders = daily_orders.filter(status=Order.Status.DELIVERED).count()
    stats.cancelled_orders = daily_orders.filter(status=Order.Status.CANCELLED).count()

    stats.total_revenue = (
        Payment.objects.filter(
            status=Payment.Status.SUCCESS,
            order__created_at__date=target_date,
        ).aggregate(total=Sum("amount"))["total"]
        or 0
    )

    # Prescriptions
    daily_prescriptions = Prescription.objects.filter(created_at__date=target_date)

    stats.prescriptions_pending = daily_prescriptions.filter(
        status=Prescription.Status.PENDING
    ).count()
    stats.prescriptions_approved = daily_prescriptions.filter(
        status=Prescription.Status.APPROVED
    ).count()
    stats.prescriptions_rejected = daily_prescriptions.filter(
        status=Prescription.Status.REJECTED
    ).count()

    stats.save()

    return stats


@transaction.atomic
def increment_order_created_metrics(order: Order):
    """Order yaratilganda chaqiriladi."""

    today = order.created_at.date()
    stats, _ = DailyStats.objects.get_or_create(date=today)

    stats.total_orders = F("total_orders") + 1
    stats.save(update_fields=["total_orders"])


@transaction.atomic
def increment_order_status_metrics(order: Order, *, old_status: str = None):
    """Order status o‘zgarganda delivered/cancelled metriclarini yangilaydi."""

    target_date = order.created_at.date()
    stats, _ = DailyStats.objects.get_or_create(date=target_date)

    if order.status == Order.Status.DELIVERED and old_status != Order.Status.DELIVERED:
        stats.completed_orders = F("completed_orders") + 1

    if order.status == Order.Status.CANCELLED and old_status != Order.Status.CANCELLED:
        stats.cancelled_orders = F("cancelled_orders") + 1

    stats.save(update_fields=["completed_orders", "cancelled_orders"])


@transaction.atomic
def increment_revenue_metrics(payment: Payment, *, old_status: str = None):
    """Payment success bo'lganda revenue yangilaydi."""

    if payment.status != Payment.Status.SUCCESS:
        return

    if old_status == Payment.Status.SUCCESS:
        return

    target_date = payment.order.created_at.date()
    stats, _ = DailyStats.objects.get_or_create(date=target_date)

    stats.total_revenue = F("total_revenue") + payment.amount
    stats.save(update_fields=["total_revenue"])


@transaction.atomic
def increment_product_performance(order: Order):
    """
    Order ichidagi mahsulotlar statistikasi update qilinadi.
    Faqat delivered bo‘lganda chaqiriladi.
    """

    items = OrderItem.objects.filter(order=order)

    for item in items:
        performance, _ = ProductPerformance.objects.get_or_create(
            product=item.product
        )

        performance.total_sold = F("total_sold") + item.quantity
        performance.total_revenue = F("total_revenue") + (
            item.price * item.quantity
        )
        performance.last_sold_at = timezone.now()

        performance.save()


@transaction.atomic
def increment_courier_performance(delivery: Delivery):
    """
    Delivery yakunlanganda chaqiriladi.
    """

    if delivery.status != Delivery.Status.DELIVERED:
        return

    courier = delivery.courier
    if not courier:
        return

    performance, _ = CourierPerformance.objects.get_or_create(courier=courier)

    performance.total_deliveries = F("total_deliveries") + 1
    performance.successful_deliveries = F("successful_deliveries") + 1

    performance.save()


def log_system_event(level: str, message: str, source: str):
    """
    Universal monitoring log.
    """

    SystemHealthLog.objects.create(
        level=level,
        message=message,
        source=source,
    )


def _admin_global_stats():
    total_users = User.objects.count()
    total_customers = User.objects.filter(role="customer").count()
    total_operators = User.objects.filter(role="operator").count()
    total_couriers = User.objects.filter(role="courier").count()
    active_users = User.objects.filter(is_active=True).count()
    blocked_users = User.objects.filter(is_active=False).count()

    return {
        "total_users": total_users,
        "total_customers": total_customers,
        "total_operators": total_operators,
        "total_couriers": total_couriers,
        "active_users": active_users,
        "blocked_users": blocked_users,
    }


def _admin_order_stats():
    today = timezone.now().date()
    week_start, week_end = _date_range(7)
    month_start = today.replace(day=1)

    status_counts = {
        status: Order.objects.filter(status=status).count()
        for status, _ in Order.Status.choices
    }

    return {
        "total_orders": Order.objects.count(),
        "by_status": status_counts,
        "today_orders": Order.objects.filter(created_at__date=today).count(),
        "weekly_orders": Order.objects.filter(created_at__date__range=(week_start, week_end)).count(),
        "monthly_orders": Order.objects.filter(created_at__date__gte=month_start).count(),
    }


def _admin_revenue_stats():
    today = timezone.now().date()
    month_start = today.replace(day=1)

    base_qs = Payment.objects.all()

    total_revenue = base_qs.filter(status=Payment.Status.SUCCESS).aggregate(
        total=Sum("amount")
    )["total"] or 0

    today_revenue = base_qs.filter(
        status=Payment.Status.SUCCESS,
        order__created_at__date=today,
    ).aggregate(total=Sum("amount"))["total"] or 0

    monthly_revenue = base_qs.filter(
        status=Payment.Status.SUCCESS,
        order__created_at__date__gte=month_start,
    ).aggregate(total=Sum("amount"))["total"] or 0

    successful_count = base_qs.filter(status=Payment.Status.SUCCESS).count()
    failed_count = base_qs.filter(status=Payment.Status.FAILED).count()

    return {
        "total_revenue": total_revenue,
        "today_revenue": today_revenue,
        "monthly_revenue": monthly_revenue,
        "successful_payments": successful_count,
        "failed_payments": failed_count,
    }


def _admin_product_stats():
    top_products = (
        ProductPerformance.objects.select_related("product")
        .order_by("-total_sold")
        .values("product_id", "product__name", "total_sold")
        [:10]
    )

    out_of_stock = Product.objects.filter(stock=0).count()
    prescription_required = Product.objects.filter(is_prescription_required=True).count()
    low_stock = Product.objects.filter(stock__gt=0, stock__lte=5).count()

    return {
        "top_products": list(top_products),
        "out_of_stock": out_of_stock,
        "prescription_required": prescription_required,
        "low_stock": low_stock,
    }


def _admin_prescription_stats():
    today = timezone.now().date()

    return {
        "pending": Prescription.objects.filter(status=Prescription.Status.PENDING).count(),
        "approved": Prescription.objects.filter(status=Prescription.Status.APPROVED).count(),
        "rejected": Prescription.objects.filter(status=Prescription.Status.REJECTED).count(),
        "today": Prescription.objects.filter(created_at__date=today).count(),
    }


def _admin_courier_stats():
    delivered_qs = Delivery.objects.filter(status=Delivery.Status.DELIVERED)

    per_courier = (
        delivered_qs.values("courier_id")
        .annotate(total=Count("id"))
        .order_by("-total")
    )

    average_time = delivered_qs.exclude(
        delivered_at__isnull=True,
        courier_assigned_at__isnull=True,
    ).annotate(
        duration=ExpressionWrapper(
            F("delivered_at") - F("courier_assigned_at"),
            output_field=DurationField(),
        )
    ).aggregate(avg=Avg("duration"))["avg"]

    undelivered = Delivery.objects.exclude(status=Delivery.Status.DELIVERED).count()

    return {
        "per_courier": list(per_courier),
        "best_courier": per_courier[0] if per_courier else None,
        "average_delivery_time": average_time,
        "undelivered": undelivered,
    }


def _admin_system_health():
    error_count = SystemHealthLog.objects.filter(level__in=["error", "critical"]).count()
    last_errors = list(
        SystemHealthLog.objects.filter(level__in=["error", "critical"]).values(
            "id", "level", "message", "source", "created_at"
        )[:10]
    )

    return {
        "error_count": error_count,
        "last_errors": last_errors,
    }


def get_admin_dashboard_overview():
    cache_key = "dashboard:admin:overview"
    return cache.get_or_set(
        cache_key,
        {
            "global_stats": _admin_global_stats(),
            "order_stats": _admin_order_stats(),
            "revenue_stats": _admin_revenue_stats(),
            "product_stats": _admin_product_stats(),
            "prescription_stats": _admin_prescription_stats(),
            "courier_stats": _admin_courier_stats(),
            "system_health": _admin_system_health(),
        },
        timeout=60,
    )


def get_operator_dashboard_overview(*, operator: User):
    today = timezone.now().date()

    order_queue = {
        "created": Order.objects.filter(status=Order.Status.DRAFT).count(),
        "awaiting_prescription": Order.objects.filter(status=Order.Status.AWAITING_PRESCRIPTION).count(),
        "awaiting_payment": Order.objects.filter(status=Order.Status.AWAITING_PAYMENT).count(),
        "paid": Order.objects.filter(status=Order.Status.PAID).count(),
        "preparing": Order.objects.filter(status=Order.Status.PREPARING).count(),
    }

    prescription_queue = {
        "pending": Prescription.objects.filter(status=Prescription.Status.PENDING).count(),
        "today": Prescription.objects.filter(created_at__date=today).count(),
    }

    operator_kpi = {
        "prepared_today": OrderStatusHistory.objects.filter(
            changed_by=operator,
            to_status=Order.Status.PREPARING,
            created_at__date=today,
        ).count(),
        "reviewed_prescriptions_today": Prescription.objects.filter(
            reviewed_by=operator,
            reviewed_at__date=today,
        ).count(),
    }

    return {
        "order_queue": order_queue,
        "prescription_queue": prescription_queue,
        "operator_kpi": operator_kpi,
    }


def get_courier_dashboard_overview(*, courier: User):
    today = timezone.now().date()

    assigned_orders = {
        "ready": Delivery.objects.filter(courier=courier, status=Delivery.Status.READY).count(),
        "on_the_way": Delivery.objects.filter(courier=courier, status=Delivery.Status.ON_THE_WAY).count(),
        "delivered": Delivery.objects.filter(courier=courier, status=Delivery.Status.DELIVERED).count(),
    }

    average_time = Delivery.objects.filter(
        courier=courier,
        status=Delivery.Status.DELIVERED,
    ).exclude(
        delivered_at__isnull=True,
        courier_assigned_at__isnull=True,
    ).annotate(
        duration=ExpressionWrapper(
            F("delivered_at") - F("courier_assigned_at"),
            output_field=DurationField(),
        )
    ).aggregate(avg=Avg("duration"))["avg"]

    courier_kpi = {
        "delivered_today": Delivery.objects.filter(
            courier=courier,
            status=Delivery.Status.DELIVERED,
            delivered_at__date=today,
        ).count(),
        "total_delivered": Delivery.objects.filter(
            courier=courier,
            status=Delivery.Status.DELIVERED,
        ).count(),
        "average_delivery_time": average_time,
    }

    return {
        "assigned_orders": assigned_orders,
        "courier_kpi": courier_kpi,
    }


def get_customer_dashboard_overview(*, customer: User):
    order_summary = {
        "new": Order.objects.filter(user=customer, status=Order.Status.DRAFT).count(),
        "on_the_way": Order.objects.filter(user=customer, status=Order.Status.ON_THE_WAY).count(),
        "delivered": Order.objects.filter(user=customer, status=Order.Status.DELIVERED).count(),
        "cancelled": Order.objects.filter(user=customer, status=Order.Status.CANCELLED).count(),
    }

    prescription_summary = {
        "pending": Prescription.objects.filter(user=customer, status=Prescription.Status.PENDING).count(),
        "approved": Prescription.objects.filter(user=customer, status=Prescription.Status.APPROVED).count(),
        "rejected": Prescription.objects.filter(user=customer, status=Prescription.Status.REJECTED).count(),
    }

    total_spent = Payment.objects.filter(
        order__user=customer,
        status=Payment.Status.SUCCESS,
    ).aggregate(total=Sum("amount"))["total"] or 0

    top_product = (
        OrderItem.objects.filter(order__user=customer)
        .values("product_id", "product__name")
        .annotate(total_qty=Sum("quantity"))
        .order_by("-total_qty")
        .first()
    )

    purchase_stats = {
        "total_spent": total_spent,
        "top_product": top_product,
    }

    return {
        "order_summary": order_summary,
        "prescription_summary": prescription_summary,
        "purchase_stats": purchase_stats,
    }