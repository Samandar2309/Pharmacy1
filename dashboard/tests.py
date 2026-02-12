from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status

from users.models import User
from orders.models import Order, OrderItem
from products.models import Product, Category
from delivery.models import Delivery
from payments.models import Payment

from dashboard.models import DailyStats, ProductPerformance


class DashboardTestCase(APITestCase):

    def setUp(self):
        # Admin
        self.admin = User.objects.create_user(
            phone_number="+998901234567",
            password="admin123",
            role="admin",
            is_active=True,
        )

        # Operator
        self.operator = User.objects.create_user(
            phone_number="+998901000111",
            password="operator123",
            role="operator",
            is_active=True,
        )

        # Courier
        self.courier = User.objects.create_user(
            phone_number="+998901112233",
            password="courier123",
            role="courier",
            is_active=True,
        )

        # Customer
        self.customer = User.objects.create_user(
            phone_number="+998901998877",
            password="customer123",
            role="customer",
            is_active=True,
        )

        self.category = Category.objects.create(name="Test Category")

        # Product
        self.product = Product.objects.create(
            name="Test Dori",
            price=10000,
            stock=100,
            is_prescription_required=False,
            category=self.category,
            description="Test",
            usage="Test",
            manufacturer="Test",
            sku="TEST-001",
        )

        self.client.force_authenticate(user=self.admin)

    def test_admin_dashboard_accessible(self):
        url = reverse("dashboard:admin-dashboard")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_operator_dashboard_accessible(self):
        self.client.force_authenticate(user=self.operator)
        url = reverse("dashboard:operator-dashboard")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_courier_dashboard_accessible(self):
        self.client.force_authenticate(user=self.courier)
        url = reverse("dashboard:courier-dashboard")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_customer_dashboard_accessible(self):
        self.client.force_authenticate(user=self.customer)
        url = reverse("dashboard:customer-dashboard")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_order_creation_updates_daily_stats(self):
        Order.objects.create(
            user=self.admin,
            status=Order.Status.DRAFT,
            total_price=10000,
            delivery_address="Test",
        )

        today = timezone.now().date()
        stats = DailyStats.objects.filter(date=today).first()

        self.assertIsNotNone(stats)
        self.assertEqual(stats.total_orders, 1)

    def test_product_performance_increment(self):
        order = Order.objects.create(
            user=self.admin,
            status=Order.Status.PAID,
            total_price=20000,
            delivery_address="Test",
        )

        OrderItem.objects.create(
            order=order,
            product=self.product,
            quantity=2,
            price=self.product.price,
        )

        order.status = Order.Status.DELIVERED
        order.save()

        performance = ProductPerformance.objects.first()
        self.assertIsNotNone(performance)
        self.assertEqual(performance.total_sold, 2)

    def test_payment_success_updates_revenue(self):
        order = Order.objects.create(
            user=self.admin,
            status=Order.Status.AWAITING_PAYMENT,
            total_price=50000,
            delivery_address="Test",
        )

        payment = Payment.objects.create(
            order=order,
            user=self.admin,
            payment_id="PAY-TEST-001",
            provider=Payment.Provider.CLICK,
            amount=50000,
            status=Payment.Status.PENDING,
        )

        payment.status = Payment.Status.SUCCESS
        payment.completed_at = timezone.now()
        payment.save()

        today = timezone.now().date()
        stats = DailyStats.objects.get(date=today)
        self.assertEqual(stats.total_revenue, 50000)

    def test_delivery_updates_courier_performance(self):
        order = Order.objects.create(
            user=self.admin,
            status=Order.Status.PAID,
            total_price=15000,
            delivery_address="Test",
        )

        delivery = Delivery.objects.create(
            order=order,
            courier=self.courier,
            status=Delivery.Status.READY,
        )


        delivery.status = Delivery.Status.DELIVERED
        delivery.delivered_at = timezone.now()  # 🔥 SHU QATORNI QO‘SHISH KERAK
        delivery.save()

        self.assertTrue(
            self.courier.courier_stats.exists()
        )

    def test_system_health_log_creation(self):
        from dashboard.services import log_system_event

        log_system_event(
            level="error",
            message="Test error",
            source="test_case",
        )

        from dashboard.models import SystemHealthLog

        self.assertEqual(SystemHealthLog.objects.count(), 1)