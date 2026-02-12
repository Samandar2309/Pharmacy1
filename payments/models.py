from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction
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
# PAYMENT MODEL (Production-Grade)
# =========================================================

class Payment(TimeStampedModel):
    """
    Universal payment model for Click and Payme.
    Thread-safe, idempotent, production-ready.
    """

    class Status(models.TextChoices):
        PENDING = "pending", "Kutilmoqda"
        PROCESSING = "processing", "Jarayonda"
        SUCCESS = "success", "Muvaffaqiyatli"
        FAILED = "failed", "Xato"
        CANCELLED = "cancelled", "Bekor qilindi"
        REFUNDED = "refunded", "Qaytarildi"

    class Provider(models.TextChoices):
        CLICK = "click", "Click"
        PAYME = "payme", "Payme"
        CASH = "cash", "Naqd"

    # =====================================================
    # RELATIONS
    # =====================================================

    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.PROTECT,
        related_name="payments",
        help_text="Buyurtma"
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="payments",
        help_text="To'lovchi foydalanuvchi"
    )

    # =====================================================
    # PAYMENT DETAILS
    # =====================================================

    payment_id = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        help_text="Ichki to'lov ID (unique)"
    )

    provider = models.CharField(
        max_length=20,
        choices=Provider.choices,
        db_index=True,
        help_text="To'lov provayderi"
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
        help_text="To'lov holati"
    )

    amount = models.DecimalField(
        max_digits=16,
        decimal_places=2,
        help_text="To'lov summasi (so'm)"
    )

    # =====================================================
    # PROVIDER-SPECIFIC DATA
    # =====================================================

    # Click fields
    click_trans_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True,
        help_text="Click transaction ID"
    )

    click_paydoc_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Click paydoc ID"
    )

    # Payme fields
    payme_transaction_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True,
        help_text="Payme transaction ID"
    )

    payme_time = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="Payme transaction time (timestamp)"
    )

    # =====================================================
    # METADATA
    # =====================================================

    provider_response = models.JSONField(
        default=dict,
        blank=True,
        help_text="Provider javob ma'lumotlari"
    )

    error_message = models.TextField(
        blank=True,
        help_text="Xatolik xabari"
    )

    # =====================================================
    # TIMESTAMPS
    # =====================================================

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="To'lov yakunlangan vaqt"
    )

    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="To'lov bekor qilingan vaqt"
    )

    # =====================================================
    # META
    # =====================================================

    class Meta:
        verbose_name = "To'lov"
        verbose_name_plural = "To'lovlar"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["payment_id"]),
            models.Index(fields=["provider", "status"]),
            models.Index(fields=["order"]),
            models.Index(fields=["click_trans_id"]),
            models.Index(fields=["payme_transaction_id"]),
        ]

    def __str__(self):
        return f"Payment #{self.payment_id} | {self.provider} | {self.status}"

    # =====================================================
    # VALIDATION
    # =====================================================

    def clean(self):
        if self.provider == self.Provider.CLICK:
            if self.status == self.Status.SUCCESS and not self.click_trans_id:
                raise ValidationError(
                    {"click_trans_id": "Click success uchun click_trans_id majburiy"}
                )

        if self.provider == self.Provider.PAYME:
            if self.status == self.Status.SUCCESS and not self.payme_transaction_id:
                raise ValidationError(
                    {"payme_transaction_id": "Payme success uchun payme_transaction_id majburiy"}
                )

    # =====================================================
    # STATE MACHINE METHODS
    # =====================================================

    @transaction.atomic
    def mark_processing(self):
        """To'lovni jarayonga o'tkazish."""
        if self.status != self.Status.PENDING:
            raise ValidationError("Faqat pending holatidan processing'ga o'tish mumkin.")

        self.status = self.Status.PROCESSING
        self.save(update_fields=["status", "updated_at"])

    @transaction.atomic
    def mark_success(self, *, provider_response: dict = None):
        """To'lovni muvaffaqiyatli yakunlash."""
        if self.status == self.Status.SUCCESS:
            return  # idempotent

        if self.status not in [self.Status.PENDING, self.Status.PROCESSING]:
            raise ValidationError("To'lovni success holatiga o'tkazish mumkin emas.")

        self.status = self.Status.SUCCESS
        self.completed_at = timezone.now()
        if provider_response:
            self.provider_response = provider_response

        self.full_clean()
        self.save(update_fields=["status", "completed_at", "provider_response", "updated_at"])

    @transaction.atomic
    def mark_failed(self, *, error_message: str = "", provider_response: dict = None):
        """To'lovni xato holatiga o'tkazish."""
        if self.status == self.Status.FAILED:
            return  # idempotent

        self.status = self.Status.FAILED
        self.error_message = error_message
        if provider_response:
            self.provider_response = provider_response

        self.save(update_fields=["status", "error_message", "provider_response", "updated_at"])

    @transaction.atomic
    def mark_cancelled(self):
        """To'lovni bekor qilish."""
        if self.status in [self.Status.SUCCESS, self.Status.REFUNDED]:
            raise ValidationError("Success yoki refunded holatida bekor qilib bo'lmaydi.")

        self.status = self.Status.CANCELLED
        self.cancelled_at = timezone.now()
        self.save(update_fields=["status", "cancelled_at", "updated_at"])

    # =====================================================
    # HELPERS
    # =====================================================

    @property
    def is_pending(self):
        return self.status == self.Status.PENDING

    @property
    def is_success(self):
        return self.status == self.Status.SUCCESS

    @property
    def is_failed(self):
        return self.status == self.Status.FAILED


# =========================================================
# PAYMENT LOG (Audit Trail)
# =========================================================

class PaymentLog(TimeStampedModel):
    """
    Payment jarayonidagi barcha eventlarni log qilish.
    Production debugging uchun muhim.
    """

    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        related_name="logs"
    )

    event_type = models.CharField(
        max_length=50,
        db_index=True,
        help_text="prepare/complete/authorize/etc"
    )

    request_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Provider'ga yuborilgan request"
    )

    response_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Provider'dan kelgan response"
    )

    error_message = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["payment", "created_at"]),
        ]

    def __str__(self):
        return f"{self.payment_id} | {self.event_type}"
