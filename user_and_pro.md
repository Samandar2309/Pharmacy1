🏥 Onlayn Dorixona Platformasi — Hozirgi holat (Users + Products)
🎯 Umumiy progress

Hozirda loyihaning 2 ta eng muhim yadro moduli to‘liq ishlab chiqildi:

✅ Users (Autentifikatsiya va foydalanuvchi boshqaruvi)
✅ Products (Dori katalogi va ombor tizimi)

Bu ikkisi:

👉 butun tizimning asosiy poydevori (foundation)

Orders / Payments / Delivery aynan shu ikkitasiga tayangan holda ishlaydi.

📊 Loyihaning umumiy tayyorlik darajasi

Agar to‘liq dorixona tizimini 100% deb olsak:

Modul	Holat
Users	✅ 100%
Products	✅ 100%
Orders	❌ 0%
Payments	❌ 0%
Delivery	❌ 0%

👉 Umumiy tayyorlik: ~50%

Lekin:
👉 eng murakkab va asosiy qismlar allaqachon bitgan

👤 USERS APP — Funksional imkoniyatlar
🎯 Vazifasi

Tizimdagi barcha foydalanuvchilarni:

ro‘yxatdan o‘tkazish

tasdiqlash

autentifikatsiya qilish

rollar orqali boshqarish

✅ Hozirda ishlaydigan funksiyalar
🔐 Autentifikatsiya

Telefon raqam orqali ro‘yxatdan o‘tish

SMS (OTP) tasdiqlash

JWT login (access + refresh)

Logout + token blacklist

Xavfsiz sessiya boshqaruvi

📱 Telefon validatsiyasi

+998 avtomatik qo‘shiladi

noto‘g‘ri formatlar bloklanadi

DB’da standart format saqlanadi

👉 production daraja

👤 Profil boshqaruvi

Profilni ko‘rish

Ism/familiya/manzilni yangilash

🔁 Parolni tiklash

Forgot password (SMS)

OTP orqali tasdiqlash

Yangi parol o‘rnatish

👥 Rollar tizimi

Tizim tayyor:

customer (mijoz)

operator

courier

admin

👉 keyingi app’lar shu rollarga asoslanadi

🔒 Xavfsizlik

JWT

Token blacklist

OTP

Password validation

Role permissions

🟢 Real hayotda Users app nima bera oladi?

Hozirning o‘zida:

👉 mijoz:

ro‘yxatdan o‘tadi

login qiladi

profilini boshqaradi

parolini tiklaydi

👉 admin/operator:

tizimga xavfsiz kiradi

Demak:

To‘liq ishlaydigan professional login tizimi mavjud
⭐ Users bahosi

👉 9.5 / 10 (production ready)

💊 PRODUCTS APP — Funksional imkoniyatlar
🎯 Vazifasi

Dorilarni:

kataloglash

qidirish

kategoriyalash

muqobil dorilar tavsiya qilish

omborni boshqarish

✅ Hozirda ishlaydigan funksiyalar
📂 Kategoriya tizimi

Kategoriyalar yaratish

Faol/no-faol

Ikonka

Frontend uchun API

💊 Dori modeli

Har bir dori:

nomi

tavsif

qo‘llanilishi

narx

ombordagi miqdor

ishlab chiqaruvchi

rasm

SKU/barcode

retsept talab qilinadimi

sotilgan soni

yaroqlilik muddati

👉 real dorixona darajasi

🔍 Qidiruv

nom bo‘yicha

ishlab chiqaruvchi bo‘yicha

faol modda bo‘yicha

🧪 Faol modda (Active Substance)

Many-to-many

ilmiy to‘g‘ri model

alternativalar uchun asos

🔁 Aqlli muqobil dorilar

Agar:

dori tugagan

yoki mijoz boshqa variant xohlasa

Tizim:

bir xil faol moddali dorilarni topadi

faqat mavjudlarini ko‘rsatadi

arzonini ustun qo‘yadi

👉 bu katta dorixonalarda ishlatiladigan real biznes funksiyasi

⚙️ Admin panel

dorilar qo‘shish/tahrirlash

filtrlash

qidiruv

stock monitoring

kam qolganini ko‘rsatish

🚀 Performance

pagination

select_related

prefetch_related

DB indexlar

👉 katta katalogga tayyor

🟢 Real hayotda Products app nima bera oladi?

Hozirning o‘zida:

👉 mijoz:

dorilarni ko‘radi

qidiradi

batafsil sahifasini ochadi

muqobilini ko‘radi

👉 admin:

omborni boshqaradi

Demak:

To‘liq ishlaydigan dorilar katalogi mavjud
⭐ Products bahosi

👉 9–9.5 / 10 (production ready)