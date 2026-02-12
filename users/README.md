## 📲 SMS YUBORISHNI ULASH (ESKIZ.UZ)

Ushbu loyiha SMS (OTP) yuborish uchun **Eskiz.uz SMS API** bilan integratsiyaga tayyor.
Hozirda Eskiz’da **sender sotib olinmagan** bo‘lishi mumkin, shuning uchun tizim **DEBUG rejim**da ishlaydi.

Quyida **SMS yuborishni ulash uchun aniq ketma-ketlik** keltirilgan.

---

### 1️⃣ Eskiz.uz’dan OLINADIGAN MA’LUMOTLAR

Eskiz.uz’da ro‘yxatdan o‘tgandan so‘ng quyidagi ma’lumotlar kerak bo‘ladi:

| Nomi | Tavsifi |
|----|----|
| `ESKIZ_EMAIL` | Eskiz akkaunt emaili |
| `ESKIZ_PASSWORD` | Eskiz akkaunt paroli |
| `ESKIZ_SENDER` | Eskiz’dan sotib olinadigan sender (masalan: `4546`) |

📌 **Eslatma**  
Sender sotib olinmaguncha SMS real yuborilmaydi.

---

### 2️⃣ `.env` FAYLGA YOZISH (MAJBURIY)

Loyihaning **root papkasi**da `.env` fayl yarating yoki tahrirlang:

```env
ESKIZ_EMAIL=eskiz_account_email
ESKIZ_PASSWORD=eskiz_account_password
ESKIZ_SENDER=4546
SMS_DEBUG=True
