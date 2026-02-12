from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Payment


@receiver(post_save, sender=Payment)
def payment_completed_signal(sender, instance, created, **kwargs):
    """
    To'lov muvaffaqiyatli bo'lganda notifikatsiya yuborish.
    """
    if not created and instance.status == Payment.Status.SUCCESS:
        # Send notification to user
        from notifications.services import NotificationService
        from notifications.models import NotificationType

        service = NotificationService()

        try:
            service.notify(
                user=instance.user,
                notification_type=NotificationType.ORDER_PAID,
                metadata={
                    "order_id": instance.order.id,
                    "payment_id": instance.payment_id,
                    "amount": str(instance.amount),
                },
                send_sms=True,
            )
        except Exception as e:
            # Log error but don't break payment flow
            from dashboard.services import log_system_event

            log_system_event(
                level="error",
                message=f"Payment notification failed: {str(e)}",
                source="payments.signals",
            )
