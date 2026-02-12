# 📦 Products App — Onlayn Dorixona Loyihasi

## Umumiy tavsif

**Products app** — Onlayn Dorixona web platformasining asosiy modullaridan biri bo‘lib, dorilar katalogini professional va production darajada boshqarish uchun ishlab chiqilgan.

Ushbu modul:
- dorilar va kategoriyalarni boshqaradi
- aqlli muqobil dorilarni tavsiya qiladi
- frontend va mobil ilovalar uchun tayyor REST API taqdim etadi
- real dorixona biznes jarayonlariga moslashtirilgan

---

## ✅ Bajarilgan ishlar

Products app to‘liq ishlab chiqildi va quyidagi qismlar yakunlandi:

- `models.py` — professional va kengaytiriladigan arxitektura
- `serializers.py` — frontendga mos, xavfsiz JSON struktura
- `views.py` — ViewSet asosida, pagination va aqlli katalog bilan
- `permissions.py` — role-based (mijoz / operator / admin)
- `urls.py` — REST standartlarga mos router bilan
- `admin.py` — qulay va biznesga mos admin panel
- Swagger / OpenAPI hujjati (`/api/docs/`)

👉 **Backend tomondan Products app yakunlangan.**

---

## 🧩 Asosiy funksionalliklar

### 📂 Kategoriyalar (Categories)
- Kategoriya yaratish va boshqarish (admin)
- Faol / nofaol kategoriyalar
- Kategoriya uchun ikonka (rasm)
- Frontend uchun kategoriya ro‘yxati API

---

### 💊 Dorilar (Products)
Har bir dori uchun:
- nomi
- tavsifi
- qo‘llanilishi
- narxi
- ombordagi miqdori
- yaroqlilik muddati
- ishlab chiqaruvchi
- SKU / barcode
- retsept talab qilinadimi
- sotuv holati (active / inactive)

---

### 🧪 Faol moddalar (Active Substances)
- Faol moddalar alohida model sifatida ajratilgan
- Bitta dori bir nechta faol moddaga ega bo‘lishi mumkin (Many-to-Many)
- Muqobil dorilarni aniqlash uchun asos

---

### 🔁 Aqlli muqobil dorilar tizimi
Agar dori mavjud bo‘lmasa yoki foydalanuvchi alternativ izlayotgan bo‘lsa:
- bir xil faol moddalarga ega dorilar topiladi
- faqat omborda mavjud dorilar ko‘rsatiladi
- eng arzon variantlar ustuvor chiqadi

Bu funksiya:
- buyurtmalar bekor bo‘lishini kamaytiradi
- foydalanuvchi tajribasini yaxshilaydi
- savdo hajmini oshiradi

---

### 🔐 Ruxsatlar (Permissions)
- **Mijoz** → faqat ko‘rish (GET)
- **Operator** → dorilarni qo‘shish va tahrirlash
- **Admin** → to‘liq boshqaruv

---

### 📑 Pagination va Performance
- Global pagination yoqilgan
- Katta dorilar bazasi uchun optimizatsiya qilingan
- `select_related` va `prefetch_related` ishlatilgan

---

### ⚙️ Admin Panel
- Dorilarni qulay boshqarish
- Kam qolgan dorilar vizual ko‘rinishda ajratiladi
- Filtrlash, qidiruv, tartiblash
- Many-to-Many faol moddalarni qulay tanlash
- Excel import/export qo‘shishga tayyor

---

## 🔗 API Endpointlar

```http
GET  /api/products/categories/
GET  /api/products/products/
GET  /api/products/products/{id}/
GET  /api/products/products/{id}/alternatives/

POST   /api/products/products/        (admin/operator)
PUT    /api/products/products/{id}/   (admin/operator)
PATCH  /api/products/products/{id}/   (admin/operator)
DELETE /api/products/products/{id}/   (admin)
