#!/usr/bin/env python
"""
Django Shell Script - OTP Test va Debugging
Run: python manage.py shell < debug_otp.py
"""

print("\n" + "="*60)
print("🔍 DORIXONA - OTP DEBUGGING SCRIPT")
print("="*60 + "\n")

from users.models import User, SMSVerification
from django.utils import timezone

# 1. Check if test user exists
print("📱 1. User Check:")
test_phone = "+998901234567"
try:
    user = User.objects.get(phone_number=test_phone)
    print(f"✅ User found!")
    print(f"   Phone: {user.phone_number}")
    print(f"   Name: {user.first_name} {user.last_name}")
    print(f"   Role: {user.role}")
    print(f"   Verified: {user.is_verified}")
    print(f"   Active: {user.is_active}")
    print(f"   Created: {user.created_at}\n")
except User.DoesNotExist:
    print(f"❌ User not found: {test_phone}\n")

# 2. Check SMS verifications
print("📬 2. SMS Verification History:")
sms_list = SMSVerification.objects.filter(phone_number=test_phone).order_by('-created_at')
if sms_list.exists():
    for idx, sms in enumerate(sms_list[:5], 1):  # Last 5
        status = "✅ VALID" if not sms.is_expired and not sms.is_used else "❌ EXPIRED/USED"
        print(f"   {idx}. Code: {sms.code} | {status}")
        print(f"      Created: {sms.created_at}")
        print(f"      Expires: {sms.expires_at}")
        print(f"      Attempts: {sms.attempts}")
        print(f"      Used: {sms.is_used}\n")
else:
    print("   ❌ No SMS records found\n")

# 3. Get latest valid OTP
print("🎯 3. Latest Valid OTP:")
latest_sms = (SMSVerification.objects
              .filter(phone_number=test_phone, is_expired=False)
              .order_by('-created_at')
              .first())

if latest_sms:
    print(f"✅ Found!")
    print(f"   Code: {latest_sms.code}")
    print(f"   Use this to verify registration\n")
else:
    print("❌ No valid OTP found")
    print("   Register user first\n")

# 4. Instructions
print("📋 4. How to Use:")
print("   1. Go to http://localhost:3000/register")
print("   2. Fill in the form:")
print(f"      Phone: {test_phone}")
print("      Password: password123")
print("      Name: Ali Valiyev")
print("   3. Click 'Ro'yxatdan o'tish'")
print("   4. Run this script to get OTP code")
print("   5. Enter code in the 4 input fields")
print("   6. Click 'Tasdiqlash'")
print("   7. ✅ Success! Home page!\n")

print("="*60)
print("✅ Debug Complete!")
print("="*60 + "\n")
