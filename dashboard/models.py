from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
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
# 1️⃣ DAILY SYSTEM STATS (Materialized Daily Snapshot)
# =========================================================

class DailyStats(TimeStampedModel):
    """
    Har kuni uchun agregatsiyalangan statistik ma'lumot.
    Celery yoki signal orqali update qilinadi.
    """

    date = models.DateField(unique=True, db_index=True)

    # Users
    total_users = models.PositiveIntegerField(default=0)
    total_operators = models.PositiveIntegerField(default=0)
    total_couriers = models.PositiveIntegerField(default=0)

    # Orders
    total_orders = models.PositiveIntegerField(default=0)
    completed_orders = models.PositiveIntegerField(default=0)
    cancelled_orders = models.PositiveIntegerField(default=0)

    # Revenue
    total_revenue = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0
    )

    # Prescriptions
    prescriptions_pending = models.PositiveIntegerField(default=0)
    prescriptions_approved = models.PositiveIntegerField(default=0)
    prescriptions_rejected = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-date"]
        indexes = [
            models.Index(fields=["date"]),
        ]

    def __str__(self):
        return f"Stats for {self.date}"


# =========================================================
# 2️⃣ PRODUCT PERFORMANCE
# =========================================================

class ProductPerformance(TimeStampedModel):
    """
    Eng ko‘p sotilgan dorilar monitoringi
    """

    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="performance_stats",
    )

    total_sold = models.PositiveIntegerField(default=0)
    total_revenue = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0
    )

    last_sold_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("product",)
        indexes = [
            models.Index(fields=["total_sold"]),
        ]
        ordering = ["-total_sold"]

    def __str__(self):
        return f"{self.product.name} performance"


# =========================================================
# 3️⃣ COURIER PERFORMANCE
# =========================================================

class CourierPerformance(TimeStampedModel):
    """
    Kuryer samaradorligi monitoringi
    """

    courier = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="courier_stats",
        limit_choices_to={"role": "courier"},
    )

    total_deliveries = models.PositiveIntegerField(default=0)
    successful_deliveries = models.PositiveIntegerField(default=0)

    average_delivery_time_minutes = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)]
    )

    total_earnings = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0
    )

    class Meta:
        unique_together = ("courier",)
        ordering = ["-total_deliveries"]

    def __str__(self):
        return f"{self.courier} performance"


# =========================================================
# 4️⃣ SYSTEM HEALTH LOG
# =========================================================

class SystemHealthLog(TimeStampedModel):
    """
    Monitoring va audit uchun.
    Xatoliklar, payment failure, SMS failure va boshqalar.
    """

    LEVEL_CHOICES = (
        ("info", "Info"),
        ("warning", "Warning"),
        ("error", "Error"),
        ("critical", "Critical"),
    )

    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    message = models.TextField()

    source = models.CharField(
        max_length=100,
        help_text="Qaysi app yoki moduldan kelgan"
    )

    resolved = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["level"]),
            models.Index(fields=["resolved"]),
        ]

    def __str__(self):
        return f"[{self.level.upper()}] {self.source}"
