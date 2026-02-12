#!/usr/bin/env python
"""
Django Shell Script - Test user yaratish
Run: python manage.py shell < create_test_user.py
"""

from users.models import User

# Delete existing test user if exists
User.objects.filter(phone_number="+998901234567").delete()

# Create test user
user = User.objects.create_user(
    phone_number="+998901234567",
    password="password123",
    first_name="Test",
    last_name="User",
    address="Tashkent, Chilonzor, 1-1-1"
)

# Verify
user.is_verified = True
user.is_active = True
user.save()

print(f"✅ Test user created!")
print(f"   Phone: +998901234567")
print(f"   Password: password123")
print(f"   Status: Verified & Active")
