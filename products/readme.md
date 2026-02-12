# 📦 PRODUCTS APP — Onlayn Dorixona Loyihasi

## Umumiy ma’lumot

**Products app** — Onlayn Dorixona web loyihasining asosiy modullaridan biri bo‘lib, dorilar (mahsulotlar), ularning kategoriyalari va muqobil variantlarini boshqarish uchun mo‘ljallangan.

Ushbu modul:
- dorilar katalogini yuritadi
- qidiruv va filtrlashni ta’minlaydi
- retsept talab qilinadigan dorilarni belgilaydi
- buyurtma jarayoniga tayyor ma’lumotlar uzatadi

---

## 🎯 App maqsadi

- Dorixonadagi barcha dorilarni yagona tizimda saqlash
- Mijozlarga dorilarni qulay topish imkonini berish
- Buyurtmalar bekor bo‘lishini kamaytirish (muqobil dorilar orqali)
- Operator va admin ishini soddalashtirish

---

## 🧩 App tarkibi

products/
├── models.py
├── serializers.py
├── views.py
├── permissions.py
├── urls.py
└── admin.py


---

## 1️⃣ Kategoriyalar tizimi (Categories)

### Category modeli

Har bir dori muayyan kategoriya ostida joylashadi.

**Maydonlar:**
- `id`
- `name` — kategoriya nomi
- `slug` — URL uchun
- `description` — qisqa izoh
- `is_active` — kategoriya faolligi
- `created_at`

### Funksionallik
- Kategoriyalar ro‘yxatini ko‘rish (mijoz)
- Kategoriya bo‘yicha dorilarni filtrlash
- Kategoriya qo‘shish / tahrirlash / o‘chirish (admin)

---

## 2️⃣ Dorilar tizimi (Products / Medicines)

### Product modeli

Dorixonadagi har bir dori uchun asosiy ma’lumotlar saqlanadi.

**Maydonlar:**
- `id`
- `name` — dori nomi
- `price` — narxi
- `description` — to‘liq tavsif
- `usage` — nima uchun ishlatiladi
- `quantity` — ombordagi miqdor
- `category` — Category bilan bog‘lanish
- `requires_prescription` — retsept talab qilinadimi
- `active_ingredient` — faol modda
- `manufacturer` — ishlab chiqaruvchi
- `image` — dori rasmi
- `order_count` — nechta buyurtma qilingan
- `is_active` — sotuvda mavjudligi
- `created_at`
- `updated_at`

---

## 3️⃣ Mijoz uchun funksionallik

### Dorilarni ko‘rish
- Dorilar ro‘yxati
- Kategoriya bo‘yicha saralash
- Narx bo‘yicha filter:
  - arzon → qimmat
  - qimmat → arzon
- Retsept talab qilinadigan dorilarni ajratish

### Qidiruv
- Dori nomi bo‘yicha
- Faol modda bo‘yicha
- Ishlab chiqaruvchi bo‘yicha

---

## 4️⃣ Dori sahifasi (Product detail)

Har bir dori sahifasida:
- Dori nomi
- Narxi
- Tavsifi
- Qo‘llanilishi
- Retsept talab qilinadimi
- Mavjud miqdori
- Ishlab chiqaruvchi
- Muqobil dorilar (agar mavjud bo‘lsa)

---

## 5️⃣ Aqlli muqobil dorilar tizimi

### Ishlash shartlari
- Agar dori omborda mavjud bo‘lmasa (`quantity = 0`)
- Yoki foydalanuvchi muqobil variant izlayotgan bo‘lsa

### Ishlash mexanizmi
- Bir xil `active_ingredient` ga ega dorilar aniqlanadi
- Quyidagi tartibda tavsiya qilinadi:
  1. Arzonroq variantlar
  2. Boshqa ishlab chiqaruvchilar
  3. Omborda mavjud dorilar

Bu funksiya:
- mijozga yordam beradi
- buyurtmalar bekor bo‘lishini kamaytiradi
- savdo hajmini oshiradi

---

## 6️⃣ Retsept bilan bog‘liq logika

Products app darajasida:
- faqat `requires_prescription` belgilanadi

Agar dori retsept talab qilsa:
- buyurtma jarayonida `prescriptions` app ishga tushadi
- retsept operator tomonidan tekshiriladi

---

## 7️⃣ Operator va Admin funksionalligi

### Admin:
- Dori qo‘shish
- Dorini tahrirlash
- Narxni o‘zgartirish
- Ombor miqdorini yangilash
- Dorini faollashtirish / o‘chirish

### Operator:
- Dorilar mavjudligini ko‘rish
- Kam qolgan dorilarni aniqlash

---

## 8️⃣ API endpointlar (DRF)

```http
GET     /api/categories/
GET     /api/products/
GET     /api/products/{id}/
GET     /api/products/search/?q=paracetamol
GET     /api/products/alternatives/{id}/

POST    /api/products/        # admin
PUT     /api/products/{id}/   # admin
DELETE  /api/products/{id}/   # admin

9️⃣ Boshqa applar bilan bog‘lanish
App nomi	Bog‘lanish
users	foydalanuvchi rollari
orders	buyurtma jarayoni
prescriptions	retseptli dorilar
notifications	ogohlantirishlar
admin	boshqaruv
🔚 Xulosa

Products app:

Onlayn Dorixona loyihasining asosiy qismi

Keyingi orders, prescriptions, delivery app’lar uchun tayanch bo‘lib xizmat qiladi

To‘g‘ri arxitektura bilan yozilganda tizim barqaror va kengaytiriladigan bo‘ladi