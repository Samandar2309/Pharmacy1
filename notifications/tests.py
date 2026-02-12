import pytest
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model

from notifications.models import (
    Notification,
    NotificationTemplate,
    NotificationType,
    NotificationStatus,
    NotificationChannel,
)
from notifications.services import NotificationService

User = get_user_model()


# =========================================================
# FIXTURE
# =========================================================

@pytest.fixture
def user(db):
    return User.objects.create_user(
        phone_number="+998901234567",
        password="testpass123",
        first_name="Test",
        last_name="User"
    )


# =========================================================
# NOTIFICATION MODEL TESTS
# =========================================================

@pytest.mark.django_db
class TestNotificationModel:

    def test_create_notification(self, user):
        notification = Notification.objects.create(
            user=user,
            notification_type=NotificationType.ORDER_CREATED,
            channel=NotificationChannel.SYSTEM,
            message="Test message",
            phone_number=user.phone_number,
        )

        assert notification.status == NotificationStatus.PENDING
        assert notification.is_read is False

    def test_mark_as_read(self, user):
        notification = Notification.objects.create(
            user=user,
            notification_type=NotificationType.ORDER_CREATED,
            channel=NotificationChannel.SYSTEM,
            message="Test message",
            phone_number=user.phone_number,
        )

        notification.mark_as_read()
        notification.refresh_from_db()

        assert notification.is_read is True
        assert notification.read_at is not None

    def test_mark_as_failed(self, user):
        notification = Notification.objects.create(
            user=user,
            notification_type=NotificationType.ORDER_CREATED,
            channel=NotificationChannel.SMS,
            message="Test message",
            phone_number=user.phone_number,
            status=NotificationStatus.PENDING,
        )

        notification.mark_failed("error")
        notification.refresh_from_db()

        assert notification.status == NotificationStatus.FAILED
        assert notification.retry_count == 1
        assert notification.error_message == "error"

    def test_unread_count(self, user):
        Notification.objects.create(
            user=user,
            notification_type=NotificationType.ORDER_CREATED,
            channel=NotificationChannel.SYSTEM,
            message="A",
            phone_number=user.phone_number,
        )

        Notification.objects.create(
            user=user,
            notification_type=NotificationType.ORDER_PAID,
            channel=NotificationChannel.SYSTEM,
            message="B",
            phone_number=user.phone_number,
        )

        count = Notification.unread_count(user)
        assert count == 2


# =========================================================
# TEMPLATE TESTS
# =========================================================

@pytest.mark.django_db
class TestNotificationTemplate:

    def test_create_template(self):
        template = NotificationTemplate.objects.create(
            notification_type=NotificationType.ORDER_CREATED,
            channel=NotificationChannel.SMS,
            template_text="Buyurtma #{order_id} yaratildi",
            is_active=True
        )

        assert template.notification_type == NotificationType.ORDER_CREATED
        assert template.channel == NotificationChannel.SMS

    def test_render_template(self):
        template = NotificationTemplate.objects.create(
            notification_type=NotificationType.ORDER_CREATED,
            channel=NotificationChannel.SMS,
            template_text="Buyurtma #{order_id} summa {total}",
            is_active=True
        )

        rendered = template.render(order_id=123, total="50000")

        assert rendered == "Buyurtma #123 summa 50000"


# =========================================================
# NOTIFICATION SERVICE TESTS
# =========================================================

@pytest.mark.django_db
class TestNotificationService:

    def test_notify_creates_system_notification(self, user):
        service = NotificationService()

        notification = service.notify(
            user=user,
            notification_type=NotificationType.ORDER_CREATED,
            metadata={"order_id": 1},
            send_sms=False,
        )

        assert notification.user == user
        assert notification.channel == NotificationChannel.SYSTEM
        assert notification.status == NotificationStatus.SENT
        assert notification.is_read is False

    def test_notify_creates_sms_notification(self, user):
        service = NotificationService()

        service.notify(
            user=user,
            notification_type=NotificationType.ORDER_CREATED,
            metadata={"order_id": 1},
            send_sms=True,
        )

        assert Notification.objects.filter(
            user=user,
            channel=NotificationChannel.SMS
        ).exists()
