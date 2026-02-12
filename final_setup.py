#!/usr/bin/env python
"""
FINAL SETUP - One script to fix everything!
Run: python manage.py shell < final_setup.py
"""

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dorixona.settings')

import django
django.setup()

from django.conf import settings
from notifications.models import NotificationTemplate, NotificationType, NotificationChannel

print("\n" + "="*70)
print("🚀 DORIXONA - FINAL SETUP")
print("="*70 + "\n")

# 1. Check SMS Settings
print("1️⃣ SMS SETTINGS CHECK:")
print(f"   SMS_DEBUG: {settings.SMS_DEBUG}")
print(f"   DEVSMS_TOKEN: {settings.DEVSMS_TOKEN[:20]}..." if settings.DEVSMS_TOKEN else "   DEVSMS_TOKEN: NOT SET")
print(f"   DEVSMS_URL: {settings.DEVSMS_URL}\n")

if settings.SMS_DEBUG:
    print("   ✅ DEBUG MODE ENABLED - SMS will NOT be sent to DevSMS")
    print("   ✅ SMS will be logged only\n")
else:
    print("   ⚠️  DEBUG MODE DISABLED - Real SMS will be sent\n")

# 2. Create Notification Templates
print("2️⃣ CREATING NOTIFICATION TEMPLATES:")

templates = [
    {
        "notification_type": NotificationType.OTP,
        "channel": NotificationChannel.SMS,
        "template": "Sizning tasdiqlash kodingiz: {code}. Bu kod 2 daqiqada amal qiladi.",
        "description": "OTP SMS"
    },
    {
        "notification_type": NotificationType.ORDER_CREATED,
        "channel": NotificationChannel.SYSTEM,
        "template": "Buyurtmangiz #{order_id} qabul qilindi. Jami: {total_price} so'm",
        "description": "Order created notification"
    },
    {
        "notification_type": NotificationType.ORDER_PAID,
        "channel": NotificationChannel.SYSTEM,
        "template": "Buyurtma #{order_id} uchun to'lov qabul qilindi.",
        "description": "Order paid notification"
    },
]

created = 0
for t in templates:
    try:
        template, was_created = NotificationTemplate.objects.get_or_create(
            notification_type=t["notification_type"],
            channel=t["channel"],
            defaults={
                "template": t["template"],
                "description": t["description"],
                "is_active": True,
            }
        )
        if was_created:
            print(f"   ✅ Created: {t['description']}")
            created += 1
        else:
            print(f"   ⚠️  Exists: {t['description']}")
    except Exception as e:
        print(f"   ❌ Error: {t['description']} - {e}")

print(f"\n   Total created: {created}\n")

# 3. Test SMS Provider
print("3️⃣ SMS PROVIDER TEST:")

from notifications.services import DevSMSProvider

provider = DevSMSProvider()
try:
    result = provider.send("+998901234567", "Test message")
    print(f"   ✅ SMS Provider working")
    print(f"   Response: {result}\n")
except Exception as e:
    print(f"   ⚠️  SMS Provider error (expected in DEBUG mode): {e}\n")

# 4. Summary
print("="*70)
print("✅ SETUP COMPLETE!")
print("="*70)
print("\nYou can now:")
print("  1. Run: python manage.py runserver")
print("  2. Go to: http://localhost:3000/register")
print("  3. Register with:")
print("     - Telefon: +998901234567")
print("     - Parol: password123")
print("  4. Get OTP from Django Shell:")
print("     >>> from users.models import SMSVerification")
print("     >>> SMSVerification.objects.last().code")
print("\n✅ READY TO TEST!\n")
