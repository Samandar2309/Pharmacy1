import pytest
from django.utils import timezone

from delivery.services import DeliveryService
from delivery.models import Delivery
from orders.models import Order


@pytest.mark.django_db
def test_assign_courier_success(order_ready, courier_user, operator_user):
    delivery = DeliveryService.assign_courier(
        order=order_ready,
        courier_id=courier_user.id,
        changed_by=operator_user
    )

    assert delivery.courier == courier_user
    assert delivery.status == Delivery.Status.READY
    assert delivery.courier_assigned_at is not None


@pytest.mark.django_db
def test_mark_on_the_way(delivery, courier_user):
    delivery = DeliveryService.mark_on_the_way(
        delivery=delivery,
        courier=courier_user
    )

    assert delivery.status == Delivery.Status.ON_THE_WAY
    assert delivery.order.status == Order.Status.ON_THE_WAY


@pytest.mark.django_db
def test_mark_delivered(delivery, courier_user):
    delivery.status = Delivery.Status.ON_THE_WAY
    delivery.save()

    delivery = DeliveryService.mark_delivered(
        delivery=delivery,
        courier=courier_user
    )

    assert delivery.status == Delivery.Status.DELIVERED
    assert delivery.delivered_at is not None
    assert delivery.order.status == Order.Status.DELIVERED
