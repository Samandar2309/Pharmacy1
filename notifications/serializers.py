from rest_framework import serializers
from django.utils import timezone
from .models import (
    Notification,
    NotificationTemplate,
    NotificationStatus,
    NotificationChannel,
)


# =========================================================
# NOTIFICATION DETAIL SERIALIZER
# =========================================================

class NotificationDetailSerializer(serializers.ModelSerializer):

    notification_type_display = serializers.CharField(
        source="get_notification_type_display",
        read_only=True
    )

    status_display = serializers.CharField(
        source="get_status_display",
        read_only=True
    )

    channel_display = serializers.CharField(
        source="get_channel_display",
        read_only=True
    )

    class Meta:
        model = Notification
        fields = [
            "id",
            "notification_type",
            "notification_type_display",
            "channel",
            "channel_display",
            "message",
            "status",
            "status_display",
            "is_read",
            "read_at",
            "sent_at",
            "created_at",
            "metadata",
        ]
        read_only_fields = fields


# =========================================================
# NOTIFICATION LIST SERIALIZER (Badge Optimized)
# =========================================================

class NotificationListSerializer(serializers.ModelSerializer):

    notification_type_display = serializers.CharField(
        source="get_notification_type_display",
        read_only=True
    )

    class Meta:
        model = Notification
        fields = [
            "id",
            "notification_type",
            "notification_type_display",
            "status",
            "is_read",
            "created_at",
        ]
        read_only_fields = fields


# =========================================================
# MARK SINGLE NOTIFICATION AS READ
# =========================================================

class MarkAsReadSerializer(serializers.Serializer):

    def save(self, **kwargs):
        notification: Notification = self.context["notification"]

        if not notification.is_read:
            notification.is_read = True
            notification.read_at = timezone.now()
            notification.save(update_fields=["is_read", "read_at", "updated_at"])

        return notification


# =========================================================
# BULK MARK AS READ
# =========================================================

class BulkMarkAsReadSerializer(serializers.Serializer):

    notification_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )

    def save(self, **kwargs):
        user = self.context["request"].user
        ids = self.validated_data.get("notification_ids")

        queryset = Notification.objects.filter(
            user=user,
            is_read=False
        )

        if ids:
            queryset = queryset.filter(id__in=ids)

        updated = queryset.update(
            is_read=True,
            read_at=timezone.now()
        )

        return updated


# =========================================================
# ADMIN FILTER SERIALIZER
# =========================================================

class NotificationFilterSerializer(serializers.Serializer):

    status = serializers.ChoiceField(
        choices=NotificationStatus.choices,
        required=False
    )

    channel = serializers.ChoiceField(
        choices=NotificationChannel.choices,
        required=False
    )

    notification_type = serializers.ChoiceField(
        choices=Notification._meta.get_field("notification_type").choices,
        required=False
    )

    is_read = serializers.BooleanField(required=False)

    date_from = serializers.DateTimeField(required=False)
    date_to = serializers.DateTimeField(required=False)

    def validate(self, attrs):
        date_from = attrs.get("date_from")
        date_to = attrs.get("date_to")

        if date_from and date_to and date_from > date_to:
            raise serializers.ValidationError(
                "Boshlanish sanasi tugash sanasidan katta bo‘lishi mumkin emas."
            )

        return attrs


# =========================================================
# TEMPLATE SERIALIZER (ADMIN CRUD)
# =========================================================

class NotificationTemplateSerializer(serializers.ModelSerializer):

    notification_type_display = serializers.CharField(
        source="get_notification_type_display",
        read_only=True
    )

    channel_display = serializers.CharField(
        source="get_channel_display",
        read_only=True
    )

    class Meta:
        model = NotificationTemplate
        fields = [
            "id",
            "notification_type",
            "notification_type_display",
            "channel",
            "channel_display",
            "template_text",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def validate_template_text(self, value):
        if not value.strip():
            raise serializers.ValidationError(
                "Shablon matni bo‘sh bo‘lishi mumkin emas."
            )

        # Balanced placeholder check
        if value.count("{") != value.count("}"):
            raise serializers.ValidationError(
                "Template placeholderlar noto‘g‘ri yopilgan."
            )

        return value
