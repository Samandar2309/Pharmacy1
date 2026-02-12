from django.db import models
from django.core.validators import MinValueValidator
from slugify import slugify


# =========================================
# ABSTRACT BASE MODEL (professional pattern)
# =========================================
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SoftDeleteModel(models.Model):
    is_deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True


# =========================
# CATEGORY MODEL
# =========================
class Category(TimeStampedModel, SoftDeleteModel):
    name = models.CharField(
        max_length=255,
        unique=True,
        db_index=True
    )

    slug = models.SlugField(
        max_length=255,
        unique=True,
        blank=True
    )

    icon = models.ImageField(
        upload_to="category_icons/%Y/%m/",
        blank=True,
        null=True
    )

    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# =========================
# ACTIVE SUBSTANCE MODEL
# =========================
class ActiveSubstance(TimeStampedModel):
    name = models.CharField(
        max_length=255,
        unique=True,
        db_index=True
    )

    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


# =========================
# PRODUCT MODEL (OPTIMIZED)
# =========================
class Product(TimeStampedModel, SoftDeleteModel):
    name = models.CharField(
        max_length=255,
        db_index=True
    )

    slug = models.SlugField(
        unique=True,
        blank=True
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products"
    )

    active_substances = models.ManyToManyField(
        ActiveSubstance,
        related_name="products",
        blank=True
    )

    description = models.TextField()
    usage = models.TextField()

    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    stock = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)]
    )

    is_prescription_required = models.BooleanField(default=False)

    manufacturer = models.CharField(
        max_length=255,
        db_index=True
    )

    image = models.ImageField(
        upload_to="products/%Y/%m/%d/",
        blank=True,
        null=True
    )

    expiry_date = models.DateField(blank=True, null=True)

    sku = models.CharField(
        max_length=100,
        unique=True,
        db_index=True
    )

    order_count = models.PositiveIntegerField(default=0)

    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]

        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["price"]),
            models.Index(fields=["category"]),
            models.Index(fields=["manufacturer"]),
            models.Index(fields=["is_active"]),
        ]

        constraints = [
            models.UniqueConstraint(
                fields=["name", "manufacturer"],
                name="unique_product_per_manufacturer"
            )
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.name}-{self.sku}")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def is_available(self):
        return (
            self.is_active
            and not self.is_deleted
            and self.stock > 0
        )
