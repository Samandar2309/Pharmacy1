from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Prescription, PrescriptionImage
def create_prescription(*, user, order=None, images):
    """
    Mijoz uchun yangi retsept yaratish.
    Barcha jarayon atomic bo‘ladi.
    """
    if not images:
        raise ValidationError("Kamida bitta retsept rasmi yuklanishi kerak.")

    if len(images) > PrescriptionImage.MAX_IMAGES:
        raise ValidationError(
            f"Eng ko‘pi bilan {PrescriptionImage.MAX_IMAGES} ta rasm yuklash mumkin."
        )

    with transaction.atomic():
        prescription = Prescription.objects.create(
            user=user,
            order=order
        )

        for image_data in images:
            PrescriptionImage.objects.create(
                prescription=prescription,
                **image_data
            )

    return prescription
def approve_prescription(*, prescription, operator):
    """
    Operator tomonidan retseptni tasdiqlash.
    """
    if prescription.status != Prescription.Status.PENDING:
        raise ValidationError(
            "Faqat tekshirilayotgan retseptni tasdiqlash mumkin."
        )

    prescription.status = Prescription.Status.APPROVED
    prescription.reviewed_by = operator
    prescription.reviewed_at = timezone.now()
    prescription.rejection_reason = None

    prescription.save(
        update_fields=[
            'status',
            'reviewed_by',
            'reviewed_at',
            'rejection_reason',
            'updated_at'
        ]
    )

    return prescription
def reject_prescription(*, prescription, operator, reason):
    """
    Operator tomonidan retseptni rad etish.
    """
    if prescription.status != Prescription.Status.PENDING:
        raise ValidationError(
            "Faqat tekshirilayotgan retseptni rad etish mumkin."
        )

    if not reason:
        raise ValidationError("Rad etish sababi majburiy.")

    prescription.status = Prescription.Status.REJECTED
    prescription.reviewed_by = operator
    prescription.reviewed_at = timezone.now()
    prescription.rejection_reason = reason

    prescription.save(
        update_fields=[
            'status',
            'reviewed_by',
            'reviewed_at',
            'rejection_reason',
            'updated_at'
        ]
    )

    return prescription
