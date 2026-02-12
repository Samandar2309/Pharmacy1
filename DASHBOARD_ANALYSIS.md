# Dashboard app tahlili va integratsiya kamchiliklari

Sana: 12.02.2026

## 1) Qamrov va manbalar

Ushbu tahlil dashboard appning hozirgi holatini, boshqa applar bilan ulanishdagi muammolarni va umumiy tizim funksionalligini qamrab oladi.

Asosiy manbalar:
- `dashboard/models.py`, `dashboard/services.py`, `dashboard/signals.py`, `dashboard/views.py`, `dashboard/serializers.py`, `dashboard/permissions.py`, `dashboard/urls.py`, `dashboard/tests.py`
- `orders/models.py`, `orders/services.py`
- `delivery/models.py`
- `prescriptions/models.py`
- `products/models.py`
- `users/models.py`
- `notifications/models.py`, `notifications/services.py`
- `SYSTEM_INTEGRATION_ANALYSIS.md`, `SYSTEM_SUMMARY_AND_RECOMMENDATIONS.md`, `PROJECT_COMPREHENSIVE_ANALYSIS.md`

Izoh: tizim bo'yicha oldingi hujjatlarda dashboard app "bo'sh" deb yozilgan, lekin amalda `dashboard/` ichida model, servis, signal va APIlar bor. Shu sababli, hujjatlardagi holat bilan kod holati orasida tafovut mavjud.

## 2) Dashboard appning qisqa tavsifi

Dashboard app vazifalari:
- Kunlik agregatsiya (snapshot) statistikasi: `DailyStats` (`dashboard/models.py`).
- Mahsulot performance: `ProductPerformance`.
- Kuryer performance: `CourierPerformance`.
- Monitoring va xatolik loglari: `SystemHealthLog`.
- Admin uchun API: overview, daily stats, top products, top couriers, system health log (`dashboard/views.py`, `dashboard/urls.py`).

Ishlash tamoyili:
- Statistikalar signal va servislar orqali yangilanadi (`dashboard/signals.py`, `dashboard/services.py`).
- Admin-only ruxsatlar (`dashboard/permissions.py`).

## 3) Dashboard va boshqa applar integratsiya nuqtalari

Quyidagi bog'lanishlar mavjud:

1) Users bilan
- `DailyStats` orqali jami user/operator/courier soni hisoblanadi (`dashboard/services.py`, `users/models.py`).

2) Orders bilan
- Order yaratilganda va status o'zgarganda kunlik statistikalar va revenue yangilanadi (`dashboard/services.py`, `dashboard/signals.py`, `orders/models.py`).
- `ProductPerformance` order itemlar orqali hisoblanadi (`dashboard/services.py`, `orders/models.py`).

3) Products bilan
- `ProductPerformance` `products.Product` ga FK orqali ulanadi (`dashboard/models.py`, `products/models.py`).

4) Delivery bilan
- `CourierPerformance` `delivery.Delivery` statuslari orqali yangilanadi (`dashboard/signals.py`, `delivery/models.py`).

5) Prescriptions bilan
- Kunlik statistikalar retsept statuslari orqali yangilanadi (`dashboard/services.py`, `dashboard/signals.py`, `prescriptions/models.py`).

6) Notifications bilan
- Dashboard `SystemHealthLog` o'zining log modeliga yozadi, notifications to'g'ridan-to'g'ri ulanish yo'q (`dashboard/services.py`, `notifications/models.py`).

## 4) Asosiy integratsiya muammolari va xatoliklar

### 4.1) Signal ulanishi kafolatlanmagan
- `dashboard/apps.py` da `ready()` yo'q, shuning uchun `dashboard/signals.py` import qilinmasa signal ishlamaydi.
- Natija: `DailyStats`, `ProductPerformance`, `CourierPerformance` yangilanmay qolishi mumkin.
- Fayllar: `dashboard/apps.py`, `dashboard/signals.py`.

### 4.2) Order modeli bilan mos kelmaslik (payment_status yo'q)
- `dashboard/services.py` va `dashboard/signals.py` `Order.payment_status` ga tayanadi.
- `orders/models.py` da `Order` modelida `payment_status` field yo'q.
- Natija: signal ishlaganda `AttributeError` bo'lishi va statistikalar to'xtashi mumkin.
- Fayllar: `dashboard/services.py`, `dashboard/signals.py`, `orders/models.py`.

### 4.3) Order status qiymatlari va oqim mosligi
- Dashboard `status == "delivered"` va `status == "cancelled"` ni tekshiradi.
- `orders.models.Order.Status` enumida `delivered` va `cancelled` mavjud, lekin `dashboard` statusni to'g'ridan-to'g'ri tekshiradi va FSM orqali o'tish kafolatini tekshirmaydi.
- Natija: status oqimi buzilganda statistika noto'g'ri hisoblanishi mumkin.
- Fayllar: `dashboard/services.py`, `dashboard/signals.py`, `orders/models.py`, `orders/services.py`.

### 4.4) Prescription status nomuvofiqligi
- `dashboard.services.recalculate_daily_stats()` `checking/approved/rejected` ga tayanadi.
- `prescriptions.models.Prescription.Status` `pending/approved/rejected`.
- Natija: `prescriptions_pending` noto'g'ri hisoblanadi.
- Fayllar: `dashboard/services.py`, `prescriptions/models.py`.

### 4.5) Courier performance faqat delivery statusiga bog'liq
- `CourierPerformance` faqat `Delivery.status == delivered` bo'lganda yangilanadi.
- Order status delivered bo'lsa-yu, delivery update bo'lmasa, kuryer statistikasi noto'g'ri qoladi.
- Fayllar: `dashboard/signals.py`, `delivery/models.py`, `orders/models.py`.

### 4.6) Serializer nomuvofiqligi (full_name)
- `CourierPerformanceSerializer` `courier.full_name` dan foydalanadi.
- `users.models.User` da `full_name` property yo'q.
- Natija: API response serializatsiyasi xatoga uchrashi mumkin.
- Fayllar: `dashboard/serializers.py`, `users/models.py`.

### 4.7) Testlar real modelga mos emas
- `dashboard/tests.py` da `Product` yaratishda `prescription_required` ishlatiladi.
- `products.models.Product` da `is_prescription_required` mavjud.
- Natija: testlar ishlamaydi.
- Fayllar: `dashboard/tests.py`, `products/models.py`.

### 4.8) Kod sifati muammosi (serializer ichidagi ortiqcha kod)
- `dashboard/serializers.py` ichida `courier_name = SerializerMethodField()` va `get_courier_name()` classdan tashqarida qolgan.
- Natija: ishlamaydigan va chalg'ituvchi kod bo'lagi.
- Fayl: `dashboard/serializers.py`.

## 5) Umumiy app funksionalligi (qisqa xarita)

- Users: telefon raqamli autentifikatsiya, rollar, OTP, soft delete (`users/models.py`).
- Products: kategoriya, aktiv modda, mahsulot, ombor, prescription flag (`products/models.py`).
- Orders: cart, order, order item, status history, checkout, stock boshqaruvi (`orders/models.py`, `orders/services.py`).
- Prescriptions: retseptlar va rasmlar, state machine, operator ko'rib chiqish (`prescriptions/models.py`).
- Delivery: yetkazib berish jarayoni, statuslar, courier assignment, tarix (`delivery/models.py`).
- Notifications: SMS va in-app bildirishnomalar, template, retry (`notifications/models.py`, `notifications/services.py`).
- Payments: hozircha bo'sh (`payments/models.py`).
- Dashboard: admin analitika, snapshot stats, performance, monitoring loglari (`dashboard/models.py`, `dashboard/views.py`).

## 6) Xavf va ta'sir bahosi

- Statistika ishonchliligi past: signal ishlamasligi yoki model mos kelmasligi sabab noto'g'ri KPIlar.
- Admin qarorlar sifati pasayadi: noto'g'ri top products/couriers va revenue ko'rsatkichlari.
- Monitoring loglar to'liq emas: real muammolar yashirin qolishi mumkin.

## 7) Tavsiyalar (kod o'zgartirmasdan)

1) Dashboard signal va servislarining haqiqiy modellarga mosligi bo'yicha qaror qabul qilish.
2) Order va Prescription status nomlarini yagona manbaga keltirish bo'yicha integratsiya rejasini ishlab chiqish.
3) Dashboard bilan Orders/Delivery/Prescriptions oqimini test scenariylar orqali tekshirish.
4) Oldingi hujjatlar va real kod holati orasidagi tafovutni hujjatlarda yangilash.

## 8) Qisqa xulosa

Dashboard app mavjud va asosiy statistik endpointlar ishlab turgan ko'rinadi. Biroq u Orders, Prescriptions va Delivery bilan bog'lanishda bir nechta muhim mos kelmasliklarga ega. Bu holat KPIlar va admin qarorlarini noto'g'ri qilish xavfini oshiradi. Tizim bo'yicha umumiy holat: asosiy oqimlar bor, lekin integratsiya nuqtalarida muammolar ko'p va dashboard uchun ular kritik hisoblanadi.
