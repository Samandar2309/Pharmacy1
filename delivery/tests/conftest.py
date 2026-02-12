import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from users.models import User
from orders.models import Order
from delivery.models import Delivery


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def admin_user(db):
    return User.objects.create_user(
        phone_number="+998901111111",
        password="testpass123",
        role="admin",
        first_name="Admin"
    )


@pytest.fixture
def operator_user(db):
    return User.objects.create_user(
        phone_number="+998902222222",
        password="testpass123",
        role="operator",
        first_name="Operator"
    )


@pytest.fixture
def courier_user(db):
    return User.objects.create_user(
        phone_number="+998903333333",
        password="testpass123",
        role="courier",
        first_name="Kuryer"
    )


@pytest.fixture
def order_ready(db, operator_user):
    return Order.objects.create(
        user=operator_user,
        status=Order.Status.READY_FOR_DELIVERY,
        total_price=50000
    )


@pytest.fixture
def delivery(db, order_ready, courier_user):
    return Delivery.objects.create(
        order=order_ready,
        courier=courier_user,
        status=Delivery.Status.READY,
        courier_assigned_at=timezone.now()
    )
