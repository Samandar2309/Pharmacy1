from django.db import models, transaction
from django.conf import settings
from django.utils import timezone


# =========================================================
# ABSTRACT BASE
# =========================================================

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# =========================================================
# CHANNEL TYPE (Future-proof)
# =========================================================

class NotificationChannel(models.TextChoices):
    SMS = "sms", "SMS"
    EMAIL = "email", "Email"
    PUSH = "push", "Push"
    SYSTEM = "system", "System (In-App)"


# =========================================================
# NOTIFICATION TYPE (TZ GA MOS)
# =========================================================

class NotificationType(models.TextChoices):

    # AUTH
    OTP = "otp", "Tasdiqlash kodi"
    PASSWORD_RESET = "password_reset", "Parol tiklash"

    # PRESCRIPTION
    PRESCRIPTION_APPROVED = "prescription_approved", "Retsept tasdiqlandi"
    PRESCRIPTION_REJECTED = "prescription_rejected", "Retsept rad etildi"

    # ORDER
    ORDER_CREATED = "order_created", "Buyurtma yaratildi"
    ORDER_AWAITING_PRESCRIPTION = "order_awaiting_prescription", "Retsept kutilmoqda"
    ORDER_AWAITING_PAYMENT = "order_awaiting_payment", "To‘lov kutilmoqda"
    ORDER_PAID = "order_paid", "To‘lov qilindi"
    ORDER_PREPARING = "order_preparing", "Tayyorlanmoqda"
    ORDER_READY_FOR_DELIVERY = "order_ready_for_delivery", "Yetkazishga tayyor"
    ORDER_ON_THE_WAY = "order_on_the_way", "Yo‘lda"
    ORDER_DELIVERED = "order_delivered", "Yetkazildi"
    ORDER_CANCELLED = "order_cancelled", "Bekor qilindi"


# =========================================================
# STATUS
# =========================================================

class NotificationStatus(models.TextChoices):
    PENDING = "pending", "Kutilmoqda"
    PROCESSING = "processing", "Yuborilmoqda"
    SENT = "sent", "Yuborildi"
    FAILED = "failed", "Xato"
    CANCELLED = "cancelled", "Bekor qilindi"


# =========================================================
# MAIN NOTIFICATION MODEL
# =========================================================

class Notification(TimeStampedModel):
    """
    Universal notification log.
    SMS + Push + In-App + Email.
    """

    # -----------------------------------------------------
    # USER
    # -----------------------------------------------------

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
        db_index=True
    )

    phone_number = models.CharField(max_length=13)

    # -----------------------------------------------------
    # CHANNEL & TYPE
    # -----------------------------------------------------

    channel = models.CharField(
        max_length=20,
        choices=NotificationChannel.choices,
        default=NotificationChannel.SYSTEM,
        db_index=True
    )

    notification_type = models.CharField(
        max_length=60,
        choices=NotificationType.choices,
        db_index=True
    )

    # -----------------------------------------------------
    # MESSAGE
    # -----------------------------------------------------

    message = models.TextField()

    # -----------------------------------------------------
    # READ SYSTEM (🔔 BADGE)
    # -----------------------------------------------------

    is_read = models.BooleanField(default=False, db_index=True)
    read_at = models.DateTimeField(null=True, blank=True)

    # -----------------------------------------------------
    # DELIVERY STATUS
    # -----------------------------------------------------

    status = models.CharField(
        max_length=20,
        choices=NotificationStatus.choices,
        default=NotificationStatus.PENDING,
        db_index=True
    )

    sent_at = models.DateTimeField(null=True, blank=True)
    last_attempt_at = models.DateTimeField(null=True, blank=True)

    # -----------------------------------------------------
    # RETRY SYSTEM
    # -----------------------------------------------------

    retry_count = models.PositiveIntegerField(default=0)
    max_retries = models.PositiveIntegerField(default=3)

    # -----------------------------------------------------
    # DEBUG / PROVIDER DATA
    # -----------------------------------------------------

    provider_response = models.JSONField(blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)

    # -----------------------------------------------------
    # CONTEXT
    # -----------------------------------------------------

    metadata = models.JSONField(default=dict, blank=True)

    # =====================================================
    # META
    # =====================================================

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "is_read"]),
            models.Index(fields=["user", "notification_type"]),
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["channel", "status"]),
        ]

    def __str__(self):
        return f"{self.notification_type} → {self.user.phone_number}"

    # =====================================================
    # READ METHODS (🔔)
    # =====================================================

    @transaction.atomic
    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=["is_read", "read_at", "updated_at"])

    @transaction.atomic
    def mark_as_unread(self):
        self.is_read = False
        self.read_at = None
        self.save(update_fields=["is_read", "read_at", "updated_at"])

    # =====================================================
    # DELIVERY METHODS
    # =====================================================

    @transaction.atomic
    def mark_processing(self):
        self.status = NotificationStatus.PROCESSING
        self.last_attempt_at = timezone.now()
        self.save(update_fields=["status", "last_attempt_at", "updated_at"])

    @transaction.atomic
    def mark_sent(self, provider_response=None):
        self.status = NotificationStatus.SENT
        self.sent_at = timezone.now()
        self.provider_response = provider_response
        self.save(update_fields=[
            "status",
            "sent_at",
            "provider_response",
            "updated_at"
        ])

    @transaction.atomic
    def mark_failed(self, error_message=None, provider_response=None):
        self.retry_count += 1
        self.last_attempt_at = timezone.now()
        self.status = NotificationStatus.FAILED
        self.error_message = error_message
        self.provider_response = provider_response

        self.save(update_fields=[
            "status",
            "retry_count",
            "error_message",
            "provider_response",
            "last_attempt_at",
            "updated_at"
        ])

    def can_retry(self):
        return (
            self.retry_count < self.max_retries and
            self.status == NotificationStatus.FAILED
        )

    # =====================================================
    # CLASS HELPERS
    # =====================================================

    @classmethod
    def unread_count(cls, user):
        return cls.objects.filter(user=user, is_read=False).count()

    @classmethod
    def mark_all_as_read(cls, user):
        return cls.objects.filter(user=user, is_read=False).update(
            is_read=True,
            read_at=timezone.now()
        )


# =========================================================
# TEMPLATE SYSTEM
# =========================================================

class NotificationTemplate(TimeStampedModel):

    notification_type = models.CharField(
        max_length=60,
        choices=NotificationType.choices
    )

    channel = models.CharField(
        max_length=20,
        choices=NotificationChannel.choices,
        default=NotificationChannel.SMS
    )

    template_text = models.TextField()
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("notification_type", "channel")

    def __str__(self):
        return f"{self.notification_type} ({self.channel})"

    def render(self, **context):
        try:
            return self.template_text.format(**context)
        except KeyError as e:
            raise ValueError(f"Template variable missing: {e}")
