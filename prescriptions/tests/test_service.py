import pytest
from django.core.exceptions import ValidationError

from prescriptions.models import Prescription
from prescriptions.services import approve_prescription, reject_prescription


@pytest.mark.django_db
def test_approve_pending_prescription(create_user):
    user = create_user(phone_number="998901111111")
    operator = create_user(
        phone_number="998902222222",
        is_staff=True
    )

    prescription = Prescription.objects.create(user=user)

    approve_prescription(
        prescription=prescription,
        operator=operator
    )

    prescription.refresh_from_db()

    assert prescription.status == Prescription.Status.APPROVED
    assert prescription.reviewed_by == operator
    assert prescription.reviewed_at is not None


@pytest.mark.django_db
def test_cannot_approve_non_pending(create_user):
    user = create_user(phone_number="998903333333")
    operator = create_user(
        phone_number="998904444444",
        is_staff=True
    )

    prescription = Prescription.objects.create(
        user=user,
        status=Prescription.Status.APPROVED
    )

    with pytest.raises(ValidationError):
        approve_prescription(
            prescription=prescription,
            operator=operator
        )


@pytest.mark.django_db
def test_reject_requires_reason(create_user):
    user = create_user(phone_number="998905555555")
    operator = create_user(
        phone_number="998906666666",
        is_staff=True
    )

    prescription = Prescription.objects.create(user=user)

    with pytest.raises(ValidationError):
        reject_prescription(
            prescription=prescription,
            operator=operator,
            reason=""
        )
