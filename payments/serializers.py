from rest_framework import serializers

from .models import Payment, PaymentLog


class PaymentSerializer(serializers.ModelSerializer):
    """
    Payment serializer for read operations.
    """

    order_id = serializers.IntegerField(source="order.id", read_only=True)
    user_phone = serializers.CharField(source="user.phone_number", read_only=True)
    provider_display = serializers.CharField(source="get_provider_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id",
            "payment_id",
            "order_id",
            "user_phone",
            "provider",
            "provider_display",
            "status",
            "status_display",
            "amount",
            "click_trans_id",
            "payme_transaction_id",
            "error_message",
            "created_at",
            "completed_at",
        ]
        read_only_fields = fields


class PaymentCreateSerializer(serializers.Serializer):
    """
    Payment yaratish uchun serializer.
    """

    order_id = serializers.IntegerField()
    provider = serializers.ChoiceField(choices=Payment.Provider.choices)

    def validate_provider(self, value):
        if value not in [Payment.Provider.CLICK, Payment.Provider.PAYME]:
            raise serializers.ValidationError("Faqat Click yoki Payme.")
        return value


class PaymentLogSerializer(serializers.ModelSerializer):
    """
    Payment log serializer.
    """

    class Meta:
        model = PaymentLog
        fields = [
            "id",
            "payment",
            "event_type",
            "request_data",
            "response_data",
            "error_message",
            "created_at",
        ]
        read_only_fields = fields


class ClickPrepareSerializer(serializers.Serializer):
    """
    Click PREPARE webhook request serializer.
    """
    click_trans_id = serializers.CharField()
    service_id = serializers.CharField()
    merchant_trans_id = serializers.CharField()
    amount = serializers.DecimalField(max_digits=16, decimal_places=2)
    action = serializers.IntegerField()
    error = serializers.IntegerField()
    error_note = serializers.CharField()
    sign_time = serializers.CharField()
    sign_string = serializers.CharField()


class ClickCompleteSerializer(serializers.Serializer):
    """
    Click COMPLETE webhook request serializer.
    """
    click_trans_id = serializers.CharField()
    service_id = serializers.CharField()
    merchant_trans_id = serializers.CharField()
    amount = serializers.DecimalField(max_digits=16, decimal_places=2)
    action = serializers.IntegerField()
    error = serializers.IntegerField()
    error_note = serializers.CharField()
    sign_time = serializers.CharField()
    sign_string = serializers.CharField()
    click_paydoc_id = serializers.CharField(required=False)


class PaymeRequestSerializer(serializers.Serializer):
    """
    Payme JSON-RPC request serializer.
    """
    method = serializers.CharField()
    params = serializers.JSONField()
    id = serializers.IntegerField()
