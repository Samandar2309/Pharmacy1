import pytest
from decimal import Decimal
from unittest.mock import patch
from datetime import date

from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

from products.models import Product, Category
from orders.models import Cart, CartItem, Order


User = get_user_model()

BASE = "/api/v3/orders/orders/"
DATA = {"delivery_address": "Toshkent"}


# =========================================================
# FIXTURES
# =========================================================

@pytest.fixture
def user():
    return User.objects.create_user(
        phone_number="+998901111111",
        password="1234",
        role="customer"
    )


@pytest.fixture
def operator():
    return User.objects.create_user(
        phone_number="+998902222222",
        password="1234",
        role="operator"
    )


@pytest.fixture
def auth_client(user):
    c = APIClient()
    c.force_authenticate(user)
    return c


@pytest.fixture
def category():
    return Category.objects.create(name="Test", slug="test")


@pytest.fixture
def product(category):
    return Product.objects.create(
        name="Paracetamol",
        slug="para",
        category=category,
        price=Decimal("10000"),
        stock=100,
        is_active=True,
        is_prescription_required=False,  # ✅ REAL FIELD
    )


# =========================================================
# HELPERS
# =========================================================

def add_cart(user, product, qty=1):
    cart, _ = Cart.objects.get_or_create(user=user)
    return CartItem.objects.create(cart=cart, product=product, quantity=qty)


# =========================================================
# BASIC CHECKOUT
# =========================================================

@pytest.mark.django_db
def test_checkout_success(auth_client, user, product):
    add_cart(user, product, 2)

    r = auth_client.post(BASE, DATA)

    assert r.status_code == 201
    assert Order.objects.count() == 1


@pytest.mark.django_db
def test_checkout_empty_cart(auth_client):
    r = auth_client.post(BASE, DATA)
    assert r.status_code == 400


# =========================================================
# PRESCRIPTION LOGIC
# =========================================================

@pytest.mark.django_db
def test_prescription_required(auth_client, user, category):
    p = Product.objects.create(
        name="Rx",
        slug="rx",
        category=category,
        price=10000,
        stock=10,
        is_prescription_required=True,  # ✅ FIXED
    )

    add_cart(user, p)

    auth_client.post(BASE, DATA)

    order = Order.objects.first()

    assert order.status == Order.Status.AWAITING_PRESCRIPTION
    assert order.needs_prescription is True


# =========================================================
# PRICE FREEZE
# =========================================================

@pytest.mark.django_db
def test_price_freeze(auth_client, user, product):
    add_cart(user, product)

    old_price = product.price
    product.price = 99999
    product.save()

    auth_client.post(BASE, DATA)

    item = Order.objects.first().items.first()

    assert item.price == old_price


# =========================================================
# STATUS TRANSITIONS
# =========================================================

@pytest.mark.django_db
def test_invalid_transition(auth_client, user, product):
    add_cart(user, product)

    auth_client.post(BASE, DATA)
    order = Order.objects.first()

    r = auth_client.post(
        f"{BASE}{order.id}/change-status/",
        {"status": "delivered"}
    )

    assert r.status_code == 400


# =========================================================
# CANCEL
# =========================================================

@pytest.mark.django_db
def test_cancel_returns_stock(auth_client, user, product):
    add_cart(user, product, 5)

    old = product.stock

    auth_client.post(BASE, DATA)
    order = Order.objects.first()

    auth_client.post(f"{BASE}{order.id}/cancel/")

    product.refresh_from_db()

    assert product.stock == old


# =========================================================
# PERMISSION (customer only own orders)
# =========================================================

@pytest.mark.django_db
def test_customer_cannot_see_others_orders(user, product):
    other = User.objects.create_user(
        phone_number="+998903333333",
        password="1234",
        role="customer"
    )

    add_cart(user, product)

    client = APIClient()
    client.force_authenticate(user)
    client.post(BASE, DATA)

    client.force_authenticate(other)
    r = client.get(BASE)

    assert len(r.data["results"]) == 0


# =========================================================
# NOTIFICATION (MOCK)
# =========================================================

@pytest.mark.django_db
@patch("notifications.services.NotificationService.order_created")  # ✅ FIXED PATH
def test_notification_called(mock_notify, auth_client, user, product):
    add_cart(user, product)

    auth_client.post(BASE, DATA)

    mock_notify.assert_called_once()


# =========================================================
# PAGINATION
# =========================================================

@pytest.mark.django_db
def test_pagination(auth_client, user, product):
    for _ in range(25):
        add_cart(user, product)
        auth_client.post(BASE, DATA)

    r = auth_client.get(BASE)

    assert len(r.data["results"]) == 20


# =========================================================
# EXPIRED PRODUCT VALIDATION
# =========================================================

@pytest.mark.django_db
def test_expired_product(category):
    with pytest.raises(Exception):
        Product.objects.create(
            name="Old",
            slug="old",
            category=category,
            price=100,
            stock=10,
            expiry_date=date(2020, 1, 1),
        )
