from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models, transaction
from django.db.models import F, Sum

from products.models import Product

User = settings.AUTH_USER_MODEL


# =========================================================
# COMMON MIXINS
# =========================================================

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# =========================================================
# 1️⃣ CART
# =========================================================

class Cart(TimeStampedModel):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="cart",
    )

    class Meta:
        verbose_name = "Cart"
        verbose_name_plural = "Carts"

    @property
    def total_price(self) -> Decimal:
        return (
            self.items.aggregate(
                total=Sum(
                    F("quantity") * F("product__price"),
                    output_field=models.DecimalField(max_digits=16, decimal_places=2)
                )
            )["total"]
            or Decimal("0.00")
        )

    @property
    def has_prescription_items(self) -> bool:
        return self.items.filter(product__requires_prescription=True).exists()

    def __str__(self):
        return f"Cart({self.user_id})"


class CartItem(TimeStampedModel):
    cart = models.ForeignKey(
        Cart,
        related_name="items",
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(100)]
    )

    class Meta:
        unique_together = ("cart", "product")
        indexes = [models.Index(fields=["cart"])]

    @property
    def subtotal(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.product_id} x {self.quantity}"


# =========================================================
# 2️⃣ ORDER
# =========================================================

class Order(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft"
        AWAITING_PRESCRIPTION = "awaiting_prescription"
        AWAITING_PAYMENT = "awaiting_payment"
        PAID = "paid"
        PREPARING = "preparing"
        READY_FOR_DELIVERY = "ready_for_delivery"
        ON_THE_WAY = "on_the_way"
        DELIVERED = "delivered"
        CANCELLED = "cancelled"

    ALLOWED_TRANSITIONS = {
        Status.DRAFT: [Status.AWAITING_PRESCRIPTION, Status.AWAITING_PAYMENT, Status.CANCELLED],
        Status.AWAITING_PRESCRIPTION: [Status.AWAITING_PAYMENT, Status.CANCELLED],
        Status.AWAITING_PAYMENT: [Status.PAID, Status.CANCELLED],
        Status.PAID: [Status.PREPARING],
        Status.PREPARING: [Status.READY_FOR_DELIVERY],
        Status.READY_FOR_DELIVERY: [Status.ON_THE_WAY],
        Status.ON_THE_WAY: [Status.DELIVERED],
    }

    user = models.ForeignKey(
        User,
        related_name="orders",
        on_delete=models.PROTECT
    )

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True
    )

    total_price = models.DecimalField(
        max_digits=16,
        decimal_places=2,
        default=Decimal("0.00")
    )

    delivery_address = models.TextField()
    needs_prescription = models.BooleanField(default=False)
    prescription_uploaded = models.BooleanField(default=False)

    courier = models.ForeignKey(
        User,
        null=True,
        blank=True,
        related_name="assigned_orders",
        on_delete=models.SET_NULL,
        limit_choices_to={"role": "courier"}
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["user"]),
        ]

    def recalculate_total(self):
        total = self.items.aggregate(
            total=Sum(F("quantity") * F("price"))
        )["total"] or Decimal("0.00")
        self.total_price = total
        self.save(update_fields=["total_price"])

    @transaction.atomic
    def change_status(self, new_status, changed_by=None):
        allowed = self.ALLOWED_TRANSITIONS.get(self.status, [])
        if new_status not in allowed:
            raise ValidationError(f"{self.status} → {new_status} not allowed")

        old = self.status
        self.status = new_status
        self.save(update_fields=["status"])

        OrderStatusHistory.objects.create(
            order=self,
            from_status=old,
            to_status=new_status,
            changed_by=changed_by
        )

    def __str__(self):
        return f"Order#{self.pk}"


# =========================================================
# ORDER ITEM
# =========================================================

class OrderItem(TimeStampedModel):
    order = models.ForeignKey(
        Order,
        related_name="items",
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    price = models.DecimalField(max_digits=16, decimal_places=2)

    def save(self, *args, **kwargs):
        if not self.price:
            self.price = self.product.price
        super().save(*args, **kwargs)
        self.order.recalculate_total()

    def delete(self, *args, **kwargs):
        order = self.order
        super().delete(*args, **kwargs)
        order.recalculate_total()

    @property
    def subtotal(self):
        return self.price * self.quantity


# =========================================================
# PRESCRIPTION
# =========================================================

def validate_prescription_file(value):
    if value.size > 5 * 1024 * 1024:
        raise ValidationError("Max 5MB")


class Prescription(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "pending"
        APPROVED = "approved"
        REJECTED = "rejected"

    order = models.OneToOneField(
        Order,
        related_name="prescription",
        on_delete=models.CASCADE
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True
    )

    operator_comment = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    def clean(self):
        if self.images.count() > 5:
            raise ValidationError("Max 5 images allowed")


class PrescriptionImage(models.Model):
    prescription = models.ForeignKey(
        Prescription,
        related_name="images",
        on_delete=models.CASCADE
    )
    image = models.ImageField(
        upload_to="prescriptions/%Y/%m/%d/",
        validators=[validate_prescription_file]
    )


# =========================================================
# PAYMENT
# =========================================================

class OrderPayment(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "pending"
        SUCCESS = "success"
        FAILED = "failed"

    order = models.OneToOneField(
        Order,
        related_name="payment",
        on_delete=models.CASCADE
    )

    payment_id = models.CharField(max_length=120, unique=True)
    transaction_id = models.CharField(max_length=255, unique=True, null=True, blank=True)

    amount = models.DecimalField(max_digits=16, decimal_places=2)
    method = models.CharField(max_length=50)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    @transaction.atomic
    def mark_success(self, transaction_id: str):
        if self.status == self.Status.SUCCESS:
            return

        self.status = self.Status.SUCCESS
        self.transaction_id = transaction_id
        self.save(update_fields=["status", "transaction_id"])

        self.order.change_status(Order.Status.PAID)


# =========================================================
# ORDER STATUS HISTORY
# =========================================================

class OrderStatusHistory(models.Model):
    order = models.ForeignKey(
        Order,
        related_name="history",
        on_delete=models.CASCADE
    )

    from_status = models.CharField(max_length=30)
    to_status = models.CharField(max_length=30)

    changed_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    created_at = models.DateTimeField(auto_now_add=True)
