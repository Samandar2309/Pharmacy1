from django.db import transaction
from django.contrib.auth import get_user_model
from django.shortcuts import render

from rest_framework import status, serializers
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.generics import GenericAPIView

from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema

from .services import OTPService
from .serializers import (
    ProfileSerializer,
    ProfileUpdateSerializer,
    RegisterSerializer,
    VerifyOTPSerializer,
    LoginSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
)

User = get_user_model()


# =====================================================
# COMMON HELPERS
# =====================================================

def success(message=None, data=None, status_code=status.HTTP_200_OK):
    return Response(
        {"message": message, "data": data},
        status=status_code
    )


def create_tokens(user):
    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh)
    }


# =====================================================
# PROFILE
# =====================================================

class ProfileView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer

    @extend_schema(responses=ProfileSerializer)
    def get(self, request):
        return success(data=self.get_serializer(request.user).data)

    @extend_schema(request=ProfileUpdateSerializer, responses=ProfileSerializer)
    def patch(self, request):
        serializer = ProfileUpdateSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return success("Profil yangilandi", ProfileSerializer(request.user).data)


# =====================================================
# REGISTER
# =====================================================

class RegisterView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    @extend_schema(request=RegisterSerializer)
    @transaction.atomic
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {
                    "message": "Validation error",
                    "errors": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = serializer.save()
            
            # Send OTP
            otp_service = OTPService()
            otp_service.send_otp(user.phone_number)

            return Response(
                {
                    "message": "SMS kod yuborildi",
                    "data": None
                },
                status=status.HTTP_201_CREATED
            )
        
        except Exception as e:
            logger.error(f"Register error: {e}")
            return Response(
                {
                    "message": "Registratsiya xatosi",
                    "error": str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )


# =====================================================
# VERIFY OTP
# =====================================================

def index(request):
    return render(request, "users/index.html")


class VerifyOTPView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = VerifyOTPSerializer

    @extend_schema(request=VerifyOTPSerializer)
    @transaction.atomic
    def post(self, request):

        serializer = self.get_serializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {
                    "message": "Validation failed",
                    "errors": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # SMS verification already done in serializer
        phone = serializer.validated_data["phone_number"]
        
        # Get user by phone
        try:
            user = User.objects.select_for_update().get(phone_number=phone)
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verify user
        user.verify()

        return success(
            "Tasdiqlandi",
            {
                **create_tokens(user),
                "user": ProfileSerializer(user).data
            }
        )


# =====================================================
# LOGIN
# =====================================================

class LoginView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    @extend_schema(request=LoginSerializer)
    def post(self, request):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]

        return success(
            data={
                **create_tokens(user),
                "user": ProfileSerializer(user).data
            }
        )


# =====================================================
# FORGOT PASSWORD
# =====================================================

class ForgotPasswordView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = ForgotPasswordSerializer

    @extend_schema(request=ForgotPasswordSerializer)
    def post(self, request):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data["phone_number"]

        if User.objects.filter(
            phone_number=phone,
            is_verified=True
        ).exists():
            OTPService().send_otp(phone)

        return success("Agar raqam mavjud bo‘lsa, SMS yuborildi")


# =====================================================
# RESET PASSWORD
# =====================================================

class ResetPasswordView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = ResetPasswordSerializer

    @extend_schema(request=ResetPasswordSerializer)
    @transaction.atomic
    def post(self, request):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data["phone_number"]
        new_password = serializer.validated_data["new_password"]

        user = User.objects.select_for_update().get(
            phone_number=phone
        )

        user.set_password(new_password)
        user.save(update_fields=["password"])

        return success("Parol yangilandi")


# =====================================================
# LOGOUT
# =====================================================

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class LogoutView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LogoutSerializer

    @extend_schema(request=LogoutSerializer)
    def post(self, request):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        RefreshToken(
            serializer.validated_data["refresh"]
        ).blacklist()

        return success("Chiqildi")