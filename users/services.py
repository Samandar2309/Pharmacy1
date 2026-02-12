import logging
import secrets
from datetime import timedelta

from django.db import transaction
from django.utils import timezone
from django.contrib.auth import get_user_model

from rest_framework.exceptions import ValidationError

from .models import SMSVerification
from notifications.services import NotificationService
from notifications.models import NotificationType

logger = logging.getLogger(__name__)

User = get_user_model()


# =====================================================
# OTP SERVICE (AUTHENTICATION RESPONSIBILITY ONLY)
# =====================================================

class OTPService:
    """
    Responsible ONLY for authentication OTP logic.

    - Generate OTP
    - Rate limit
    - Expiry
    - Mark used
    - Integrate with NotificationService
    """

    CODE_LENGTH = 4
    EXPIRE_SECONDS = 120
    RATE_LIMIT_SECONDS = 60
    MAX_ATTEMPTS = 3

    def __init__(self):
        self.notification_service = NotificationService()

    # -------------------------------------------------
    # GENERATE CODE
    # -------------------------------------------------

    def _generate_code(self) -> str:
        return f"{secrets.randbelow(9000) + 1000}"

    # -------------------------------------------------
    # SEND OTP
    # -------------------------------------------------

    @transaction.atomic
    def send_otp(self, phone_number: str) -> None:

        # Rate limit check
        since = timezone.now() - timedelta(seconds=self.RATE_LIMIT_SECONDS)

        recent = SMSVerification.objects.filter(
            phone_number=phone_number,
            created_at__gte=since
        ).exists()

        if recent:
            raise ValidationError(
                f"{self.RATE_LIMIT_SECONDS} soniya kuting va qayta urinib ko‘ring."
            )

        # Old kodlarni invalid qilish
        SMSVerification.objects.filter(
            phone_number=phone_number,
            is_used=False
        ).update(is_used=True)

        # Yangi kod yaratish
        code = self._generate_code()

        sms = SMSVerification.objects.create(
            phone_number=phone_number,
            code=code
        )

        # Notification orqali yuborish
        self.notification_service.notify(
            user=self._get_or_create_temp_user(phone_number),
            notification_type=NotificationType.OTP,
            metadata={"code": code},
            send_sms=True
        )

        logger.info(f"OTP created for {phone_number}")

        return sms

    # -------------------------------------------------
    # VERIFY OTP
    # -------------------------------------------------

    @transaction.atomic
    def verify_otp(self, phone_number: str, code: str) -> bool:

        sms = (
            SMSVerification.objects
            .select_for_update()
            .filter(
                phone_number=phone_number,
                code=code,
                is_used=False
            )
            .order_by("-created_at")
            .first()
        )

        if not sms:
            return False

        if sms.is_expired:
            return False

        sms.is_used = True
        sms.save(update_fields=["is_used"])

        logger.info(f"OTP verified for {phone_number}")
        return True

    # -------------------------------------------------
    # CLEANUP (optional cron)
    # -------------------------------------------------

    def cleanup_expired(self) -> int:
        expired = SMSVerification.objects.filter(
            is_used=False,
            created_at__lt=timezone.now() - timedelta(seconds=self.EXPIRE_SECONDS)
        )

        count = expired.count()
        expired.delete()

        return count

    # -------------------------------------------------
    # TEMP USER HANDLING (OPTIONAL)
    # -------------------------------------------------

    def _get_or_create_temp_user(self, phone_number: str) -> User:
        """
        OTP register jarayonida user hali verify bo‘lmagan bo‘lishi mumkin.
        """
        user, _ = User.objects.get_or_create(
            phone_number=phone_number,
            defaults={
                "username": phone_number,
                "is_active": True
            }
        )
        return user
