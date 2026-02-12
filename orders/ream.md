📦 ORDERS APP — UMUMIY MONITORING & TEXNIK XULOSA

(Real Production / Senior+ daraja)

🎯 ORDERS APP MAQSADI

Orders app — Onlayn Dorixona platformasining yuragi bo‘lib, quyidagi jarayonlarni boshqaradi:

savatcha (cart)

buyurtma yaratish

buyurtma hayot sikli (statuslar)

mahsulotlar bilan bog‘lanish

stock (ombor) nazorati

operator va kuryer workflow

frontend va boshqa applar uchun markaziy API

👉 Payments, Delivery, Notifications to‘liq Orders’ga tayangan holda ishlaydi.

✅ 1. QILIB BO‘LINGAN ISHLAR (HOZIRGI HOLAT)
🔹 MODELS (100% TAYYOR)

Orders app’da quyidagi modellar mavjud:

Cart

CartItem

Order

OrderItem

Xususiyatlari:

price freeze (OrderItem.price)

computed fields (total_price, items_count)

admin + API uchun xavfsiz

real biznesga mos

📊 Holati: Production ready (10/10)

🔹 SERVICES — BUSINESS LOGIC (100% TAYYOR)

Butun biznes mantiq faqat service layer’da joylashgan:

OrderCreationService

cart → order aylantirish

atomic transaction

stock tekshirish va kamaytirish

retsept flag aniqlash

OrderStatusService

qat’iy status flow

OrderCancelService

bekor qilish + stock rollback

Muhim:

views va serializers’da biznes logika YO‘Q

race condition oldi olingan (F() expressions)

📊 Holati: Production ready (10/10)

🔹 SERIALIZERS (100% TAYYOR)

Thin serializers

Frontend-friendly JSON

Computed fieldlar ochiq

Service layer’ga tayangan

📊 Holati: Production ready (10/10)

🔹 VIEWS (100% TAYYOR)

ModelViewSet (industry standard)

Pagination + edge-case handling

Custom exception mapping

Clean REST API

API imkoniyatlari:

cart ko‘rish

order yaratish

order list/detail

cancel

status change

📊 Holati: Production ready (10/10)

🔹 PERMISSIONS (100% TAYYOR)

To‘liq role-based security:

customer

operator

courier

admin

Action-level va object-level permission mavjud.

📊 Holati: Production ready (10/10)

🔹 URLS (100% TAYYOR)

DRF router-based

RESTful

frontend uchun barqaror

📊 Holati: Production ready (10/10)

🔹 ADMIN PANEL (100% TAYYOR)

operator-friendly

inline OrderItem’lar

rangli status badge

xavfsiz (readonly joylar)

📊 Holati: Production ready (10/10)

🟢 HOZIR ORDERS APP NIMALARNI QILA OLADI?
👤 MIJOZ

savatchani ko‘radi

buyurtma beradi

buyurtmalarini ko‘radi

bekor qiladi (ruxsat doirasida)

🧑‍⚕️ OPERATOR

buyurtmalarni ko‘radi

statuslarni boshqaradi

tayyorlash jarayonini yuritadi

🚚 KURYER

faqat o‘ziga biriktirilgan orderlarni ko‘radi

yetkazish statuslarini belgilaydi

👑 ADMIN

barcha jarayon ustidan nazorat

admin panel orqali monitoring

🔗 ORDERS APP ↔ BOSHQA APPLAR INTEGRATSIYASI
👥 USERS APP (ULANGAN)

user

role

authentication

👉 Orders Users app’ga to‘liq tayangan

💊 PRODUCTS APP (ULANGAN)

product

price

stock

👉 Stock kamaytirish / qaytarish Orders service’da

🧾 PRESCRIPTIONS APP (QISMAN)

needs_prescription flag bor

order oqimi to‘xtatilishi mumkin

👉 Keyinchalik: prescription tasdiqlangandan keyin order davom ettiriladi

💳 PAYMENTS APP (KEYINGI BOSQICH)

Orders tomonda tayyor joylar:

payment_status

order lifecycle

Payments app’da qo‘shiladi:

PaymentTransaction modeli

external provider (Click, Payme)

webhook

idempotency

🚚 DELIVERY APP (KEYINGI BOSQICH)

Orders tomonda tayyor:

courier field

status flow

Delivery app’da qo‘shiladi:

courier assignment

route / tracking

delivery confirmation

🔔 NOTIFICATIONS APP (KEYINGI BOSQICH)

Orders event’lari tayyor:

order created

status changed

delivered

Notifications app’da:

SMS

email

push