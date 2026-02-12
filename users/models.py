from datetime import timedelta
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone
import re
from django.core.exceptions import ValidationError


# =====================================================
# ABSTRACT BASE MODELS
# =====================================================

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SoftDeleteQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_deleted=False)

    def deleted(self):
        return self.filter(is_deleted=True)


class ActiveManager(models.Manager):
    """Default manager → only active objects"""

    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db).filter(is_deleted=False)


class SoftDeleteModel(models.Model):
    is_deleted = models.BooleanField(default=False)

    objects = ActiveManager()      # 🔥 faqat active
    all_objects = models.Manager() # 🔥 hammasi

    class Meta:
        abstract = True


# =====================================================
# CUSTOM USER MANAGER
# =====================================================

class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def _normalize_phone(self, phone: str) -> str:
        """
        Qabul qiladi:
            947077178
            998947077178
            +998947077178
            +998 94 707 71 78

        Saqlaydi:
            +998947077178
        """

        if not phone:
            raise ValidationError("Telefon raqam majburiy")

        # faqat raqamlarni qoldiramiz
        digits = re.sub(r"\D", "", phone)

        # 9XXXXXXXX → 9989XXXXXXXX
        if len(digits) == 9:
            digits = "998" + digits

        # 9989XXXXXXXX → OK
        if len(digits) == 12 and digits.startswith("998"):
            return f"+{digits}"

        raise ValidationError("Telefon raqam noto‘g‘ri formatda")

    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError("Telefon raqam majburiy")

        phone_number = self._normalize_phone(phone_number)

        extra_fields.setdefault("username", phone_number)

        user = self.model(phone_number=phone_number, **extra_fields)

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("role", User.Role.ADMIN)

        return self.create_user(phone_number, password, **extra_fields)


# =====================================================
# USER MODEL (10/10 PRODUCTION)
# =====================================================

class User(AbstractUser, TimeStampedModel, SoftDeleteModel):

    # ---------------------------------------------
    # ROLES
    # ---------------------------------------------
    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        OPERATOR = "operator", "Operator"
        COURIER = "courier", "Courier"
        CUSTOMER = "customer", "Customer"

    # ---------------------------------------------
    # AUTH FIELDS
    # ---------------------------------------------
    username = models.CharField(
        max_length=150,
        unique=True,
        blank=True,
        null=True,
        db_index=True
    )

    phone_regex = RegexValidator(
        regex=r"^\+998\d{9}$",
        message="Format: +998XXXXXXXXX"
    )

    phone_number = models.CharField(
        max_length=13,
        unique=True,
        db_index=True,
        validators=[phone_regex]
    )

    role = models.CharField(
        max_length=15,
        choices=Role.choices,
        default=Role.CUSTOMER,
        db_index=True
    )

    address = models.TextField(blank=True)

    # ---------------------------------------------
    # VERIFICATION
    # ---------------------------------------------
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True, db_index=True)

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    # ---------------------------------------------
    # META
    # ---------------------------------------------
    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["phone_number"]),
            models.Index(fields=["role"]),
            models.Index(fields=["is_verified"]),
            models.Index(fields=["verified_at"]),
        ]

    # ---------------------------------------------
    # HELPERS (🔥 senior qulaylik)
    # ---------------------------------------------

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN

    @property
    def is_operator(self):
        return self.role == self.Role.OPERATOR

    @property
    def is_courier(self):
        return self.role == self.Role.COURIER

    @property
    def is_customer(self):
        return self.role == self.Role.CUSTOMER

    # ---------------------------------------------
    # BUSINESS METHODS
    # ---------------------------------------------

    def verify(self):
        self.is_verified = True
        self.verified_at = timezone.now()
        self.save(update_fields=["is_verified", "verified_at"])

    def deactivate(self):
        self.is_active = False
        self.save(update_fields=["is_active"])

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.phone_number
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.phone_number} ({self.role})"


# =====================================================
# SMS / OTP VERIFICATION
# =====================================================

class SMSVerification(TimeStampedModel):

    CODE_LENGTH = 4
    EXPIRE_SECONDS = 120
    RATE_LIMIT_SECONDS = 60

    phone_number = models.CharField(max_length=13, db_index=True)
    code = models.CharField(max_length=CODE_LENGTH)
    is_used = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["phone_number", "created_at"]),
        ]

    # ---------------------------------------------
    # LOGIC
    # ---------------------------------------------

    @property
    def is_expired(self):
        return (timezone.now() - self.created_at).total_seconds() > self.EXPIRE_SECONDS

    @classmethod
    def can_send_sms(cls, phone_number):
        since = timezone.now() - timedelta(seconds=cls.RATE_LIMIT_SECONDS)
        return not cls.objects.filter(
            phone_number=phone_number,
            created_at__gte=since
        ).exists()

    def __str__(self):
        return f"OTP {self.phone_number}"
