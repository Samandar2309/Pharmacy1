# 👤 USERS APP — Onlayn Dorixona Web Platformasi

## 📌 Umumiy tavsif

`users` app — **Onlayn Dorixona Web Platformasi**ning asosiy va eng muhim moduli bo‘lib, foydalanuvchilarni ro‘yxatdan o‘tkazish, autentifikatsiya qilish, rollar orqali ajratish va xavfsizlikni ta’minlash uchun javob beradi.

Ushbu modul **production-ready** holatda yozilgan va frontend hamda boshqa backend modullar (`orders`, `products`, `delivery`) bilan to‘liq integratsiyaga tayyor.

---

## 🎯 USERS APP’NING ASOSIY MAQSADI

- Foydalanuvchilarni telefon raqam orqali ro‘yxatdan o‘tkazish
- SMS (OTP) orqali foydalanuvchini tasdiqlash
- JWT asosida login / logout mexanizmini ta’minlash
- Parolni tiklash imkoniyatini berish
- Foydalanuvchi profili bilan ishlash
- Rollar orqali tizimga kirishni cheklash
- Operator, kuryer va admin ishlarini ajratish
- Django admin orqali boshqaruvni ta’minlash
- API hujjatlarini avtomatik yaratish (Redoc)

---

## 👥 FOYDALANUVCHI ROLLARI

Tizimda quyidagi rollar mavjud:

| Rol | Tavsif |
|---|---|
| `customer` | Mijoz — dorilarni ko‘radi va buyurtma beradi |
| `operator` | Buyurtmalarni qabul qiladi va tayyorlaydi |
| `courier` | Buyurtmalarni yetkazib beradi |
| `admin` | Tizimni umumiy boshqaradi |
| `superadmin` | Django admin orqali to‘liq nazorat |

Rollar **custom permissions** orqali qat’iy tekshiriladi.

---

## 🔐 AUTENTIFIKATSIYA VA XAVFSIZLIK

### 🔹 Autentifikatsiya usuli
- JWT (access + refresh)
- SimpleJWT + token blacklist

### 🔹 Xavfsizlik choralar
- Telefon raqam qat’iy formatda (`+998XXXXXXXXX`)
- OTP 2 daqiqa amal qiladi
- OTP urinishlar soni cheklangan
- Ishlatilgan OTP qayta ishlatilmaydi
- Logout vaqtida refresh token blacklist’ga tushadi
- Role-based va object-level permissions

---

## 📝 RO‘YXATDAN O‘TISH (REGISTER)

### Endpoint
POST /api/v1/users/register/


### Request body
```json
{
  "phone_number": "+998XXXXXXXXX",
  "full_name": "Ism Familiya",
  "password": "StrongPassword123"
}
Jarayon
User yaratiladi (is_verified = false)

Eski OTP’lar bekor qilinadi

Yangi 4 xonali OTP SMS yuboriladi

📩 SMS ORQALI TASDIQLASH (VERIFY OTP)
Endpoint
POST /api/v1/users/verify/
Request body
{
  "phone_number": "+998XXXXXXXXX",
  "code": "1234"
}
Natija
User is_verified = true

JWT access va refresh tokenlar qaytariladi

User avtomatik tizimga kiritiladi

🔑 LOGIN
Endpoint
POST /api/v1/users/login/
Request body
{
  "phone_number": "+998XXXXXXXXX",
  "password": "StrongPassword123"
}
Natija
JWT tokenlar

User ma’lumotlari

🚪 LOGOUT
Endpoint
POST /api/v1/users/logout/
Request body
{
  "refresh": "REFRESH_TOKEN"
}
Natija
Refresh token blacklist’ga qo‘shiladi

Qayta ishlatib bo‘lmaydi

🔁 PAROLNI TIKLASH
Forgot password
POST /api/v1/users/password/forgot/
{
  "phone_number": "+998XXXXXXXXX"
}
➡ SMS orqali OTP yuboriladi

Reset password
POST /api/v1/users/password/reset/
{
  "phone_number": "+998XXXXXXXXX",
  "code": "1234",
  "new_password": "NewStrongPassword123"
}
👤 FOYDALANUVCHI PROFILI
Profilni ko‘rish
GET /api/v1/users/me/
Authorization: Bearer ACCESS_TOKEN
Profilni tahrirlash
PATCH /api/v1/users/me/
Authorization: Bearer ACCESS_TOKEN
{
  "first_name": "Ism",
  "last_name": "Familiya",
  "address": "Toshkent shahar..."
}
🛡 PERMISSIONS (RUXSATLAR)
Custom permission’lar orqali:

IsAdmin

IsOperator

IsCourier

IsCustomer

IsAdminOrOperator

IsOwner

ReadOnly

Misol:

permission_classes = [IsAuthenticated, IsOperator]
Noto‘g‘ri rol → 403 Forbidden

🧑‍💼 DJANGO ADMIN
Admin panel orqali:

Foydalanuvchilarni boshqarish

Rollarni o‘zgartirish

is_verified, is_active holatini nazorat qilish

SMSVerification (OTP) monitoring

JWT blacklist tokenlarni ko‘rish

Django admin faqat superadmin uchun mo‘ljallangan.

📄 API HUJJATLARI
Redoc
/api/redoc/
OpenAPI schema
/api/schema/
Redoc orqali barcha users endpointlari va autentifikatsiya talablari ko‘rinadi.

⚙️ TEXNOLOGIYALAR
Django 5.x

Django REST Framework

Custom User Model

Custom UserManager

SimpleJWT + Blacklist

drf-spectacular (OpenAPI)

SQLite (development)

PostgreSQL (production-ready)

✅ USERS APP NIMA ISHLARNI BAJARA OLADI?
✔ Telefon orqali ro‘yxatdan o‘tish
✔ SMS (OTP) orqali tasdiqlash
✔ JWT login / logout
✔ Parolni tiklash
✔ Foydalanuvchi profili
✔ Rollar orqali kirishni cheklash
✔ Operator / Kuryer / Admin ajratish
✔ Django admin boshqaruvi
✔ API hujjatlari

📊 HOZIRGI HOLAT
Users app: ~95% yakunlangan

Frontend integratsiya uchun tayyor

Production asosiga mos

Keyingi app’lar (orders, products, delivery) uchun mustahkam poydevor

