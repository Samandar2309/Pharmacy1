from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny

from django.core.exceptions import ValidationError

from orders.models import Order
from .models import Payment, PaymentLog
from .serializers import (
    PaymentSerializer,
    PaymentCreateSerializer,
    PaymentLogSerializer,
    ClickPrepareSerializer,
    ClickCompleteSerializer,
    PaymeRequestSerializer,
)
from .services import (
    PaymentService,
    ClickService,
    PaymeService,
    PaymentValidationError,
)


# =========================================================
# CUSTOMER ENDPOINTS
# =========================================================

class PaymentCreateView(APIView):
    """
    To'lov yaratish (mijoz uchun).
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PaymentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order_id = serializer.validated_data["order_id"]
        provider = serializer.validated_data["provider"]

        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response(
                {"error": "Buyurtma topilmadi yoki sizga tegishli emas."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            payment = PaymentService.create_payment(
                order=order,
                provider=provider,
                amount=order.total_price,
            )
        except PaymentValidationError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            PaymentSerializer(payment).data,
            status=status.HTTP_201_CREATED,
        )


class PaymentListView(ListAPIView):
    """
    To'lovlar ro'yxati (mijoz uchun).
    """

    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user).order_by("-created_at")


class PaymentDetailView(RetrieveAPIView):
    """
    To'lov tafsiloti.
    """

    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "payment_id"

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)


class PaymentLogListView(ListAPIView):
    """
    To'lov loglari (admin uchun).
    """

    serializer_class = PaymentLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        payment_id = self.kwargs.get("payment_id")
        return PaymentLog.objects.filter(payment__payment_id=payment_id).order_by("-created_at")


# =========================================================
# CLICK WEBHOOK ENDPOINTS
# =========================================================

class ClickPrepareView(APIView):
    """
    Click PREPARE webhook.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ClickPrepareSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {
                    "error": -8,
                    "error_note": "Invalid request format",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        click_service = ClickService()
        response_data = click_service.handle_prepare(request_data=serializer.validated_data)

        return Response(response_data, status=status.HTTP_200_OK)


class ClickCompleteView(APIView):
    """
    Click COMPLETE webhook.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ClickCompleteSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {
                    "error": -8,
                    "error_note": "Invalid request format",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        click_service = ClickService()
        response_data = click_service.handle_complete(request_data=serializer.validated_data)

        return Response(response_data, status=status.HTTP_200_OK)


# =========================================================
# PAYME WEBHOOK ENDPOINT
# =========================================================

class PaymeWebhookView(APIView):
    """
    Payme JSON-RPC 2.0 webhook.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        # Verify authorization
        payme_service = PaymeService()
        authorization = request.headers.get("Authorization", "")

        if not payme_service.provider.verify_signature(authorization_header=authorization):
            return Response(
                payme_service.provider.error_response(
                    error_code=-32504,
                    error_message="Insufficient privilege",
                ),
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Parse JSON-RPC request
        serializer = PaymeRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                payme_service.provider.error_response(
                    error_code=-32600,
                    error_message="Invalid request",
                ),
                status=status.HTTP_400_BAD_REQUEST,
            )

        method = serializer.validated_data["method"]
        params = serializer.validated_data["params"]
        request_id = serializer.validated_data["id"]

        response_data = payme_service.handle_request(
            method=method,
            params=params,
            request_id=request_id,
        )

        return Response(response_data, status=status.HTTP_200_OK)
