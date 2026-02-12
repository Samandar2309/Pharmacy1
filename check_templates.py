#!/usr/bin/env python
"""
Check templates and test SMS
Run: python manage.py shell < check_templates.py
"""

from notifications.models import NotificationTemplate
from django.conf import settings

print("\n" + "="*60)
print("🔍 TEMPLATE CHECK")
print("="*60 + "\n")

# 1. Check settings
print("1️⃣ SETTINGS:")
print(f"   SMS_DEBUG: {settings.SMS_DEBUG}")
print(f"   DEVSMS_TOKEN: {settings.DEVSMS_TOKEN[:20]}..." if settings.DEVSMS_TOKEN else "   NOT SET")
print()

# 2. Check templates
print("2️⃣ TEMPLATES IN DATABASE:")
templates = NotificationTemplate.objects.all()
print(f"   Total: {templates.count()}")

if templates.count() == 0:
    print("   ❌ NO TEMPLATES FOUND!")
    print("   Templates need to be created manually or via migration")
else:
    for t in templates:
        print(f"   ✅ {t.notification_type} - {t.channel}")
        print(f"      Text: {t.template_text[:50]}...")
        print()

# 3. Check OTP SMS template specifically
print("3️⃣ OTP SMS TEMPLATE:")
otp_sms = NotificationTemplate.objects.filter(
    notification_type='otp',
    channel='sms'
).first()

if otp_sms:
    print(f"   ✅ Found!")
    print(f"   Template: {otp_sms.template_text}")
    print(f"   Active: {otp_sms.is_active}")
else:
    print("   ❌ NOT FOUND! This is the problem!")
    print("   Creating now...")
    NotificationTemplate.objects.create(
        notification_type='otp',
        channel='sms',
        template_text='Sizning tasdiqlash kodingiz: {code}',
        is_active=True
    )
    print("   ✅ Created!")

print("\n" + "="*60)
print("✅ CHECK COMPLETE")
print("="*60 + "\n")
