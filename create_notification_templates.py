#!/usr/bin/env python
"""
Django Shell Script - Create Notification Templates
Run: python manage.py shell < create_notification_templates.py
"""

from notifications.models import NotificationTemplate, NotificationType, NotificationChannel

print("\n" + "="*60)
print("📝 NOTIFICATION TEMPLATES - CREATE")
print("="*60 + "\n")

# Template defaults
templates = [
    {
        "notification_type": NotificationType.OTP,
        "channel": NotificationChannel.SMS,
        "template_text": "Sizning tasdiqlash kodingiz: {code}. Bu kod 2 daqiqada amal qiladi.",
        "description": "OTP SMS template"
    },
    {
        "notification_type": NotificationType.OTP,
        "channel": NotificationChannel.SYSTEM,
        "template_text": "OTP: {code}",
        "description": "OTP System template"
    },
    {
        "notification_type": NotificationType.ORDER_CREATED,
        "channel": NotificationChannel.SYSTEM,
        "template_text": "Buyurtmangiz #{order_id} qabul qilindi. Jami: {total_price} so'm",
        "description": "Order created notification"
    },
    {
        "notification_type": NotificationType.ORDER_PAID,
        "channel": NotificationChannel.SYSTEM,
        "template_text": "Buyurtma #{order_id} uchun to'lov qabul qilindi. Tayyorlash boshlandi.",
        "description": "Order paid notification"
    },
]

created_count = 0

for template_data in templates:
    try:
        template, created = NotificationTemplate.objects.get_or_create(
            notification_type=template_data["notification_type"],
            channel=template_data["channel"],
            defaults={
                "template_text": template_data["template_text"],
                "is_active": True,
            }
        )
        
        if created:
            print(f"✅ Created: {template_data['description']}")
            created_count += 1
        else:
            print(f"⚠️  Already exists: {template_data['description']}")
    
    except Exception as e:
        print(f"❌ Error: {template_data['description']} - {e}")

print("\n" + "="*60)
print(f"✅ Total created: {created_count}")
print("="*60 + "\n")
