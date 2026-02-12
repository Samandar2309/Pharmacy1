📄 prescriptions/README.md
# 📋 PRESCRIPTIONS APP  
(Onlayn Dorixona Web Platformasi)

## 1. Umumiy maqsad

`prescriptions` app — **retsept talab qilinadigan dorilarni qonuniy va xavfsiz boshqarish**
uchun mo‘ljallangan modul.

Ushbu app quyidagilarni ta’minlaydi:

- Retsept rasmlarini yuklash
- Retseptni operator/admin tomonidan tekshirish
- Retsept asosida buyurtmani davom ettirish yoki to‘xtatish
- Retsept talab qilinmaydigan dorilar bilan mos ishlash
- Real dorixona ish jarayoniga mos UX va biznes qoidalari

---

## 2. Qaysi holatda prescription ishlaydi?

### ❌ Hamma dori uchun emas

`products.Product` modelida:

```python
requires_prescription = models.BooleanField(default=False)

Misollar:
Dori	requires_prescription
Trimol	❌ Yo‘q
Paracetamol	❌ Yo‘q
Amoxicillin	✅ Ha
Ceftriaxone	✅ Ha
3. Asosiy biznes qoidalari
3.1 Retsept talab qilinmaydigan dori

Buyurtma to‘g‘ridan-to‘g‘ri beriladi

Prescription app ishlamaydi

3.2 Retsept talab qilinadigan dori

Retsept rasmi majburiy

Operator/Admin tasdiqlamaguncha buyurtma davom etmaydi

3.3 Aralash savatcha (retseptli + retseptsiz)

Tizim mijozga tanlov beradi

Agar mijoz retseptsiz dorilarni alohida buyurtma qilmoqchi bo‘lsa:

retseptli dorilar avtomatik chiqarib tashlanadi

Qonuniy nazorat backend tomonidan amalga oshiriladi

4. App ichidagi modelllar
4.1 Prescription

Retseptni tekshirish jarayoni.

Statuslar:

PENDING – tekshiruvda

APPROVED – tasdiqlangan

REJECTED – rad etilgan

State machine qoidasi:

PENDING → APPROVED
PENDING → REJECTED


Qayta o‘zgartirish mumkin emas.

4.2 PrescriptionImage

Bitta retseptga bir nechta rasm

Maksimal: 5 ta

Formatlar: jpg, jpeg, png

Fayl hajmi cheklangan

Parallel upload’da race-condition’dan himoyalangan

4.3 PrescriptionItem

Retseptda ko‘rsatilgan dorilar

Audit va qonuniy nazorat uchun

Prescription + Product kombinatsiyasi unikal

5. API endpointlar
5.1 Retsept yaratish (mijoz)
POST /api/v7/prescriptions/


Talablar:

Auth required

Kamida 1 ta rasm

Maksimal 5 ta rasm

Natija:

201 Created

5.2 Retseptlar ro‘yxati
GET /api/v7/prescriptions/


Mijoz → faqat o‘zini

Operator/Admin → barchasini

5.3 Kutilayotgan retseptlar (operator/admin)
GET /api/v7/prescriptions/pending/

5.4 Retseptni tasdiqlash
POST /api/v7/prescriptions/{id}/approve/


Faqat Operator/Admin

Faqat PENDING holatda

5.5 Retseptni rad etish
POST /api/v7/prescriptions/{id}/reject/


Body:

{
  "rad_sababi": "Sabab majburiy"
}

6. Permissionlar
Rol	Huquqlar
Mijoz	Retsept yaratish, o‘zini ko‘rish
Operator	Pending ko‘rish, approve/reject
Admin	To‘liq nazorat
7. Admin panel funksionalligi

Retseptlar ro‘yxati

Rasm preview

Dorilar ro‘yxati

Status badge

Bulk approve / reject

Sabab bilan rad etish

HTML template ishlatilmaydi

Django 5.x bilan to‘liq mos

8. Services layer

Biznes logika model va view’dan ajratilgan:

create_prescription

approve_prescription

reject_prescription

Bu:

test yozishni osonlashtiradi

kodni barqaror qiladi

qayta foydalanish imkonini beradi

9. Signal logikasi

Retsept yaratilganda

Retsept holati o‘zgarganda

Kelajakda:

notification

audit log

analytics

uchun tayyor.

10. Testlar

App to‘liq testlangan:

pytest prescriptions/


Testlar qamrovi:

API

Permission

Service layer

Edge-case’lar

11. Nima uchun bu arxitektura tanlandi?

✅ Qonuniy talablar

✅ Real dorixona ish jarayoni

✅ Frontend + Backend ajratilgan

✅ Kengaytiriladigan

✅ Production ready

12. Kelajakda kengaytirish

OCR orqali retseptni avtomatik tekshirish

Audit log modeli

Notification (SMS/Telegram)

Statistik tahlil

13. Xulosa

prescriptions app:

MVP emas

test bilan yopilgan

real dorixona topshirishga tayyor

qonuniy va texnik jihatdan to‘liq