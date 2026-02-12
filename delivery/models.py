from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone

from orders.models import Order

User = settings.AUTH_USER_MODEL


# =========================================================
# COMMON BASE
# =========================================================

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# =========================================================
# DELIVERY
# =========================================================

class DeliveryQuerySet(models.QuerySet):
    """
    Custom QuerySet for common delivery queries
    """
    
    def active(self):
        """Faol deliverylar"""
        return self.filter(is_active=True)
    
    def by_status(self, status):
        """Status bo'yicha filter"""
        return self.filter(status=status)
    
    def ready(self):
        """Yetkazishga tayyor"""
        return self.active().filter(status=Delivery.Status.READY)
    
    def on_the_way(self):
        """Yo'lda"""
        return self.active().filter(status=Delivery.Status.ON_THE_WAY)
    
    def delivered(self):
        """Yetkazilgan"""
        return self.filter(status=Delivery.Status.DELIVERED)
    
    def for_courier(self, courier):
        """Kuryerga biriktirilgan deliverylar"""
        return self.active().filter(courier=courier)
    
    def ready_for_assignment(self):
        """Kuryerga biriktirilmagan, tayyor deliverylar"""
        return self.ready().filter(courier__isnull=True)
    
    def with_related(self):
        """Related objectlarni optimized yuklash"""
        return self.select_related('order', 'courier', 'order__user')
    
    def with_history(self):
        """Status tarixi bilan birga"""
        return self.prefetch_related('status_history')


class DeliveryManager(models.Manager):
    """
    Custom Manager for Delivery model
    """
    
    def get_queryset(self):
        return DeliveryQuerySet(self.model, using=self._db)
    
    def active(self):
        return self.get_queryset().active()
    
    def ready_for_assignment(self):
        return self.get_queryset().ready_for_assignment()
    
    def for_courier(self, courier):
        return self.get_queryset().for_courier(courier)


class Delivery(TimeStampedModel):
    """
    TZ 8-bo‘limga to‘liq mos delivery modeli.
    """

    class Status(models.TextChoices):
        READY = "ready", "Yetkazishga tayyor"
        ON_THE_WAY = "on_the_way", "Yo‘lda"
        DELIVERED = "delivered", "Yetkazildi"
        CANCELED = "canceled", "Bekor qilindi"

    # -----------------------------------------------------
    # RELATIONS
    # -----------------------------------------------------

    order = models.OneToOneField(
        Order,
        on_delete=models.PROTECT,
        related_name="delivery",
        help_text="Yetkazishga tayyor buyurtma"
    )

    courier = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="deliveries",
        limit_choices_to={"role": "courier"},
        help_text="Biriktirilgan kuryer (ixtiyoriy)"
    )

    # -----------------------------------------------------
    # STATE
    # -----------------------------------------------------

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.READY,
        db_index=True
    )

    is_active = models.BooleanField(
        default=True,
        help_text="Faol delivery (soft delete)"
    )

    # -----------------------------------------------------
    # TIME TRACKING (TZga mos)
    # -----------------------------------------------------

    courier_assigned_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Kuryer real biriktirilgan vaqt"
    )

    delivered_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Buyurtma yetkazilgan vaqt"
    )

    canceled_at = models.DateTimeField(
        null=True,
        blank=True
    )

    note = models.TextField(
        blank=True,
        help_text="Operator yoki kuryer izohi"
    )

    # -----------------------------------------------------
    # MANAGER
    # -----------------------------------------------------

    objects = DeliveryManager()

    # -----------------------------------------------------
    # META
    # -----------------------------------------------------

    class Meta:
        verbose_name = "Yetkazib berish"
        verbose_name_plural = "Yetkazib berishlar"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["order"],
                condition=Q(is_active=True),
                name="unique_active_delivery_per_order"
            )
        ]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["courier", "status"]),
        ]

    def __str__(self):
        return f"Delivery #{self.pk} | Order #{self.order_id} | {self.status}"

    # =====================================================
    # VALIDATION
    # =====================================================

    def clean(self):
        if self.courier and getattr(self.courier, "role", None) != "courier":
            raise ValidationError(
                {"courier": "Faqat kuryer rolidagi foydalanuvchi biriktirilishi mumkin."}
            )

        if self.status == self.Status.ON_THE_WAY and not self.courier:
            raise ValidationError(
                {"courier": "Yo‘lda holati uchun kuryer biriktirilgan bo‘lishi shart."}
            )

        if self.status == self.Status.DELIVERED and not self.delivered_at:
            raise ValidationError(
                {"delivered_at": "Yetkazildi holati uchun delivered_at majburiy."}
            )

        if self.status == self.Status.CANCELED and not self.canceled_at:
            raise ValidationError(
                {"canceled_at": "Bekor qilindi holati uchun canceled_at majburiy."}
            )

    def save(self, *args, **kwargs):
        """
        Override save to:
        1. Force validation (clean() is NOT called automatically)
        2. Auto-set timestamps based on status changes
        3. Track status changes for history
        """
        # Force validation
        self.full_clean()

        # Track old status for history (if updating)
        if self.pk:
            try:
                old_delivery = Delivery.objects.get(pk=self.pk)
                if old_delivery.status != self.status:
                    self._old_status = old_delivery.status
                    self._status_changed = True
            except Delivery.DoesNotExist:
                pass

        # Auto-set timestamps
        if self.status == self.Status.DELIVERED and not self.delivered_at:
            self.delivered_at = timezone.now()
        
        if self.status == self.Status.CANCELED and not self.canceled_at:
            self.canceled_at = timezone.now()

        super().save(*args, **kwargs)

    # =====================================================
    # HELPERS
    # =====================================================

    @property
    def is_delivered(self):
        return self.status == self.Status.DELIVERED
    
    @property
    def is_ready(self):
        return self.status == self.Status.READY
    
    @property
    def is_on_the_way(self):
        return self.status == self.Status.ON_THE_WAY
    
    @property
    def is_canceled(self):
        return self.status == self.Status.CANCELED
    
    @property
    def has_courier(self):
        return self.courier is not None
    
    def can_mark_on_the_way(self):
        """Yo'lda holatiga o'tish mumkinmi?"""
        return self.status == self.Status.READY and self.courier is not None
    
    def can_mark_delivered(self):
        """Yetkazildi holatiga o'tish mumkinmi?"""
        return self.status == self.Status.ON_THE_WAY
    
    def can_cancel(self):
        """Bekor qilish mumkinmi?"""
        return self.status not in (self.Status.DELIVERED, self.Status.CANCELED)


# =========================================================
# DELIVERY STATUS HISTORY (AUDIT)
# =========================================================

class DeliveryStatusHistory(models.Model):
    """
    TZ 6.8-band: buyurtma holati o‘zgarishlari tarixi
    """

    delivery = models.ForeignKey(
        Delivery,
        on_delete=models.CASCADE,
        related_name="status_history"
    )

    old_status = models.CharField(
        max_length=20,
        choices=Delivery.Status.choices
    )

    new_status = models.CharField(
        max_length=20,
        choices=Delivery.Status.choices
    )

    changed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    changed_at = models.DateTimeField(
        auto_now_add=True,
        editable=False
    )

    class Meta:
        ordering = ["-changed_at"]
        verbose_name = "Delivery status tarixi"
        verbose_name_plural = "Delivery statuslar tarixi"

    def __str__(self):
        return f"{self.delivery_id}: {self.old_status} → {self.new_status}"
