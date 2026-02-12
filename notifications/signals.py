import logging
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.db import transaction

from notifications.services import NotificationService
from notifications.models import NotificationType, NotificationChannel

logger = logging.getLogger(__name__)


# =========================================================
# ORDER STATUS TRACKING
# =========================================================

_previous_order_status = {}


@receiver(pre_save, sender="orders.Order")
def store_previous_order_status(sender, instance, **kwargs):
    if instance.pk:
        try:
            old = sender.objects.get(pk=instance.pk)
            _previous_order_status[instance.pk] = old.status
        except sender.DoesNotExist:
            pass


@receiver(post_save, sender="orders.Order")
def order_status_changed(sender, instance, created, **kwargs):

    service = NotificationService()

    def send(notification_type):
        service.create_and_send(
            user=instance.user,
            notification_type=notification_type,
            channel=NotificationChannel.SMS,
            metadata={
                "order_id": instance.id,
                "total_price": getattr(instance, "total_price", None),
            }
        )

    try:
        if created:
            transaction.on_commit(
                lambda: send(NotificationType.ORDER_CREATED)
            )
            return

        previous_status = _previous_order_status.pop(instance.pk, None)

        if previous_status == instance.status:
            return  # Status o‘zgarmagan

        status_map = {
            "awaiting_prescription": NotificationType.ORDER_AWAITING_PRESCRIPTION,
            "awaiting_payment": NotificationType.ORDER_AWAITING_PAYMENT,
            "paid": NotificationType.ORDER_PAID,
            "preparing": NotificationType.ORDER_PREPARING,
            "ready_for_delivery": NotificationType.ORDER_READY_FOR_DELIVERY,
            "on_the_way": NotificationType.ORDER_ON_THE_WAY,
            "delivered": NotificationType.ORDER_DELIVERED,
            "cancelled": NotificationType.ORDER_CANCELLED,
        }

        notification_type = status_map.get(instance.status)

        if notification_type:
            transaction.on_commit(lambda: send(notification_type))

    except Exception as e:
        logger.error(f"Order notification failed: {e}")


# =========================================================
# PRESCRIPTION STATUS TRACKING
# =========================================================

_previous_prescription_status = {}


@receiver(pre_save, sender="prescriptions.Prescription")
def store_previous_prescription_status(sender, instance, **kwargs):
    if instance.pk:
        try:
            old = sender.objects.get(pk=instance.pk)
            _previous_prescription_status[instance.pk] = old.status
        except sender.DoesNotExist:
            pass


@receiver(post_save, sender="prescriptions.Prescription")
def prescription_status_changed(sender, instance, created, **kwargs):

    if created:
        return  # Yangi yaratilganda SMS kerak emas

    service = NotificationService()

    previous_status = _previous_prescription_status.pop(instance.pk, None)

    if previous_status == instance.status:
        return

    try:
        if instance.status == "approved":
            transaction.on_commit(
                lambda: service.create_and_send(
                    user=instance.user,
                    notification_type=NotificationType.PRESCRIPTION_APPROVED,
                    metadata={
                        "prescription_id": instance.id
                    }
                )
            )

        elif instance.status == "rejected":
            transaction.on_commit(
                lambda: service.create_and_send(
                    user=instance.user,
                    notification_type=NotificationType.PRESCRIPTION_REJECTED,
                    metadata={
                        "prescription_id": instance.id,
                        "reason": getattr(instance, "rejection_reason", None),
                    }
                )
            )

    except Exception as e:
        logger.error(f"Prescription notification failed: {e}")
