from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Prescription


@receiver(post_save, sender=Prescription)
def prescription_status_changed(sender, instance, created, update_fields=None, **kwargs):
    """
    Prescription holati o‘zgarganda ishlaydigan signal.

    Qoidalar:
    - faqat status bilan bog‘liq o‘zgarishlar
    - faqat DB commit bo‘lgandan keyin
    - signal ichida og‘ir logika yo‘q
    """

    # 1️⃣ YANGI RETSEPT YARATILDI
    if created:
        def on_commit_created():
            # notifications.notify_operators(
            #     message="Yangi retsept keldi"
            # )
            pass

        transaction.on_commit(on_commit_created)
        return

    # Agar update_fields berilgan bo‘lsa va status yo‘q bo‘lsa — chiqib ketamiz
    if update_fields is not None and 'status' not in update_fields:
        return

    # 2️⃣ STATUSGA QARAB EVENT CHIQARAMIZ
    if instance.status == Prescription.Status.APPROVED:
        def on_commit_approved():
            # notifications.notify_user(
            #     user=instance.user,
            #     message="Retseptingiz tasdiqlandi"
            # )
            pass

        transaction.on_commit(on_commit_approved)

    elif instance.status == Prescription.Status.REJECTED:
        def on_commit_rejected():
            # notifications.notify_user(
            #     user=instance.user,
            #     message=f"Retsept rad etildi: {instance.rejection_reason}"
            # )
            pass

        transaction.on_commit(on_commit_rejected)
