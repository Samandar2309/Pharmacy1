# 🚀 QUICK START - Notifications App

## 1. Migration va Initial Setup

```bash
# Migrationlarni yaratish
python manage.py makemigrations notifications

# Migrationlarni qo'llash
python manage.py migrate notifications
```

## 2. Default Shablonlarni Yuklash

```bash
python manage.py shell
```

Keyin quyidagi kodni ishga tushiring:

```python
from notifications.models import NotificationTemplate, Notification

templates = [
    (Notification.NotificationType.OTP, 'Dorixona: tasdiqlash kodi {code}'),
    (Notification.NotificationType.PASSWORD_RESET, 'Parol tiklash: {code}'),
    (Notification.NotificationType.ORDER_CREATED, 'Buyurtma #{order_id} yaratildi. Summa: {total_price} som'),
    (Notification.NotificationType.ORDER_AWAITING_PRESCRIPTION, 'Buyurtma #{order_id} uchun retsept yuklang'),
    (Notification.NotificationType.ORDER_AWAITING_PAYMENT, 'Buyurtma #{order_id} uchun to\'lov qiling'),
    (Notification.NotificationType.ORDER_PAID, 'Buyurtma #{order_id} to\'lovi qabul qilindi'),
    (Notification.NotificationType.ORDER_PREPARING, 'Buyurtma #{order_id} tayyorlanmoqda'),
    (Notification.NotificationType.ORDER_READY_FOR_DELIVERY, 'Buyurtma #{order_id} yetkazishga tayyor'),
    (Notification.NotificationType.ORDER_ON_THE_WAY, 'Buyurtma #{order_id} yo\'lda'),
    (Notification.NotificationType.ORDER_DELIVERED, 'Buyurtma #{order_id} yetkazildi. Rahmat!'),
    (Notification.NotificationType.ORDER_CANCELLED, 'Buyurtma #{order_id} bekor qilindi'),
    (Notification.NotificationType.PRESCRIPTION_APPROVED, 'Retseptingiz tasdiqlandi'),
    (Notification.NotificationType.PRESCRIPTION_REJECTED, 'Retseptingiz rad etildi. Sabab: {reason}'),
]

for notification_type, template_text in templates:
    NotificationTemplate.objects.get_or_create(
        notification_type=notification_type,
        defaults={'template_text': template_text, 'is_active': True}
    )

print("✅ Shablonlar yuklandi!")
```

## 3. SMS Sozlamalari (.env)

```env
# DevSMS token (https://devsms.uz)
DEVSMS_TOKEN=your_token_here

# Debug mode (True = SMS yuborilmaydi, faqat log)
SMS_DEBUG=True
```

## 4. Test Qilish

```bash
# Barcha testlar
pytest notifications/tests.py -v

# Faqat OTP testlari
pytest notifications/tests.py::TestOTPService -v

# Coverage bilan
pytest notifications/tests.py --cov=notifications --cov-report=html
```

## 5. API Test Qilish (Postman/cURL)

### OTP So'rash
```bash
curl -X POST http://localhost:8000/api/v1/notifications/otp/request/ \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+998901234567", "purpose": "registration"}'
```

### OTP Tekshirish
```bash
curl -X POST http://localhost:8000/api/v1/notifications/otp/verify/ \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+998901234567", "code": "1234", "purpose": "registration"}'
```

### Mening Bildirishnomalarim (Token kerak)
```bash
curl -X GET http://localhost:8000/api/v1/notifications/notifications/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## 6. Admin Panelga Kirish

```
URL: http://localhost:8000/admin/notifications/
```

- Bildirishnomalar: `/admin/notifications/notification/`
- OTP Kodlar: `/admin/notifications/otpcode/`
- Shablonlar: `/admin/notifications/notificationtemplate/`

## 7. Kod Ichida Ishlatish

### OTP Yuborish
```python
from notifications.services import OTPService

otp_service = OTPService()
otp = otp_service.generate_and_send_otp(
    phone_number='+998901234567',
    purpose='registration'
)
```

### Buyurtma Bildirishnomasi
```python
from notifications.services import NotificationService

service = NotificationService()
service.notify_order_created(order)
```

### Manual Bildirishnoma
```python
from notifications.services import NotificationService

service = NotificationService()
notification = service.create_notification(
    user=user,
    notification_type='order_created',
    message='Custom xabar'
)
```

## 8. Muammolarni Hal Qilish

### SMS yuborilmayapti
- `SMS_DEBUG=True` ni tekshiring
- `DEVSMS_TOKEN` ni tekshiring
- Loglarni ko'ring: `tail -f logs/django.log`

### OTP ishlamayapti
- Telefon format: `+998XXXXXXXXX`
- Kod 4 raqam
- 120 soniya ichida kiriting

### Migration xatosi
```bash
python manage.py migrate notifications --fake
python manage.py migrate notifications
```

## 9. Production Checklist

- [ ] `SMS_DEBUG=False` qiling
- [ ] `DEVSMS_TOKEN` to'g'ri token bilan almashtiring
- [ ] Rate limiting sozlang (1 daqiqada 1 SMS)
- [ ] Celery setup (async SMS)
- [ ] Monitoring setup (Sentry, etc.)
- [ ] Backup setup

## 10. Keyingi Qadamlar

1. Celery bilan async SMS yuborish
2. Email bildirishnomalar qo'shish
3. Push notifications (FCM)
4. WebSocket real-time notifications
5. User preferences (bildirishnoma sozlamalari)

---

**Support**: dev@dorixona.uz  
**Docs**: http://localhost:8000/api/docs/
