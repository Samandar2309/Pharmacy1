# 📱 Notifications App - Bildirishnomalar Tizimi

## 📋 Umumiy Ma'lumot

Notifications app - Dorixona loyihasining bildirishnomalar moduli. TZ talablariga muvofiq SMS orqali barcha muhim hodisalar haqida foydalanuvchilarni xabardor qiladi.

## 🎯 Asosiy Funksiyalar

### 1. OTP (One-Time Password) Tizimi
- ✅ 4 xonali tasdiqlash kodlari
- ✅ 120 soniya amal qilish muddati
- ✅ 1 daqiqada 1 marta yuborish cheklovi
- ✅ 3 marta noto'g'ri urinish cheklovi
- ✅ SMS orqali yuborish (DevSMS integration)

### 2. Buyurtma Bildirishnomalari
- ✅ Buyurtma yaratildi
- ✅ Retsept kutilmoqda
- ✅ To'lov kutilmoqda
- ✅ To'lov qilindi
- ✅ Tayyorlanmoqda
- ✅ Yetkazishga tayyor
- ✅ Yo'lda
- ✅ Yetkazildi
- ✅ Bekor qilindi

### 3. Retsept Bildirishnomalari
- ✅ Retsept tasdiqlandi
- ✅ Retsept rad etildi (sabab bilan)

## 📊 Modellar

### 1. `Notification` - Bildirishnomalar
```python
- user: Foydalanuvchi
- notification_type: Bildirishnoma turi (choices)
- message: SMS matni
- phone_number: Qabul qiluvchi telefon
- status: pending/sent/failed/cancelled
- metadata: JSON (qo'shimcha ma'lumotlar)
- retry_count: Qayta urinishlar soni
```

### 2. `OTPCode` - Tasdiqlash Kodlari
```python
- phone_number: Telefon raqam
- code: 4 xonali kod
- purpose: registration/login/password_reset/phone_verification
- expires_at: Amal qilish muddati
- is_used: Ishlatilganmi
- attempts: Urinishlar soni
```

### 3. `NotificationTemplate` - Shablonlar
```python
- notification_type: Bildirishnoma turi
- template_text: Shablon matni (placeholder support)
- is_active: Faolmi
```

## 🔧 Servislar

### 1. `SMSService` - SMS yuborish
```python
sms_service = SMSService()
sms_service.send(phone='+998901234567', message='Test xabar')
```

### 2. `NotificationService` - Bildirishnomalar
```python
service = NotificationService()

# Buyurtma bildirishnomalari
service.notify_order_created(order)
service.notify_order_paid(order)
service.notify_order_delivered(order)

# Retsept bildirishnomalari
service.notify_prescription_approved(prescription)
service.notify_prescription_rejected(prescription)
```

### 3. `OTPService` - Tasdiqlash kodlari
```python
otp_service = OTPService()

# OTP yaratish va yuborish
otp = otp_service.generate_and_send_otp(
    phone_number='+998901234567',
    purpose=OTPCode.Purpose.REGISTRATION
)

# OTP tekshirish
is_valid = otp_service.verify_otp(
    phone_number='+998901234567',
    code='1234',
    purpose=OTPCode.Purpose.REGISTRATION
)
```

## 🌐 API Endpoints

### OTP API (Public - authentication yo'q)

#### 1. OTP so'rash
```http
POST /api/v1/notifications/otp/request/
Content-Type: application/json

{
    "phone_number": "+998901234567",
    "purpose": "registration"
}

Response 200:
{
    "message": "Tasdiqlash kodi yuborildi",
    "phone_number": "+998901234567",
    "expires_in": 120
}
```

#### 2. OTP tekshirish
```http
POST /api/v1/notifications/otp/verify/
Content-Type: application/json

{
    "phone_number": "+998901234567",
    "code": "1234",
    "purpose": "registration"
}

Response 200:
{
    "message": "Kod tasdiqlandi",
    "verified": true
}
```

#### 3. OTP qayta yuborish
```http
POST /api/v1/notifications/otp/resend/
Content-Type: application/json

{
    "phone_number": "+998901234567",
    "purpose": "registration"
}

Response 200:
{
    "message": "Tasdiqlash kodi qayta yuborildi",
    "phone_number": "+998901234567",
    "expires_in": 120
}
```

### Notification API (Authenticated)

#### 1. Mening bildirishnomalarim
```http
GET /api/v1/notifications/notifications/
Authorization: Bearer <token>

Response 200:
[
    {
        "id": 1,
        "notification_type": "order_created",
        "notification_type_display": "Buyurtma yaratildi",
        "message": "Buyurtma #123 muvaffaqiyatli yaratildi...",
        "status": "sent",
        "created_at": "2024-01-15T10:30:00Z"
    }
]
```

#### 2. Bildirishnoma tafsilotlari
```http
GET /api/v1/notifications/notifications/{id}/
Authorization: Bearer <token>

Response 200:
{
    "id": 1,
    "notification_type": "order_created",
    "notification_type_display": "Buyurtma yaratildi",
    "message": "Buyurtma #123 muvaffaqiyatli yaratildi...",
    "status": "sent",
    "status_display": "Yuborildi",
    "sent_at": "2024-01-15T10:30:05Z",
    "created_at": "2024-01-15T10:30:00Z",
    "metadata": {
        "order_id": 123
    }
}
```

#### 3. O'qilmagan bildirishnomalar soni
```http
GET /api/v1/notifications/notifications/unread-count/
Authorization: Bearer <token>

Response 200:
{
    "unread_count": 5
}
```

### Template API (Admin only)

```http
GET /api/v1/notifications/templates/
POST /api/v1/notifications/templates/
GET /api/v1/notifications/templates/{id}/
PUT /api/v1/notifications/templates/{id}/
DELETE /api/v1/notifications/templates/{id}/
```

## 🔄 Signals (Avtomatik bildirishnomalar)

Signals orqali avtomatik bildirishnoma yuborish:

```python
# orders/models.py da Order holati o'zgarganda
@receiver(post_save, sender=Order)
def order_status_changed(sender, instance, created, **kwargs):
    # Avtomatik bildirishnoma yuboriladi
    
# prescriptions/models.py da Prescription holati o'zgarganda
@receiver(post_save, sender=Prescription)
def prescription_status_changed(sender, instance, created, **kwargs):
    # Avtomatik bildirishnoma yuboriladi
```

## ⚙️ Sozlamalar

`settings.py` da quyidagi sozlamalar kerak:

```python
# SMS Provider
DEVSMS_TOKEN = "your_devsms_token"
DEVSMS_URL = "https://devsms.uz/api/send_sms.php"

# Debug mode (SMS yuborilmaydi, faqat log)
SMS_DEBUG = True  # Production da False
```

## 🧪 Testlar

```bash
# Barcha testlarni ishga tushirish
pytest notifications/tests.py -v

# Faqat OTP testlari
pytest notifications/tests.py::TestOTPService -v

# Faqat Notification testlari
pytest notifications/tests.py::TestNotificationService -v
```

## 📝 Admin Panel

Admin panelda quyidagilar bor:
- ✅ Barcha bildirishnomalarni ko'rish
- ✅ OTP kodlarni kuzatish
- ✅ Shablonlarni boshqarish
- ✅ Filtr va qidiruv
- ✅ Rangli status badgelar

## 🔒 Xavfsizlik

1. **Rate Limiting**: 1 daqiqada 1 marta OTP
2. **OTP Muddati**: 120 soniya
3. **Urinish Cheklovi**: 3 marta
4. **Bir martalik**: Har bir OTP faqat 1 marta ishlatiladi
5. **Privacy**: Foydalanuvchi faqat o'z bildirishnomalarini ko'radi

## 📈 Kelajakdagi Yaxshilanishlar

- [ ] Celery integration (async SMS yuborish)
- [ ] Email bildirishnomalar
- [ ] Push notifications (FCM)
- [ ] WebSocket real-time bildirishnomalar
- [ ] Bildirishnoma sozlamalari (user preferences)
- [ ] SMS templates admin UI
- [ ] Bildirishnomalar statistikasi
- [ ] A/B testing uchun template variants

## 🤝 Integratsiya

Boshqa applar bilan integratsiya:

```python
# orders/services.py
from notifications.services import NotificationService

def create_order(user, cart):
    order = Order.objects.create(...)
    
    # Bildirishnoma avtomatik yuboriladi (signal orqali)
    # Yoki qo'lda:
    notification_service = NotificationService()
    notification_service.notify_order_created(order)
```

## 📞 Support

Savollar yoki muammolar bo'lsa:
- Admin: dorixona@example.com
- Developer: dev@example.com

---

**Version**: 1.0.0  
**Last Updated**: 2024-01-15  
**Status**: ✅ Production Ready
