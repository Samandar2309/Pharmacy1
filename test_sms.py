#!/usr/bin/env python
"""
Quick SMS Test Script
Run: python manage.py shell < test_sms.py
"""

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dorixona.settings')

import django
django.setup()

from django.conf import settings
from notifications.models import NotificationTemplate, NotificationType, NotificationChannel
from notifications.services import NotificationService
from users.models import User

print("\n" + "="*70)
print("📱 SMS TEST SCRIPT")
print("="*70 + "\n")

# 1. Check Settings
print("1️⃣ SETTINGS CHECK:")
print(f"   DEBUG: {settings.DEBUG}")
print(f"   SMS_DEBUG: {settings.SMS_DEBUG}")
print(f"   DEVSMS_TOKEN: {settings.DEVSMS_TOKEN[:20] if settings.DEVSMS_TOKEN else 'NOT SET'}...")
print()

# 2. Create Templates
print("2️⃣ CREATE TEMPLATES:")

template_data = [
    {
        "type": NotificationType.OTP,
        "channel": NotificationChannel.SMS,
        "template_text": "Sizning tasdiqlash kodingiz: {code}",
        "desc": "OTP SMS"
    },
    {
        "type": NotificationType.OTP,
        "channel": NotificationChannel.SYSTEM,
        "template_text": "OTP: {code}",
        "desc": "OTP System"
    },
]

for t in template_data:
    template, created = NotificationTemplate.objects.get_or_create(
        notification_type=t["type"],
        channel=t["channel"],
        defaults={
            "template_text": t["template_text"],
            "is_active": True
        }
    )
    status = "✅ Created" if created else "⚠️  Exists"
    print(f"   {status}: {t['desc']}")

print()

# 3. Test SMS Send
print("3️⃣ TEST SMS SEND:")

try:
    user = User.objects.first()
    if not user:
        print("   ❌ No users found")
    else:
        service = NotificationService()
        result = service.notify(
            user=user,
            notification_type=NotificationType.OTP,
            metadata={"code": "1234"},
            send_sms=True
        )
        print(f"   ✅ Notification sent: {result.id}")
        print(f"      Type: {result.notification_type}")
        print(f"      Channel: {result.channel}")
        print(f"      Status: {result.status}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "="*70)
print("✅ TEST COMPLETE")
print("="*70 + "\n")
