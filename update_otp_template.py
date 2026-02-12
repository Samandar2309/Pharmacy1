#!/usr/bin/env python
"""
Update OTP SMS Template to match DevSMS approved format
Run: python manage.py shell < update_otp_template.py
"""

from notifications.models import NotificationTemplate, NotificationType, NotificationChannel

print("\n" + "="*60)
print("📝 UPDATING OTP SMS TEMPLATE")
print("="*60 + "\n")

# DevSMS approved template format
APPROVED_TEMPLATE = "Dorixona tizimi: ro'yxatdan o'tish uchun tasdiqlash kodingiz {code}"

# Update or create OTP SMS template
template, created = NotificationTemplate.objects.update_or_create(
    notification_type=NotificationType.OTP,
    channel=NotificationChannel.SMS,
    defaults={
        'template_text': APPROVED_TEMPLATE,
        'is_active': True,
    }
)

if created:
    print("✅ Template created")
else:
    print("✅ Template updated")

print(f"\nTemplate text:")
print(f"  {template.template_text}")
print(f"\nExample with code 1234:")
print(f"  {template.template_text.format(code='1234')}")

print("\n" + "="*60)
print("✅ UPDATE COMPLETE")
print("="*60)
print("\nNow restart backend:")
print("  python manage.py runserver")
print("\n")
