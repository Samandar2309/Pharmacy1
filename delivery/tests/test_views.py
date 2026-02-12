import pytest
from rest_framework.reverse import reverse
from rest_framework import status

from delivery.models import Delivery


@pytest.mark.django_db
def test_courier_can_see_own_deliveries(api_client, courier_user, delivery):
    api_client.force_authenticate(user=courier_user)

    url = reverse("delivery:courier-delivery-list")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK

    # pagination bo‘lsa ham, bo‘lmasa ham ishlaydi
    if isinstance(response.data, dict):
        assert response.data["count"] == 1
    else:
        assert len(response.data) == 1


@pytest.mark.django_db
def test_courier_update_status(api_client, courier_user, delivery):
    api_client.force_authenticate(user=courier_user)

    # holatni aniq READY qilib olamiz
    delivery.status = Delivery.Status.READY
    delivery.save(update_fields=["status"])

    url = reverse(
        "delivery:courier-update-status",
        kwargs={"delivery_id": delivery.id}
    )

    response = api_client.post(
        url,
        {"status": Delivery.Status.ON_THE_WAY},
        format="json"
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["status"] == Delivery.Status.ON_THE_WAY


@pytest.mark.django_db
def test_operator_assign_courier(api_client, operator_user, courier_user, order_ready):
    api_client.force_authenticate(user=operator_user)

    # ishonch hosil qilamiz: delivery hali yo‘q
    assert not hasattr(order_ready, "delivery")

    url = reverse(
        "delivery:assign-courier",
        kwargs={"order_id": order_ready.id}
    )

    response = api_client.post(
        url,
        {"courier_id": courier_user.id},
        format="json"
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["courier"]["id"] == courier_user.id
