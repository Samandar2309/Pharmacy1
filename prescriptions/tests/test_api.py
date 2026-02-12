import pytest
from rest_framework.test import APIClient
from prescriptions.tests.utils import get_test_image


@pytest.mark.django_db
def test_client_can_create_prescription_with_image(create_user):
    client_user = create_user(
        phone_number="+998947077178",
        password="12344321"
    )

    api = APIClient()
    api.force_authenticate(user=client_user)

    image = get_test_image()

    response = api.post(
        "/api/v7/prescriptions/",
        data={"rasmlar": [image]},
        format="multipart"
    )

    assert response.status_code == 201
