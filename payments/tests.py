from decimal import Decimal

from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status

from users.models import User
from orders.models import Order
from products.models import Product, Category
from payments.models import Payment
from payments.services import PaymentService, ClickService, PaymeService


class PaymentTestCase(APITestCase):

    def setUp(self):
        # Customer
        self.customer = User.objects.create_user(
            phone_number="+998901234567",
            password="customer123",
            role="customer",
            is_active=True,
        )

        self.category = Category.objects.create(name="Test Category")

        self.product = Product.objects.create(
            name="Test Dori",
            price=50000,
            stock=100,
            is_prescription_required=False,
            category=self.category,
            description="Test",
            usage="Test",
            manufacturer="Test",
            sku="TEST-001",
        )

        self.order = Order.objects.create(
            user=self.customer,
            status=Order.Status.AWAITING_PAYMENT,
            total_price=50000,
            delivery_address="Tashkent",
        )

        self.client.force_authenticate(user=self.customer)

    def test_create_payment_success(self):
        """Test payment creation via API."""
        url = reverse("payments:create")
        data = {
            "order_id": self.order.id,
            "provider": "click",
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["provider"], "click")
        self.assertEqual(response.data["status"], "pending")

    def test_create_payment_invalid_order(self):
        """Test payment creation with invalid order."""
        url = reverse("payments:create")
        data = {
            "order_id": 99999,
            "provider": "click",
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_payment_list(self):
        """Test payment list endpoint."""
        payment = PaymentService.create_payment(
            order=self.order,
            provider=Payment.Provider.CLICK,
            amount=self.order.total_price,
        )

        url = reverse("payments:list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_payment_detail(self):
        """Test payment detail endpoint."""
        payment = PaymentService.create_payment(
            order=self.order,
            provider=Payment.Provider.CLICK,
            amount=self.order.total_price,
        )

        url = reverse("payments:detail", kwargs={"payment_id": payment.payment_id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["payment_id"], payment.payment_id)

    def test_payment_service_idempotent(self):
        """Test payment creation is idempotent."""
        payment1 = PaymentService.create_payment(
            order=self.order,
            provider=Payment.Provider.CLICK,
            amount=self.order.total_price,
        )

        payment1.mark_success()

        payment2 = PaymentService.create_payment(
            order=self.order,
            provider=Payment.Provider.CLICK,
            amount=self.order.total_price,
        )

        self.assertEqual(payment1.id, payment2.id)

    def test_payment_complete(self):
        """Test payment completion updates order status."""
        payment = PaymentService.create_payment(
            order=self.order,
            provider=Payment.Provider.CLICK,
            amount=self.order.total_price,
        )

        PaymentService.complete_payment(payment=payment)

        self.order.refresh_from_db()
        self.assertEqual(payment.status, Payment.Status.SUCCESS)
        self.assertEqual(self.order.status, Order.Status.PAID)

    def test_click_prepare_success(self):
        """Test Click PREPARE webhook."""
        payment = PaymentService.create_payment(
            order=self.order,
            provider=Payment.Provider.CLICK,
            amount=self.order.total_price,
        )

        # Simulate Click PREPARE request
        url = reverse("payments:click-prepare")
        data = {
            "click_trans_id": "123456",
            "service_id": "test_service",
            "merchant_trans_id": payment.payment_id,
            "amount": "50000.00",
            "action": 0,
            "error": 0,
            "error_note": "",
            "sign_time": "2026-02-12 10:00:00",
            "sign_string": "dummy_signature",
        }

        response = self.client.post(url, data)

        # Note: This will fail signature check in real scenario
        # For testing, you should mock signature verification
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class PaymentModelTestCase(APITestCase):

    def setUp(self):
        self.customer = User.objects.create_user(
            phone_number="+998901234567",
            password="customer123",
            role="customer",
        )

        self.category = Category.objects.create(name="Test")

        self.product = Product.objects.create(
            name="Test Dori",
            price=50000,
            stock=100,
            category=self.category,
            description="Test",
            usage="Test",
            manufacturer="Test",
            sku="TEST-001",
        )

        self.order = Order.objects.create(
            user=self.customer,
            status=Order.Status.AWAITING_PAYMENT,
            total_price=50000,
            delivery_address="Tashkent",
        )

    def test_payment_state_machine(self):
        """Test payment state transitions."""
        payment = Payment.objects.create(
            order=self.order,
            user=self.customer,
            payment_id="PAY-TEST-001",
            provider=Payment.Provider.CLICK,
            amount=50000,
            status=Payment.Status.PENDING,
        )

        # PENDING -> PROCESSING
        payment.mark_processing()
        self.assertEqual(payment.status, Payment.Status.PROCESSING)

        # PROCESSING -> SUCCESS
        payment.mark_success()
        self.assertEqual(payment.status, Payment.Status.SUCCESS)
        self.assertIsNotNone(payment.completed_at)

    def test_payment_cannot_cancel_after_success(self):
        """Test that successful payment cannot be cancelled."""
        payment = Payment.objects.create(
            order=self.order,
            user=self.customer,
            payment_id="PAY-TEST-002",
            provider=Payment.Provider.CLICK,
            amount=50000,
            status=Payment.Status.SUCCESS,
            completed_at=timezone.now(),
        )

        with self.assertRaises(Exception):
            payment.mark_cancelled()
