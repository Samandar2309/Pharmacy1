🛒 ORDERS APP — FUNKSIONAL TEXNIK TOPSHIRIQ
🎯 ORDERS APP NING ASOSIY VAZIFASI

Orders app:

mijoz tanlagan dorilarni buyurtmaga aylantiradi

buyurtma hayotiy siklini boshlanishidan oxirigacha boshqaradi

operator va kuryer ishini bir zanjirga bog‘laydi

boshqa app’lar (users, products, delivery, prescriptions) bilan markaziy bog‘lovchi bo‘lib ishlaydi

1️⃣ SAVATCHA (CART) FUNKSIONALLIGI
Orders app nimalarni qila oladi:

Mijoz dorilarni vaqtincha savatchaga qo‘sha oladi

Har bir dori uchun:

miqdor belgilanadi

narx ko‘rinadi

Savatchada:

umumiy summa hisoblanadi

dori o‘chiriladi

miqdor o‘zgartiriladi

🔹 Savatcha order yaratilmaguncha vaqtinchalik holatda turadi
🔹 Buyurtma tasdiqlanganda savatcha → Order ga aylanadi

2️⃣ BUYURTMA YARATISH (CHECKOUT)
Orders app nima qiladi:

Savatchadagi dorilar asosida buyurtma yaratadi

Mijozdan quyidagilar olinadi:

yetkazib berish manzili

izoh (ixtiyoriy)

Har bir dori uchun:

buyurtma paytidagi narx saqlanadi

Buyurtma unique ID bilan yaratiladi

📌 Natija:

Buyurtma statusi: “qabul qilindi”

Buyurtma tarixga tushadi

3️⃣ BUYURTMA STATUSLARINI BOSHQARISH

Orders app butun jarayonni statuslar orqali boshqaradi.

Statuslar va ma’nosi:
Status	Kim o‘zgartiradi	Maqsadi
qabul qilindi	tizim	buyurtma yaratildi
tayyorlanmoqda	operator	dorilar yig‘ilmoqda
kuryerga tayyor	operator	topshirishga tayyor
yetkazilmoqda	kuryer	yo‘lda
yetkazildi	kuryer	yakunlandi
bekor qilindi	admin/operator	muammo bo‘lsa

❗ Statuslar o‘zboshimchalik bilan o‘zgarmaydi
❗ Faqat ruxsat berilgan ketma-ketlik bo‘ladi

4️⃣ MIJOZ UCHUN FUNKSIONALLIK

Mijoz:

faqat o‘z buyurtmalarini ko‘ra oladi

buyurtma holatini real vaqtda kuzatadi

buyurtma tarkibini ko‘radi:

dorilar

miqdor

narx

umumiy summa

🚫 Mijoz:

statusni o‘zgartira olmaydi

boshqa buyurtmalarni ko‘ra olmaydi

5️⃣ OPERATOR UCHUN FUNKSIONALLIK

Operator:

yangi buyurtmalar ro‘yxatini ko‘radi

buyurtmani ochib:

dorilar ro‘yxatini ko‘radi

retsept talab qilinadigan dorilarni aniqlaydi

buyurtma statusini o‘zgartiradi:

qabul qilindi → tayyorlanmoqda

tayyorlanmoqda → kuryerga tayyor

buyurtmani kuryerga topshiradi

6️⃣ KURYER UCHUN FUNKSIONALLIK

Kuryer:

faqat o‘ziga biriktirilgan buyurtmalarni ko‘radi

yetkazib berish manzilini ko‘radi

statusni o‘zgartiradi:

kuryerga tayyor → yetkazilmoqda

yetkazilmoqda → yetkazildi

7️⃣ ADMIN UCHUN FUNKSIONALLIK

Admin:

barcha buyurtmalarni ko‘radi

istalgan buyurtmani tekshiradi

zarur bo‘lsa:

bekor qiladi

qayta yo‘naltiradi

statistik ma’lumotlarni ko‘rishga tayyor (keyin)

8️⃣ BOSHQA APP’LAR BILAN ALOQA

Orders app:

🔗 users app

foydalanuvchi roli

JWT auth

owner tekshiruvi

🔗 products app

narx

mavjud miqdor

retsept talabi

🔗 prescriptions app

retseptni tekshirish

tasdiqlanmagan dori → buyurtmaga o‘tmaydi

🔗 delivery app

kuryer biriktirish

yetkazib berish holati

9️⃣ NIMALAR YO‘Q (HOZIRCHA)

❌ To‘lov integratsiyasi
❌ Cashback / bonus
❌ Promo kodlar
❌ Qayta buyurtma (reorder)

(Bular keyingi bosqichlar)

🧊 FUNKSIONALLIK MUZLATILDI (FREEZE POINT)

Agar sen ha desang, biz quyidagilarni qabul qilamiz:

✔ Orders app faqat buyurtma logikasi
✔ Savatcha → Order → Status flow
✔ Role-based boshqaruv
✔ To‘lovsiz, lekin tayyor struktura