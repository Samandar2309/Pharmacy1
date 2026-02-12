from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView, get_object_or_404

from delivery.models import Delivery
from delivery.serializers import (
    DeliveryListSerializer,
    DeliveryDetailSerializer,
    AssignCourierSerializer,
    DeliveryStatusUpdateSerializer,
    CancelDeliverySerializer,
)
from delivery.services import DeliveryService
from .permissions import (
    HasDeliveryRole,
    IsCourierOwnDelivery,
    CanCourierUpdateStatus,
)
from orders.models import Order


# =========================================================
# OPERATOR / ADMIN VIEWS
# =========================================================

class OperatorDeliveryListView(ListAPIView):
    """
    Operator / Admin:
    - Yetkazishga tayyor deliverylar ro‘yxati
    """

    permission_classes = [
        IsAuthenticated,
        HasDeliveryRole,
    ]
    serializer_class = DeliveryListSerializer

    def get_queryset(self):
        return Delivery.objects.filter(status=Delivery.Status.READY)


class AssignCourierView(APIView):
    """
    Operator / Admin:
    - Buyurtmani kuryerga biriktiradi
    """

    permission_classes = [
        IsAuthenticated,
        HasDeliveryRole,
    ]

    def post(self, request, order_id):
        serializer = AssignCourierSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order = get_object_or_404(Order, id=order_id)

        delivery = DeliveryService.assign_courier(
            order=order,
            courier_id=serializer.validated_data["courier_id"],
            changed_by=request.user
        )

        return Response(
            DeliveryDetailSerializer(delivery).data,
            status=status.HTTP_200_OK
        )


# =========================================================
# COURIER VIEWS
# =========================================================

class CourierDeliveryListView(ListAPIView):
    """
    Kuryer:
    - Faqat o‘ziga biriktirilgan deliverylar
    """

    permission_classes = [
        IsAuthenticated,
        HasDeliveryRole,
    ]
    serializer_class = DeliveryListSerializer

    def get_queryset(self):
        return Delivery.objects.filter(
            courier=self.request.user,
            is_active=True
        )


class CourierDeliveryDetailView(RetrieveAPIView):
    """
    Kuryer:
    - O‘z delivery tafsilotini ko‘radi
    """

    permission_classes = [
        IsAuthenticated,
        HasDeliveryRole,
        IsCourierOwnDelivery,
    ]
    serializer_class = DeliveryDetailSerializer
    lookup_url_kwarg = "delivery_id"

    def get_queryset(self):
        return Delivery.objects.filter(is_active=True)


class CourierUpdateStatusView(APIView):
    """
    Kuryer:
    - Delivery holatini yangilaydi (Yo‘lda / Yetkazildi)
    """

    permission_classes = [
        IsAuthenticated,
        HasDeliveryRole,
        CanCourierUpdateStatus,
        IsCourierOwnDelivery,
    ]

    def post(self, request, delivery_id):
        serializer = DeliveryStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        delivery = get_object_or_404(Delivery, id=delivery_id)

        new_status = serializer.validated_data["status"]

        if new_status == Delivery.Status.ON_THE_WAY:
            delivery = DeliveryService.mark_on_the_way(
                delivery=delivery,
                courier=request.user
            )
        elif new_status == Delivery.Status.DELIVERED:
            delivery = DeliveryService.mark_delivered(
                delivery=delivery,
                courier=request.user
            )

        return Response(
            DeliveryDetailSerializer(delivery).data,
            status=status.HTTP_200_OK
        )


# =========================================================
# ADMIN / OPERATOR CANCEL
# =========================================================

class CancelDeliveryView(APIView):
    """
    Admin / Operator:
    - Delivery’ni bekor qiladi
    """

    permission_classes = [
        IsAuthenticated,
        HasDeliveryRole,
    ]

    def post(self, request, delivery_id):
        serializer = CancelDeliverySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        delivery = get_object_or_404(Delivery, id=delivery_id)

        delivery = DeliveryService.cancel_delivery(
            delivery=delivery,
            changed_by=request.user,
            reason=serializer.validated_data.get("reason", "")
        )

        return Response(
            DeliveryDetailSerializer(delivery).data,
            status=status.HTTP_200_OK
        )
