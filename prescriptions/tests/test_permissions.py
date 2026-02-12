import pytest
from rest_framework.test import APIClient
from prescriptions.tests.utils import get_test_image


@pytest.mark.django_db
def test_cannot_upload_more_than_5_images(create_user):
    client_user = create_user(
        phone_number="+998947077178",
        password="12344321"
    )

    api = APIClient()
    api.force_authenticate(user=client_user)

    images = [get_test_image(name=f"{i}.png") for i in range(6)]

    response = api.post(
        "/api/v7/prescriptions/",
        data={"rasmlar": images},
        format="multipart"
    )

    assert response.status_code == 400
