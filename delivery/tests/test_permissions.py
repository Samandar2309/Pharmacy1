import pytest
from delivery.permissions import IsCourierOwnDelivery


@pytest.mark.django_db
def test_courier_can_access_own_delivery(courier_user, delivery):
    """
    Kuryer o‘ziga biriktirilgan delivery’ni ko‘ra olishi kerak
    """
    permission = IsCourierOwnDelivery()
    request = type("Request", (), {"user": courier_user})()

    assert permission.has_object_permission(request, None, delivery) is True


@pytest.mark.django_db
def test_courier_cannot_access_other_courier_delivery(db, courier_user, delivery):
    """
    Boshqa kuryer begona delivery’ni ko‘ra olmasligi kerak
    """
    from users.models import User

    other_courier = User.objects.create_user(
        phone_number="998909999999",
        password="test123",
        role="courier"
    )

    permission = IsCourierOwnDelivery()
    request = type("Request", (), {"user": other_courier})()

    assert permission.has_object_permission(request, None, delivery) is False
