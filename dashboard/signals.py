from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.db import transaction

from orders.models import Order
from delivery.models import Delivery
from prescriptions.models import Prescription
from payments.models import Payment

from .services import (
    increment_order_created_metrics,
    increment_order_status_metrics,
    increment_product_performance,
    increment_courier_performance,
    increment_revenue_metrics,
    log_system_event,
)


# =========================================================
# ORDER STATUS TRACKING
# =========================================================

@receiver(pre_save, sender=Order)
def capture_old_order_state(sender, instance, **kwargs):
    """
    Eski status qiymatini vaqtincha instance ichiga saqlaymiz.
    """
    if not instance.pk:
        instance._old_status = None
        return

    try:
        old = Order.objects.get(pk=instance.pk)
        instance._old_status = old.status
    except Order.DoesNotExist:
        instance._old_status = None


@receiver(post_save, sender=Order)
def handle_order_updates(sender, instance, created, **kwargs):
    try:
        with transaction.atomic():

            # 🔹 Yangi order
            if created:
                increment_order_created_metrics(instance)
                return

            increment_order_status_metrics(instance, old_status=getattr(instance, "_old_status", None))

            # 🔹 Delivered bo‘ldimi?
            if (
                instance.status == Order.Status.DELIVERED
                and getattr(instance, "_old_status", None) != Order.Status.DELIVERED
            ):
                increment_product_performance(instance)

    except Exception as e:
        log_system_event(
            level="error",
            message=str(e),
            source="dashboard.order_signal",
        )


@receiver(pre_save, sender=Payment)
def capture_old_payment_status(sender, instance, **kwargs):
    if not instance.pk:
        instance._old_status = None
        return

    try:
        old = Payment.objects.get(pk=instance.pk)
        instance._old_status = old.status
    except Payment.DoesNotExist:
        instance._old_status = None


@receiver(post_save, sender=Payment)
def handle_payment_updates(sender, instance, created, **kwargs):
    try:
        with transaction.atomic():
            increment_revenue_metrics(instance, old_status=getattr(instance, "_old_status", None))
    except Exception as e:
        log_system_event(
            level="error",
            message=str(e),
            source="dashboard.payment_signal",
        )


@receiver(pre_save, sender=Delivery)
def capture_old_delivery_status(sender, instance, **kwargs):
    if not instance.pk:
        instance._old_status = None
        return

    try:
        old = Delivery.objects.get(pk=instance.pk)
        instance._old_status = old.status
    except Delivery.DoesNotExist:
        instance._old_status = None


@receiver(post_save, sender=Delivery)
def handle_delivery_updates(sender, instance, created, **kwargs):
    try:
        if (
            instance.status == Delivery.Status.DELIVERED
            and instance._old_status != Delivery.Status.DELIVERED
        ):
            increment_courier_performance(instance)

    except Exception as e:
        log_system_event(
            level="error",
            message=str(e),
            source="dashboard.delivery_signal",
        )


@receiver(post_save, sender=Prescription)
def handle_prescription_updates(sender, instance, created, **kwargs):
    try:
        from .services import recalculate_daily_stats
        recalculate_daily_stats(instance.created_at.date())

    except Exception as e:
        log_system_event(
            level="error",
            message=str(e),
            source="dashboard.prescription_signal",
        )