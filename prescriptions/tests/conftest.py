import pytest
from django.contrib.auth import get_user_model


API_PREFIX = "/api/v7/prescriptions"


@pytest.fixture
def api_prefix():
    return API_PREFIX


@pytest.fixture
def create_user(db):
    """
    User yaratish uchun fixture.
    Django setup bo'lganidan keyin get_user_model() chaqiriladi.
    """
    User = get_user_model()

    def _create_user(
        phone_number,
        password="12344321",
        is_staff=False,
        is_superuser=False,
        **extra
    ):
        return User.objects.create_user(
            phone_number=phone_number,
            password=password,
            is_staff=is_staff,
            is_superuser=is_superuser,
            **extra
        )
    return _create_user
