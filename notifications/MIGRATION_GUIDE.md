# NOTIFICATION APP - MIGRATION GUIDE

## Migration Yaratish

```bash
# Windows CMD
python manage.py makemigrations notifications
python manage.py migrate notifications
```

## Initial Data (Shablonlar)

Migration dan keyin default shablonlarni yuklash uchun:

```bash
python manage.py shell
```

```python
from notifications.models import NotificationTemplate, Notification

# OTP shablon
NotificationTemplate.objects.create(
    notification_type=Notification.NotificationType.OTP,
    template_text='Dorixona tizimi: tasdiqlash kodingiz {code}',
    is_active=True
)

# Parol tiklash
NotificationTemplate.objects.create(
    notification_type=Notification.NotificationType.PASSWORD_RESET,
    template_text='Parol tiklash kodi: {code}. 120 soniya amal qiladi.',
    is_active=True
)

# Buyurtma yaratildi
NotificationTemplate.objects.create(
    notification_type=Notification.NotificationType.ORDER_CREATED,
    template_text='Buyurtma #{order_id} muvaffaqiyatli yaratildi. Jami: {total_price} som.',
    is_active=True
)

# Retsept kutilmoqda
NotificationTemplate.objects.create(
    notification_type=Notification.NotificationType.ORDER_AWAITING_PRESCRIPTION,
    template_text='Buyurtma #{order_id} uchun retsept yuklang.',
    is_active=True
)

# Tolov kutilmoqda
NotificationTemplate.objects.create(
    notification_type=Notification.NotificationType.ORDER_AWAITING_PAYMENT,
    template_text='Buyurtma #{order_id} uchun tolov qiling. Summa: {total_price} som.',
    is_active=True
)

# Tolov qilindi
NotificationTemplate.objects.create(
    notification_type=Notification.NotificationType.ORDER_PAID,
    template_text='Buyurtma #{order_id} uchun tolov qabul qilindi.',
    is_active=True
)

# Tayyorlanmoqda
NotificationTemplate.objects.create(
    notification_type=Notification.NotificationType.ORDER_PREPARING,
    template_text='Buyurtma #{order_id} tayyorlanmoqda.',
    is_active=True
)

# Yetkazishga tayyor
NotificationTemplate.objects.create(
    notification_type=Notification.NotificationType.ORDER_READY_FOR_DELIVERY,
    template_text='Buyurtma #{order_id} yetkazishga tayyor. Tez orada kuryer yetkazadi.',
    is_active=True
)

# Yolda
NotificationTemplate.objects.create(
    notification_type=Notification.NotificationType.ORDER_ON_THE_WAY,
    template_text='Buyurtma #{order_id} yolda.',
    is_active=True
)

# Yetkazildi
NotificationTemplate.objects.create(
    notification_type=Notification.NotificationType.ORDER_DELIVERED,
    template_text='Buyurtma #{order_id} yetkazildi. Rahmat!',
    is_active=True
)

# Bekor qilindi
NotificationTemplate.objects.create(
    notification_type=Notification.NotificationType.ORDER_CANCELLED,
    template_text='Buyurtma #{order_id} bekor qilindi.',
    is_active=True
)

# Retsept tasdiqlandi
NotificationTemplate.objects.create(
    notification_type=Notification.NotificationType.PRESCRIPTION_APPROVED,
    template_text='Retseptingiz tasdiqlandi. Buyurtmani davom ettiring.',
    is_active=True
)

# Retsept rad etildi
NotificationTemplate.objects.create(
    notification_type=Notification.NotificationType.PRESCRIPTION_REJECTED,
    template_text='Retseptingiz rad etildi. Sabab: {reason}',
    is_active=True
)

print("✅ Barcha shablonlar yuklandi!")
```

## Yoki Management Command orqali

```bash
python manage.py loaddata notifications/fixtures/templates.json
```

## Tekshirish

```bash
python manage.py shell
```

```python
from notifications.models import NotificationTemplate

# Barcha shablonlar
templates = NotificationTemplate.objects.all()
for t in templates:
    print(f"{t.notification_type}: {t.template_text[:50]}...")

# Soni
print(f"\nJami {templates.count()} ta shablon")
```
