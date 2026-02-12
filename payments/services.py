"""
Payment Service Layer - Production Grade

Bu service Click va Payme provayderlarini boshqaradi.
Thread-safe, idempotent, va retry-safe.
"""

import hashlib
import hmac
import base64
import uuid
from decimal import Decimal
from typing import Optional, Dict, Any

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from orders.models import Order
from .models import Payment, PaymentLog


# =========================================================
# EXCEPTIONS
# =========================================================

class PaymentError(Exception):
    """Base payment exception."""
    pass


class PaymentValidationError(PaymentError):
    """Validation error."""
    pass


class PaymentProviderError(PaymentError):
    """Provider-side error."""
    pass


# =========================================================
# CLICK PROVIDER
# =========================================================

class ClickProvider:
    """
    Click payment provider integration.
    
    Docs: https://docs.click.uz/
    """

    PREPARE = 0
    COMPLETE = 1

    def __init__(self):
        self.service_id = settings.CLICK_SERVICE_ID
        self.merchant_id = settings.CLICK_MERCHANT_ID
        self.secret_key = settings.CLICK_SECRET_KEY

    def verify_signature(self, *, click_trans_id, service_id, secret_key, merchant_trans_id,
                          amount, action, sign_time, sign_string):
        """
        Click webhook imzosini tekshirish.
        """
        data = f"{click_trans_id}{service_id}{secret_key}{merchant_trans_id}{amount}{action}{sign_time}"
        expected_sign = hashlib.md5(data.encode()).hexdigest()

        return expected_sign == sign_string

    def prepare_response(self, *, click_trans_id, merchant_trans_id, error=0, error_note="Success"):
        """
        Click prepare javobini shakllantirish.
        """
        return {
            "click_trans_id": click_trans_id,
            "merchant_trans_id": merchant_trans_id,
            "merchant_prepare_id": merchant_trans_id,
            "error": error,
            "error_note": error_note,
        }

    def complete_response(self, *, click_trans_id, merchant_trans_id, error=0, error_note="Success"):
        """
        Click complete javobini shakllantirish.
        """
        return {
            "click_trans_id": click_trans_id,
            "merchant_trans_id": merchant_trans_id,
            "merchant_confirm_id": merchant_trans_id,
            "error": error,
            "error_note": error_note,
        }


# =========================================================
# PAYME PROVIDER
# =========================================================

class PaymeProvider:
    """
    Payme payment provider integration.
    
    Docs: https://developer.help.paycom.uz/
    """

    def __init__(self):
        self.merchant_id = settings.PAYME_MERCHANT_ID
        self.secret_key = settings.PAYME_SECRET_KEY

    def verify_signature(self, *, authorization_header):
        """
        Payme webhook authorization tekshirish.
        """
        if not authorization_header or not authorization_header.startswith("Basic "):
            return False

        try:
            base64_credentials = authorization_header.split(" ")[1]
            decoded = base64.b64decode(base64_credentials).decode("utf-8")
            username, password = decoded.split(":")

            return username == "Paycom" and password == self.secret_key
        except Exception:
            return False

    def error_response(self, *, error_code, error_message, request_id=None):
        """
        Payme error response formati.
        """
        return {
            "error": {
                "code": error_code,
                "message": error_message,
                "data": None,
            },
            "id": request_id,
        }

    def success_response(self, *, result, request_id=None):
        """
        Payme success response formati.
        """
        return {
            "result": result,
            "id": request_id,
        }


# =========================================================
# PAYMENT SERVICE (Universal Layer)
# =========================================================

class PaymentService:
    """
    Universal payment service.
    Provider-agnostic operations.
    """

    @staticmethod
    def generate_payment_id():
        """Generate unique payment ID."""
        return f"PAY-{uuid.uuid4().hex[:16].upper()}"

    @staticmethod
    @transaction.atomic
    def create_payment(*, order: Order, provider: str, amount: Decimal) -> Payment:
        """
        To'lov yaratish (idempotent).
        """
        if order.status != Order.Status.AWAITING_PAYMENT:
            raise PaymentValidationError(
                "Buyurtma awaiting_payment holatida bo'lishi kerak."
            )

        # Check if payment already exists for this order
        existing = Payment.objects.filter(
            order=order,
            provider=provider,
            status=Payment.Status.SUCCESS
        ).first()

        if existing:
            return existing

        payment = Payment.objects.create(
            order=order,
            user=order.user,
            payment_id=PaymentService.generate_payment_id(),
            provider=provider,
            amount=amount,
            status=Payment.Status.PENDING,
        )

        PaymentLog.objects.create(
            payment=payment,
            event_type="created",
            request_data={"amount": str(amount), "provider": provider},
        )

        return payment

    @staticmethod
    @transaction.atomic
    def complete_payment(*, payment: Payment, provider_data: dict = None):
        """
        To'lovni yakunlash va order statusini yangilash.
        """
        if payment.is_success:
            return  # idempotent

        payment.mark_success(provider_response=provider_data)

        # Update order status
        order = payment.order
        if order.status == Order.Status.AWAITING_PAYMENT:
            order.change_status(Order.Status.PAID, changed_by=None)

        PaymentLog.objects.create(
            payment=payment,
            event_type="completed",
            response_data=provider_data or {},
        )

    @staticmethod
    @transaction.atomic
    def fail_payment(*, payment: Payment, error_message: str, provider_data: dict = None):
        """
        To'lovni xato holatiga o'tkazish.
        """
        payment.mark_failed(error_message=error_message, provider_response=provider_data)

        PaymentLog.objects.create(
            payment=payment,
            event_type="failed",
            error_message=error_message,
            response_data=provider_data or {},
        )

    @staticmethod
    def get_payment_by_id(payment_id: str) -> Optional[Payment]:
        """
        Payment ID bo'yicha topish.
        """
        return Payment.objects.filter(payment_id=payment_id).first()


# =========================================================
# CLICK SERVICE (Business Logic)
# =========================================================

class ClickService:
    """
    Click-specific business logic.
    """

    def __init__(self):
        self.provider = ClickProvider()

    @transaction.atomic
    def handle_prepare(self, *, request_data: dict) -> dict:
        """
        Click PREPARE so'rovini qayta ishlash.
        """
        click_trans_id = request_data.get("click_trans_id")
        merchant_trans_id = request_data.get("merchant_trans_id")  # our payment_id
        amount = Decimal(request_data.get("amount", 0))
        action = request_data.get("action")
        sign_time = request_data.get("sign_time")
        sign_string = request_data.get("sign_string")

        # Verify signature
        if not self.provider.verify_signature(
            click_trans_id=click_trans_id,
            service_id=self.provider.service_id,
            secret_key=self.provider.secret_key,
            merchant_trans_id=merchant_trans_id,
            amount=str(amount),
            action=action,
            sign_time=sign_time,
            sign_string=sign_string,
        ):
            return self.provider.prepare_response(
                click_trans_id=click_trans_id,
                merchant_trans_id=merchant_trans_id,
                error=-1,
                error_note="Invalid signature",
            )

        # Find payment
        payment = PaymentService.get_payment_by_id(merchant_trans_id)

        if not payment:
            return self.provider.prepare_response(
                click_trans_id=click_trans_id,
                merchant_trans_id=merchant_trans_id,
                error=-5,
                error_note="Payment not found",
            )

        # Validate amount
        if payment.amount != amount:
            return self.provider.prepare_response(
                click_trans_id=click_trans_id,
                merchant_trans_id=merchant_trans_id,
                error=-2,
                error_note="Incorrect amount",
            )

        # Validate order status
        if payment.order.status != Order.Status.AWAITING_PAYMENT:
            return self.provider.prepare_response(
                click_trans_id=click_trans_id,
                merchant_trans_id=merchant_trans_id,
                error=-9,
                error_note="Order not ready for payment",
            )

        # Mark as processing
        payment.click_trans_id = click_trans_id
        payment.mark_processing()
        payment.save(update_fields=["click_trans_id"])

        PaymentLog.objects.create(
            payment=payment,
            event_type="click_prepare",
            request_data=request_data,
        )

        return self.provider.prepare_response(
            click_trans_id=click_trans_id,
            merchant_trans_id=merchant_trans_id,
            error=0,
            error_note="Success",
        )

    @transaction.atomic
    def handle_complete(self, *, request_data: dict) -> dict:
        """
        Click COMPLETE so'rovini qayta ishlash.
        """
        click_trans_id = request_data.get("click_trans_id")
        merchant_trans_id = request_data.get("merchant_trans_id")
        error = request_data.get("error")

        payment = PaymentService.get_payment_by_id(merchant_trans_id)

        if not payment:
            return self.provider.complete_response(
                click_trans_id=click_trans_id,
                merchant_trans_id=merchant_trans_id,
                error=-5,
                error_note="Payment not found",
            )

        if error == 0:
            # Success
            payment.click_paydoc_id = request_data.get("click_paydoc_id")
            payment.save(update_fields=["click_paydoc_id"])

            PaymentService.complete_payment(payment=payment, provider_data=request_data)

            return self.provider.complete_response(
                click_trans_id=click_trans_id,
                merchant_trans_id=merchant_trans_id,
                error=0,
                error_note="Success",
            )
        else:
            # Failed
            PaymentService.fail_payment(
                payment=payment,
                error_message=f"Click error: {error}",
                provider_data=request_data,
            )

            return self.provider.complete_response(
                click_trans_id=click_trans_id,
                merchant_trans_id=merchant_trans_id,
                error=error,
                error_note="Payment failed",
            )


# =========================================================
# PAYME SERVICE (Business Logic)
# =========================================================

class PaymeService:
    """
    Payme-specific business logic (JSON-RPC 2.0).
    """

    def __init__(self):
        self.provider = PaymeProvider()

    @transaction.atomic
    def handle_request(self, *, method: str, params: dict, request_id) -> dict:
        """
        Payme JSON-RPC so'rovlarini marshrutlash.
        """
        if method == "CheckPerformTransaction":
            return self.check_perform_transaction(params=params, request_id=request_id)

        elif method == "CreateTransaction":
            return self.create_transaction(params=params, request_id=request_id)

        elif method == "PerformTransaction":
            return self.perform_transaction(params=params, request_id=request_id)

        elif method == "CancelTransaction":
            return self.cancel_transaction(params=params, request_id=request_id)

        elif method == "CheckTransaction":
            return self.check_transaction(params=params, request_id=request_id)

        else:
            return self.provider.error_response(
                error_code=-32601,
                error_message="Method not found",
                request_id=request_id,
            )

    def check_perform_transaction(self, *, params: dict, request_id) -> dict:
        """
        CheckPerformTransaction: buyurtmani tekshirish.
        """
        account = params.get("account", {})
        order_id = account.get("order_id")
        amount = params.get("amount")  # tiyin

        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return self.provider.error_response(
                error_code=-31050,
                error_message="Order not found",
                request_id=request_id,
            )

        expected_amount = int(order.total_price * 100)  # convert to tiyin

        if amount != expected_amount:
            return self.provider.error_response(
                error_code=-31001,
                error_message="Incorrect amount",
                request_id=request_id,
            )

        if order.status != Order.Status.AWAITING_PAYMENT:
            return self.provider.error_response(
                error_code=-31008,
                error_message="Order not ready for payment",
                request_id=request_id,
            )

        return self.provider.success_response(
            result={"allow": True},
            request_id=request_id,
        )

    def create_transaction(self, *, params: dict, request_id) -> dict:
        """
        CreateTransaction: to'lovni yaratish yoki topish.
        """
        transaction_id = params.get("id")
        account = params.get("account", {})
        order_id = account.get("order_id")
        amount = params.get("amount")
        payme_time = params.get("time")

        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return self.provider.error_response(
                error_code=-31050,
                error_message="Order not found",
                request_id=request_id,
            )

        # Check if payment already exists
        existing = Payment.objects.filter(
            order=order,
            payme_transaction_id=transaction_id,
        ).first()

        if existing:
            return self.provider.success_response(
                result={
                    "transaction": existing.id,
                    "state": 1 if existing.is_success else 0,
                    "create_time": int(existing.created_at.timestamp() * 1000),
                },
                request_id=request_id,
            )

        # Create new payment
        payment = PaymentService.create_payment(
            order=order,
            provider=Payment.Provider.PAYME,
            amount=Decimal(amount) / 100,  # tiyin to sum
        )

        payment.payme_transaction_id = transaction_id
        payment.payme_time = payme_time
        payment.mark_processing()
        payment.save(update_fields=["payme_transaction_id", "payme_time"])

        PaymentLog.objects.create(
            payment=payment,
            event_type="payme_create",
            request_data=params,
        )

        return self.provider.success_response(
            result={
                "transaction": payment.id,
                "state": 1,
                "create_time": int(payment.created_at.timestamp() * 1000),
            },
            request_id=request_id,
        )

    def perform_transaction(self, *, params: dict, request_id) -> dict:
        """
        PerformTransaction: to'lovni yakunlash.
        """
        transaction_id = params.get("id")

        payment = Payment.objects.filter(payme_transaction_id=transaction_id).first()

        if not payment:
            return self.provider.error_response(
                error_code=-31003,
                error_message="Transaction not found",
                request_id=request_id,
            )

        PaymentService.complete_payment(payment=payment, provider_data=params)

        return self.provider.success_response(
            result={
                "transaction": payment.id,
                "state": 2,
                "perform_time": int(timezone.now().timestamp() * 1000),
            },
            request_id=request_id,
        )

    def cancel_transaction(self, *, params: dict, request_id) -> dict:
        """
        CancelTransaction: to'lovni bekor qilish.
        """
        transaction_id = params.get("id")

        payment = Payment.objects.filter(payme_transaction_id=transaction_id).first()

        if not payment:
            return self.provider.error_response(
                error_code=-31003,
                error_message="Transaction not found",
                request_id=request_id,
            )

        payment.mark_cancelled()

        PaymentLog.objects.create(
            payment=payment,
            event_type="payme_cancel",
            request_data=params,
        )

        return self.provider.success_response(
            result={
                "transaction": payment.id,
                "state": -1,
                "cancel_time": int(timezone.now().timestamp() * 1000),
            },
            request_id=request_id,
        )

    def check_transaction(self, *, params: dict, request_id) -> dict:
        """
        CheckTransaction: to'lov holatini tekshirish.
        """
        transaction_id = params.get("id")

        payment = Payment.objects.filter(payme_transaction_id=transaction_id).first()

        if not payment:
            return self.provider.error_response(
                error_code=-31003,
                error_message="Transaction not found",
                request_id=request_id,
            )

        state = 2 if payment.is_success else 1

        return self.provider.success_response(
            result={
                "transaction": payment.id,
                "state": state,
                "create_time": int(payment.created_at.timestamp() * 1000),
            },
            request_id=request_id,
        )
