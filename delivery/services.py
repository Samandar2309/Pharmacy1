from django.core.exceptions import ValidationError, PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone

from users.models import User
from orders.models import Order
from delivery.models import Delivery, DeliveryStatusHistory


class DeliveryService:
    """
    Delivery app uchun yagona va qat’iy service qatlam.

    Qoidalar:
    - tashqi qatlam (API / View / Test) faqat ID uzatadi
    - service ichida barcha tekshiruvlar yopiladi
    - status o‘zgarishlari auditga yoziladi
    """

    # =====================================================
    # OPERATOR / ADMIN
    # =====================================================

    @staticmethod
    @transaction.atomic
    def assign_courier(*, order: Order, courier_id: int, changed_by):
        """
        Buyurtmani kuryerga biriktirish.

        Qoidalar:
        - buyurtma READY_FOR_DELIVERY bo‘lishi shart
        - faqat courier rolidagi user biriktiriladi
        """

        if order.status != Order.Status.READY_FOR_DELIVERY:
            raise ValidationError(
                "Faqat 'Yetkazishga tayyor' holatidagi buyurtma kuryerga biriktiriladi."
            )

        courier = get_object_or_404(
            User,
            id=courier_id,
            role="courier",
            is_active=True,
        )

        delivery, created = Delivery.objects.select_for_update().get_or_create(
            order=order,
            is_active=True,
            defaults={
                "courier": courier,
                "courier_assigned_at": timezone.now(),
            },
        )

        if not created:
            delivery.courier = courier
            delivery.courier_assigned_at = timezone.now()
            delivery._changed_by = changed_by  # For signal
            delivery.save(update_fields=["courier", "courier_assigned_at", "updated_at"])
        else:
            # New delivery created
            delivery._changed_by = changed_by
            delivery._status_changed = True
            delivery._old_status = Delivery.Status.READY
            # Signal will handle history

        return delivery

    # =====================================================
    # COURIER
    # =====================================================

    @staticmethod
    @transaction.atomic
    def mark_on_the_way(*, delivery: Delivery, courier):
        """
        Kuryer delivery’ni 'Yo‘lda' holatiga o‘tkazadi.
        """

        if courier.role != "courier":
            raise PermissionDenied("Faqat kuryer delivery holatini o‘zgartira oladi.")

        if delivery.courier_id != courier.id:
            raise PermissionDenied("Bu delivery sizga biriktirilmagan.")

        if delivery.status != Delivery.Status.READY:
            raise ValidationError(
                "Faqat 'Yetkazishga tayyor' holatidan 'Yo‘lda' ga o‘tiladi."
            )

        old_status = delivery.status

        delivery.status = Delivery.Status.ON_THE_WAY
        delivery.save(update_fields=["status", "updated_at"])

        delivery.order.status = Order.Status.ON_THE_WAY
        delivery.order.save(update_fields=["status", "updated_at"])

        DeliveryStatusHistory.objects.create(
            delivery=delivery,
            old_status=old_status,
            new_status=delivery.status,
            changed_by=courier,
        )

        return delivery

    @staticmethod
    @transaction.atomic
    def mark_delivered(*, delivery: Delivery, courier):
        """
        Kuryer delivery’ni 'Yetkazildi' deb belgilaydi.
        """

        if courier.role != "courier":
            raise PermissionDenied("Faqat kuryer delivery holatini o‘zgartira oladi.")

        if delivery.courier_id != courier.id:
            raise PermissionDenied("Bu delivery sizga biriktirilmagan.")

        if delivery.status != Delivery.Status.ON_THE_WAY:
            raise ValidationError(
                "Faqat 'Yo‘lda' holatidagi delivery yetkazildi deb belgilanadi."
            )

        old_status = delivery.status
        now = timezone.now()

        delivery.status = Delivery.Status.DELIVERED
        delivery.delivered_at = now
        delivery.is_active = False
        delivery.save(
            update_fields=["status", "delivered_at", "is_active", "updated_at"]
        )

        delivery.order.status = Order.Status.DELIVERED
        delivery.order.save(update_fields=["status", "updated_at"])

        DeliveryStatusHistory.objects.create(
            delivery=delivery,
            old_status=old_status,
            new_status=delivery.status,
            changed_by=courier,
        )

        return delivery

    # =====================================================
    # CANCEL
    # =====================================================

    @staticmethod
    @transaction.atomic
    def cancel_delivery(*, delivery: Delivery, changed_by, reason: str = ""):
        """
        Delivery’ni bekor qilish (admin / operator).
        """

        if delivery.status == Delivery.Status.DELIVERED:
            raise ValidationError("Yetkazilgan delivery bekor qilinmaydi.")

        old_status = delivery.status

        delivery.status = Delivery.Status.CANCELED
        delivery.canceled_at = timezone.now()
        delivery.is_active = False
        delivery.note = reason
        delivery.save(
            update_fields=["status", "canceled_at", "is_active", "note", "updated_at"]
        )

        delivery.order.status = Order.Status.CANCELED
        delivery.order.save(update_fields=["status", "updated_at"])

        DeliveryStatusHistory.objects.create(
            delivery=delivery,
            old_status=old_status,
            new_status=delivery.status,
            changed_by=changed_by,
        )

        return delivery
