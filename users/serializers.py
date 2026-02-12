import re

from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework import serializers

from .models import SMSVerification

User = get_user_model()


# =====================================================
# 🔥 PHONE NORMALIZATION (SINGLE SOURCE OF TRUTH)
# =====================================================

def normalize_phone(phone: str) -> str:
    """
    Always returns E.164 format: +998XXXXXXXXX

    Accepts:
        947077178
        998947077178
        +998947077178
        +998 94 707 71 78
    """

    if not phone:
        raise serializers.ValidationError("Telefon raqam majburiy.")

    digits = re.sub(r"\D", "", phone.strip())

    # 9xxxxxxxx → 998xxxxxxxxx
    if len(digits) == 9:
        digits = "998" + digits

    if len(digits) == 12 and digits.startswith("998"):
        return f"+{digits}"

    raise serializers.ValidationError("Telefon raqam noto‘g‘ri formatda")


class PhoneNumberField(serializers.CharField):
    default_error_messages = {
        "invalid": "Telefon raqam noto‘g‘ri formatda"
    }

    def to_internal_value(self, value):
        try:
            return normalize_phone(value)
        except serializers.ValidationError:
            self.fail("invalid")


# =====================================================
# 🔥 OTP HELPER
# =====================================================

def get_valid_sms(phone: str, code: str) -> SMSVerification:
    sms = (
        SMSVerification.objects
        .filter(phone_number=phone, code=code, is_used=False)
        .order_by("-created_at")
        .first()
    )

    if not sms:
        raise serializers.ValidationError("Kod noto‘g‘ri.")

    if sms.is_expired:
        raise serializers.ValidationError("Kod muddati o‘tgan.")

    return sms


# =====================================================
# 🔥 PROFILE
# =====================================================

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "phone_number",
            "first_name",
            "last_name",
            "address",
            "role",
            "is_verified",
        )
        read_only_fields = fields


class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "address")

    def validate(self, attrs):
        if not attrs:
            raise serializers.ValidationError("Kamida bitta maydon yuboring.")
        return attrs


# =====================================================
# 🔥 REGISTER (MINIMAL + UX FRIENDLY)
# =====================================================

class RegisterSerializer(serializers.Serializer):
    phone_number = PhoneNumberField(help_text="+998901234567")
    first_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=50)
    password = serializers.CharField(write_only=True)

    def validate_password(self, value):
        validate_password(value)
        return value

    @transaction.atomic
    def create(self, validated_data):
        phone = validated_data["phone_number"]

        if User.objects.filter(phone_number=phone).exists():
            raise serializers.ValidationError({
                "phone_number": "Bu raqam allaqachon ro‘yxatdan o‘tgan."
            })

        return User.objects.create_user(
            phone_number=phone,
            password=validated_data["password"],
            first_name=validated_data["first_name"].strip(),
            last_name=validated_data["last_name"].strip(),
        )


# =====================================================
# 🔥 VERIFY OTP
# =====================================================

class VerifyOTPSerializer(serializers.Serializer):
    phone_number = PhoneNumberField()
    code = serializers.CharField(max_length=SMSVerification.CODE_LENGTH)

    @transaction.atomic
    def validate(self, attrs):
        # Normalize phone for SMS lookup (remove +)
        phone = attrs["phone_number"]
        phone_digits = "".join(filter(str.isdigit, phone))
        
        # Try both formats in database
        sms = (
            SMSVerification.objects
            .filter(code=attrs["code"], is_used=False)
            .filter(phone_number__in=[phone, phone_digits])
            .order_by("-created_at")
            .first()
        )

        if not sms:
            raise serializers.ValidationError({"code": "Kod noto'g'ri."})

        if sms.is_expired:
            raise serializers.ValidationError({"code": "Kod muddati o'tgan."})

        sms.is_used = True
        sms.save(update_fields=["is_used"])

        attrs["sms"] = sms
        attrs["phone_number"] = sms.phone_number  # Use actual phone from DB
        return attrs


# =====================================================
# 🔥 LOGIN
# =====================================================

class LoginSerializer(serializers.Serializer):
    phone_number = PhoneNumberField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        phone_number = attrs["phone_number"]
        password = attrs["password"]
        
        try:
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            raise serializers.ValidationError("Telefon yoki parol noto'g'ri.")

        # Check password
        if not user.check_password(password):
            raise serializers.ValidationError("Telefon yoki parol noto'g'ri.")

        if not user.is_verified:
            raise serializers.ValidationError("Telefon tasdiqlanmagan.")

        if not user.is_active:
            raise serializers.ValidationError("Foydalanuvchi bloklangan.")

        attrs["user"] = user
        return attrs


# =====================================================
# 🔥 FORGOT PASSWORD (NO USER ENUMERATION)
# =====================================================

class ForgotPasswordSerializer(serializers.Serializer):
    phone_number = PhoneNumberField()

    def validate_phone_number(self, value):
        # intentionally NOT revealing existence
        return value


# =====================================================
# 🔥 RESET PASSWORD
# =====================================================

class ResetPasswordSerializer(serializers.Serializer):
    phone_number = PhoneNumberField()
    code = serializers.CharField(max_length=SMSVerification.CODE_LENGTH)
    new_password = serializers.CharField(write_only=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value

    @transaction.atomic
    def validate(self, attrs):
        attrs["sms"] = get_valid_sms(
            attrs["phone_number"],
            attrs["code"]
        )
        return attrs


# =====================================================
# 🔥 SEND SMS (RATE LIMIT)
# =====================================================

class SendSMSSerializer(serializers.Serializer):
    phone_number = PhoneNumberField()

    def validate_phone_number(self, value):
        if not SMSVerification.can_send_sms(value):
            raise serializers.ValidationError(
                "1 daqiqa kuting va qayta urinib ko‘ring."
            )
        return value