from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db import transaction

from drf_spectacular.utils import extend_schema

from .models import Notification, NotificationTemplate, NotificationStatus
from .serializers import (
    NotificationDetailSerializer,
    NotificationListSerializer,
    NotificationTemplateSerializer,
)
from .permissions import CanManageTemplates


# =========================================================
# USER NOTIFICATIONS
# =========================================================

class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Foydalanuvchi o‘z notificationlarini ko‘rishi mumkin.
    """

    permission_classes = [IsAuthenticated]

    # -------------------------------------------
    # OPTIMIZED QUERY
    # -------------------------------------------

    def get_queryset(self):
        return (
            Notification.objects
            .filter(user=self.request.user)
            .select_related("user")
            .order_by("-created_at")
        )

    # -------------------------------------------
    # SERIALIZER SWITCH
    # -------------------------------------------

    def get_serializer_class(self):
        if self.action == "list":
            return NotificationListSerializer
        return NotificationDetailSerializer

    # -------------------------------------------
    # LIST
    # -------------------------------------------

    @extend_schema(summary="Mening bildirishnomalarim")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    # -------------------------------------------
    # RETRIEVE (AUTO MARK AS READ)
    # -------------------------------------------

    @extend_schema(summary="Bildirishnoma tafsiloti")
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        # 🔔 avtomatik read qilish
        if not instance.is_read:
            instance.is_read = True
            instance.read_at = timezone.now()
            instance.save(update_fields=["is_read", "read_at", "updated_at"])

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    # =====================================================
    # 🔔 UNREAD COUNT (Badge uchun)
    # =====================================================

    @action(detail=False, methods=["get"], url_path="unread-count")
    def unread_count(self, request):
        count = self.get_queryset().filter(is_read=False).count()

        return Response(
            {"unread_count": count},
            status=status.HTTP_200_OK
        )

    # =====================================================
    # MARK SINGLE AS READ
    # =====================================================

    @action(detail=True, methods=["post"], url_path="mark-as-read")
    def mark_as_read(self, request, pk=None):
        notification = self.get_object()

        if not notification.is_read:
            notification.is_read = True
            notification.read_at = timezone.now()
            notification.save(update_fields=["is_read", "read_at", "updated_at"])

        return Response(
            {"message": "Notification o‘qildi"},
            status=status.HTTP_200_OK
        )

    # =====================================================
    # MARK ALL AS READ
    # =====================================================

    @action(detail=False, methods=["post"], url_path="mark-all-read")
    def mark_all_read(self, request):
        updated = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).update(
            is_read=True,
            read_at=timezone.now()
        )

        return Response(
            {
                "message": "Barcha notificationlar o‘qildi",
                "updated_count": updated
            },
            status=status.HTTP_200_OK
        )

    # =====================================================
    # FAILED COUNT (Monitoring)
    # =====================================================

    @action(detail=False, methods=["get"], url_path="failed-count")
    def failed_count(self, request):
        count = self.get_queryset().filter(
            status=NotificationStatus.FAILED
        ).count()

        return Response(
            {"failed_count": count},
            status=status.HTTP_200_OK
        )

    # =====================================================
    # RETRY FAILED
    # =====================================================

    @action(detail=True, methods=["post"], url_path="retry")
    def retry(self, request, pk=None):

        notification = self.get_object()

        if notification.status != NotificationStatus.FAILED:
            return Response(
                {"error": "Faqat FAILED notificationni qayta yuborish mumkin"},
                status=status.HTTP_400_BAD_REQUEST
            )

        from .services import NotificationService

        service = NotificationService()
        service.send(notification)

        return Response(
            {"message": "Qayta yuborish jarayoni boshlandi"},
            status=status.HTTP_200_OK
        )


# =========================================================
# TEMPLATE MANAGEMENT (ADMIN ONLY)
# =========================================================

class NotificationTemplateViewSet(viewsets.ModelViewSet):

    queryset = NotificationTemplate.objects.all().order_by("notification_type")
    serializer_class = NotificationTemplateSerializer
    permission_classes = [IsAuthenticated, CanManageTemplates]
