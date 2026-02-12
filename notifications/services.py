import logging
import requests
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from .models import (
    Notification,
    NotificationTemplate,
    NotificationStatus,
    NotificationChannel,
)

logger = logging.getLogger(__name__)

# =========================================================
# Exceptions
# =========================================================
class NotificationError(Exception):
    pass

class ProviderError(NotificationError):
    pass

# =========================================================
# Provider Strategy
# =========================================================
class BaseNotificationProvider(ABC):
    @abstractmethod
    def send(self, destination: str, message: str) -> Dict[str, Any]:
        pass

# =========================================================
# SMS Provider (DevSMS)
# =========================================================
class DevSMSProvider(BaseNotificationProvider):
    _session = requests.Session()
    RETRIES = 3
    TIMEOUT = 10

    def send(self, destination: str, message: str) -> Dict[str, Any]:
        phone = self._clean(destination)

        # Debug mode - don't send actual SMS
        if settings.SMS_DEBUG:
            logger.info(f"SMS DEBUG MODE - Simulated SMS to {phone}: {message}")
            return {
                "status": "debug",
                "message": "Debug mode: SMS not sent",
                "phone": phone,
            }

        payload = {
            "phone": phone,
            "message": message,
        }

        headers = {
            "Authorization": f"Bearer {settings.DEVSMS_TOKEN}",
            "Content-Type": "application/json",
        }

        last_exception = None
        for attempt in range(self.RETRIES):
            try:
                response = self._session.post(
                    f"{settings.DEVSMS_URL}/send_sms.php",
                    json=payload,
                    headers=headers,
                    timeout=self.TIMEOUT,
                )

                data = response.json()
                if response.status_code == 200 and (data.get("status") == "success" or data.get("ok")):
                    logger.info(f"✅ SMS sent successfully to {phone}")
                    return data

                logger.warning(f"DevSMS returned error: {data}")
                response.raise_for_status()
                return data

            except Exception as e:
                last_exception = e
                logger.warning(f"SMS retry {attempt + 1}/{self.RETRIES} failed: {e}")

        logger.error(f"SMS failed permanently: {last_exception}")
        raise ProviderError(str(last_exception))

    @staticmethod
    def _clean(phone: str) -> str:
        digits = "".join(filter(str.isdigit, phone))
        if len(digits) == 12 and digits.startswith("998"):
            return digits
        return digits

# =========================================================
# Notification Service
# =========================================================
class NotificationService:
    def __init__(self):
        self.sms_provider = DevSMSProvider()

    # -----------------------------
    # Template rendering
    # -----------------------------
    def _render_template(self, *, notification_type: str, channel: str, context: dict) -> str:
        try:
            template = NotificationTemplate.objects.get(
                notification_type=notification_type,
                channel=channel,
                is_active=True,
            )
            return template.render(**context)
        except NotificationTemplate.DoesNotExist:
            logger.warning(f"Template missing for {notification_type}/{channel}")
            # Fallback template for DevSMS
            return f"Dorixona tizimi: ro‘yxatdan o‘tish uchun tasdiqlash kodingiz {context.get('code', 'XXXX')}"

    # -----------------------------
    # Create SYSTEM notification
    # -----------------------------
    @transaction.atomic
    def create_system_notification(
        self,
        *,
        user,
        notification_type: str,
        metadata: Optional[dict] = None,
        custom_message: Optional[str] = None,
    ) -> Notification:
        metadata = metadata or {}
        message = custom_message or self._render_template(
            notification_type=notification_type,
            channel=NotificationChannel.SYSTEM,
            context=metadata,
        )

        return Notification.objects.create(
            user=user,
            notification_type=notification_type,
            channel=NotificationChannel.SYSTEM,
            message=message,
            phone_number=user.phone_number,
            metadata=metadata,
            status=NotificationStatus.SENT,
            is_read=False,
            sent_at=timezone.now(),
        )

    # -----------------------------
    # Create SMS notification
    # -----------------------------
    @transaction.atomic
    def create_sms_notification(
        self,
        *,
        user,
        notification_type: str,
        metadata: Optional[dict] = None,
        custom_message: Optional[str] = None,
    ) -> Notification:
        metadata = metadata or {}
        message = custom_message or self._render_template(
            notification_type=notification_type,
            channel=NotificationChannel.SMS,
            context=metadata,
        )

        return Notification.objects.create(
            user=user,
            notification_type=notification_type,
            channel=NotificationChannel.SMS,
            message=message,
            phone_number=user.phone_number,
            metadata=metadata,
            status=NotificationStatus.PENDING,
            is_read=False,
        )

    # -----------------------------
    # Send single notification
    # -----------------------------
    def send(self, notification: Notification) -> Notification:
        if notification.channel != NotificationChannel.SMS:
            return notification
        if notification.status == NotificationStatus.SENT:
            return notification

        notification.mark_processing()

        try:
            provider_response = self.sms_provider.send(
                notification.phone_number,
                notification.message,
            )
            notification.mark_sent(provider_response)
        except Exception as e:
            logger.warning(f"SMS send warning (will retry): {e}")
            notification.mark_failed(
                error_message=str(e),
                provider_response=None,
            )

        return notification

    # -----------------------------
    # Main entrypoint
    # -----------------------------
    def notify(
        self,
        *,
        user,
        notification_type: str,
        metadata: Optional[dict] = None,
        send_sms: bool = True,
    ):
        # 1️⃣ Always create system notification
        self.create_system_notification(
            user=user,
            notification_type=notification_type,
            metadata=metadata,
        )

        # 2️⃣ Optionally create + send SMS
        if send_sms:
            sms_notification = self.create_sms_notification(
                user=user,
                notification_type=notification_type,
                metadata=metadata,
            )
            transaction.on_commit(lambda: self.send(sms_notification))

        return True

    # -----------------------------
    # Retry failed SMS
    # -----------------------------
    def retry_failed(self):
        failed_notifications = Notification.objects.filter(
            status=NotificationStatus.FAILED,
            channel=NotificationChannel.SMS,
        )
        for notification in failed_notifications:
            if not notification.can_retry():
                continue
            if notification.last_attempt_at:
                delta = timezone.now() - notification.last_attempt_at
                if delta.total_seconds() < 30:
                    continue
            self.send(notification)

    # -----------------------------
    # Bulk send (admin)
    # -----------------------------
    def bulk_send(self, queryset):
        for notification in queryset.filter(channel=NotificationChannel.SMS):
            self.send(notification)
