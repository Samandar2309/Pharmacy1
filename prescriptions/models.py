from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models, transaction
from django.utils import timezone
from django.contrib.auth import get_user_model


User = get_user_model()


# ============================================================
# PRESCRIPTION (STATE MACHINE + AUDIT SAFE)
# ============================================================

class Prescription(models.Model):
    """
    Prescription — bitta tekshiruv jarayoni.
    Qat'iy state-machine:
        PENDING -> APPROVED | REJECTED
    """

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='prescriptions',
        verbose_name='Mijoz'
    )

    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='prescriptions',
        verbose_name='Buyurtma'
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True
    )

    rejection_reason = models.TextField(
        blank=True,
        null=True,
        verbose_name='Rad etish sababi'
    )

    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_prescriptions',
        verbose_name='Tekshirgan operator'
    )

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Tekshiruv vaqti'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Yaratilgan vaqti'
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Yangilangan vaqti'
    )

    class Meta:
        verbose_name = 'Prescription'
        verbose_name_plural = 'Prescriptions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]

    # -----------------------------
    # DOMAIN RULES (STATE MACHINE)
    # -----------------------------

    def _ensure_pending(self):
        """
        Business rule:
        faqat PENDING holatdagina qaror chiqarish mumkin.
        """
        if self.status != self.Status.PENDING:
            raise ValidationError(
                'Faqat PENDING holatdagi retseptni o‘zgartirish mumkin.'
            )

    def approve(self, operator):
        """
        Retseptni tasdiqlash.
        """
        self._ensure_pending()

        self.status = self.Status.APPROVED
        self.reviewed_by = operator
        self.reviewed_at = timezone.now()
        self.rejection_reason = None

        self.save(update_fields=[
            'status',
            'reviewed_by',
            'reviewed_at',
            'rejection_reason',
            'updated_at'
        ])

    def reject(self, operator, reason: str):
        """
        Retseptni rad etish.
        """
        self._ensure_pending()

        if not reason:
            raise ValidationError('Rad etish sababi majburiy.')

        self.status = self.Status.REJECTED
        self.reviewed_by = operator
        self.reviewed_at = timezone.now()
        self.rejection_reason = reason

        self.save(update_fields=[
            'status',
            'reviewed_by',
            'reviewed_at',
            'rejection_reason',
            'updated_at'
        ])

    # -----------------------------
    # DATA INVARIANTS
    # -----------------------------

    def clean(self):
        """
        Data-level invariant (admin / serializer uchun).
        """
        if self.status == self.Status.REJECTED and not self.rejection_reason:
            raise ValidationError({
                'rejection_reason': 'Rad etish sababi majburiy.'
            })

    def __str__(self):
        return f'Prescription #{self.id}'


# ============================================================
# PRESCRIPTION IMAGE (MULTI IMAGE + LIMIT + RACE SAFE)
# ============================================================

class PrescriptionImage(models.Model):
    """
    Retseptga tegishli rasm(lar).
    Unlimited emas — biznes cheklovlari bilan.
    """

    MAX_IMAGES = 5
    MAX_FILE_SIZE_MB = 5

    prescription = models.ForeignKey(
        Prescription,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='Retsept'
    )

    image = models.ImageField(
        upload_to='prescriptions/%Y/%m/%d/',
        validators=[
            FileExtensionValidator(['jpg', 'jpeg', 'png'])
        ],
        verbose_name='Retsept rasmi'
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Yuklangan vaqti'
    )

    class Meta:
        verbose_name = 'Prescription Image'
        verbose_name_plural = 'Prescription Images'
        ordering = ['uploaded_at']

    def clean(self):
        if self.image and self.image.size > self.MAX_FILE_SIZE_MB * 1024 * 1024:
            raise ValidationError(
                f'Rasm hajmi {self.MAX_FILE_SIZE_MB}MB dan oshmasligi kerak.'
            )

    def save(self, *args, **kwargs):
        """
        Race-condition safe save:
        parallel upload bo‘lsa ham limit buzilmaydi.
        """
        with transaction.atomic():
            prescription = (
                Prescription.objects
                .select_for_update()
                .get(pk=self.prescription_id)
            )

            if prescription.images.count() >= self.MAX_IMAGES:
                raise ValidationError(
                    f'Maksimal {self.MAX_IMAGES} ta rasm yuklash mumkin.'
                )

            self.full_clean()
            super().save(*args, **kwargs)

    def __str__(self):
        return f'Image #{self.id} for Prescription #{self.prescription_id}'


# ============================================================
# PRESCRIPTION ITEM (AUDIT + LEGAL TRACE)
# ============================================================

class PrescriptionItem(models.Model):
    """
    Retseptda ko‘rsatilgan dorilar.
    Audit, tekshiruv va qonuniy nazorat uchun muhim.
    """

    prescription = models.ForeignKey(
        Prescription,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Retsept'
    )

    product = models.ForeignKey(
        'products.Product',
        on_delete=models.PROTECT,
        related_name='prescription_items',
        verbose_name='Dori'
    )

    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name='Miqdori'
    )

    class Meta:
        verbose_name = 'Prescription Item'
        verbose_name_plural = 'Prescription Items'
        unique_together = ('prescription', 'product')

    def __str__(self):
        return f'{self.product} × {self.quantity}'
